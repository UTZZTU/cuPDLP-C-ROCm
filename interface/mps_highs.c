#include "mps_lp.h"
#include "wrapper_highs.h"
#include "../cupdlp/cupdlp_backend_compat.h"
#include <stdio.h>
#include <stdlib.h>

static cupdlp_bool phase_timing_enabled(void) {
  const char *value = getenv("CUPDLP_PHASE_TIMING");
  return value != NULL && atoi(value) != 0;
}

static void print_phase_timing(const char *name, cupdlp_float seconds) {
  printf("PHASE_TIMING\t%s\t%.6f\n", name, (double)seconds);
}

static cupdlp_bool research_stats_enabled(void) {
  const char *value = getenv("CUPDLP_RESEARCH_STATS");
  return value != NULL && atoi(value) != 0;
}

static int compare_cupdlp_int(const void *lhs, const void *rhs) {
  const cupdlp_int a = *(const cupdlp_int *)lhs;
  const cupdlp_int b = *(const cupdlp_int *)rhs;
  return (a > b) - (a < b);
}

static void print_nnz_distribution(const char *name,
                                   const cupdlp_int *values,
                                   cupdlp_int count) {
  if (count <= 0) return;
  cupdlp_int *sorted =
      (cupdlp_int *)malloc((size_t)count * sizeof(cupdlp_int));
  if (sorted == NULL) return;
  memcpy(sorted, values, (size_t)count * sizeof(cupdlp_int));
  qsort(sorted, (size_t)count, sizeof(cupdlp_int), compare_cupdlp_int);
  cupdlp_int p95_index = (95 * count + 99) / 100 - 1;
  if (p95_index < 0) p95_index = 0;
  long long sum = 0;
  for (cupdlp_int i = 0; i < count; ++i) sum += sorted[i];
  printf("RESEARCH_MATRIX\t%s\tcount=%d\tmin=%d\tmean=%.6f\tp95=%d\tmax=%d\n",
         name, count, sorted[0], (double)sum / (double)count,
         sorted[p95_index], sorted[count - 1]);
  free(sorted);
}

static void print_matrix_statistics(cupdlp_int nRows, cupdlp_int nCols,
                                    cupdlp_int nnz, const int *csc_beg,
                                    const int *csc_idx) {
  cupdlp_int *row_nnz =
      (cupdlp_int *)calloc((size_t)nRows, sizeof(cupdlp_int));
  cupdlp_int *col_nnz =
      (cupdlp_int *)malloc((size_t)nCols * sizeof(cupdlp_int));
  if (row_nnz == NULL || col_nnz == NULL) {
    free(row_nnz);
    free(col_nnz);
    return;
  }
  for (cupdlp_int col = 0; col < nCols; ++col) {
    col_nnz[col] = csc_beg[col + 1] - csc_beg[col];
    for (int pos = csc_beg[col]; pos < csc_beg[col + 1]; ++pos) {
      if (csc_idx[pos] >= 0 && csc_idx[pos] < nRows) ++row_nnz[csc_idx[pos]];
    }
  }
  printf("RESEARCH_MATRIX\tshape\trows=%d\tcols=%d\tnnz=%d\n", nRows, nCols,
         nnz);
  print_nnz_distribution("row_nnz", row_nnz, nRows);
  print_nnz_distribution("column_nnz", col_nnz, nCols);
  free(row_nnz);
  free(col_nnz);
}

/*
  HiGHS IO for cuPDLP.

  For cuPDLP, the problem is formulated as
      min  cT x
      s.t.   Aeq x = beq
           Aineq x >= bineq
           lb <= x <= ub
*/
cupdlp_retcode main(int argc, char **argv) {
  cupdlp_retcode retcode = RETCODE_OK;

  const cupdlp_bool ifPhaseTiming = phase_timing_enabled();
  const cupdlp_float phase_total_start = getTimeStamp();
  cupdlp_float phase_mps_load_model = 0.0;
  cupdlp_float phase_presolve = 0.0;
  cupdlp_float phase_formulate = 0.0;
  cupdlp_float phase_init_scaling = 0.0;
  cupdlp_float phase_gpu_setup = 0.0;
  cupdlp_float phase_csc_host_build = 0.0;
  cupdlp_float phase_scaling = 0.0;
  cupdlp_float phase_problem_alloc = 0.0;
  cupdlp_float phase_solver_setup = 0.0;
  cupdlp_float phase_solver_and_json = 0.0;
  cupdlp_float phase_output = 0.0;
  cupdlp_float phase_cleanup_start = 0.0;

  char *fname = "./example/afiro.mps";
  char *fout = "./solution-sum.json";
  char *fout_sol = "./solution.json";

  cupdlp_bool ifSaveSol = false;
  cupdlp_bool ifPresolve = false;

  // for cuPDLP
  int nCols_pdlp = 0;
  int nRows_pdlp = 0;
  int nEqs_pdlp = 0;
  int nnz_pdlp = 0;
  int status_pdlp = -1;

  cupdlp_float *rhs = NULL;
  cupdlp_float *cost = NULL;
  cupdlp_float *lower = NULL;
  cupdlp_float *upper = NULL;

  // -------------------------
  int *csc_beg = NULL, *csc_idx = NULL;
  double *csc_val = NULL;

  // for model to solve, need to free
  double offset =
      0.0;  // true objVal = sig * c'x + offset, sig = 1 (min) or -1 (max)
  double sense = 1;  // 1 (min) or -1 (max)
  int *constraint_new_idx = NULL;
  int *constraint_type = NULL;

  // for model to solve, need not to free
  int nCols = 0;
  cupdlp_float *col_value = cupdlp_NULL;
  cupdlp_float *col_dual = cupdlp_NULL;
  cupdlp_float *row_value = cupdlp_NULL;
  cupdlp_float *row_dual = cupdlp_NULL;

  // for original model, need to free
  int nCols_org = 0;
  int nRows_org = 0;
  cupdlp_float *col_value_org = cupdlp_NULL;
  cupdlp_float *col_dual_org = cupdlp_NULL;
  cupdlp_float *row_value_org = cupdlp_NULL;
  cupdlp_float *row_dual_org = cupdlp_NULL;

  // for presolved model, need to free
  int nCols_pre = 0;
  int nRows_pre = 0;
  cupdlp_float *col_value_pre = cupdlp_NULL;
  cupdlp_float *col_dual_pre = cupdlp_NULL;
  cupdlp_float *row_value_pre = cupdlp_NULL;
  cupdlp_float *row_dual_pre = cupdlp_NULL;
  cupdlp_int value_valid = 0;
  cupdlp_int dual_valid = 0;

  void *model = NULL;
  void *presolvedmodel = NULL;
  int presolve_status = -1;
  void *model2solve = NULL;

  CUPDLPscaling *scaling =
      (CUPDLPscaling *)cupdlp_malloc(sizeof(CUPDLPscaling));

  // claim solvers variables
  // prepare pointers
  CUPDLP_MATRIX_FORMAT src_matrix_format = CSC;
  CUPDLP_MATRIX_FORMAT dst_matrix_format = CSR_CSC;
  CUPDLPcsc *csc_cpu = cupdlp_NULL;
  CUPDLPproblem *prob = cupdlp_NULL;

  // load parameters
  for (cupdlp_int i = 0; i < argc - 1; i++) {
    if (strcmp(argv[i], "-fname") == 0) {
      fname = argv[i + 1];
    } else if (strcmp(argv[i], "-out") == 0) {
      fout = argv[i + 1];
    } else if (strcmp(argv[i], "-h") == 0) {
      print_script_usage();
      break;
    } else if (strcmp(argv[i], "-savesol") == 0) {
      ifSaveSol = atoi(argv[i + 1]);
    } else if (strcmp(argv[i], "-ifPre") == 0) {
      ifPresolve = atoi(argv[i + 1]);
    } else if (strcmp(argv[i], "-outSol") == 0) {
      fout_sol = argv[i + 1];
    }
  }
  if (strcmp(argv[argc - 1], "-h") == 0) {
    print_script_usage();
  }

  // set solver parameters
  cupdlp_bool ifChangeIntParam[N_INT_USER_PARAM] = {false};
  cupdlp_int intParam[N_INT_USER_PARAM] = {0};
  cupdlp_bool ifChangeFloatParam[N_FLOAT_USER_PARAM] = {false};
  cupdlp_float floatParam[N_FLOAT_USER_PARAM] = {0.0};
  CUPDLP_CALL(getUserParam(argc, argv, ifChangeIntParam, intParam,
                           ifChangeFloatParam, floatParam));

  cupdlp_float phase_start = getTimeStamp();
  model = createModel_highs();
  CUPDLP_CALL(loadMps_highs(model, fname));
  phase_mps_load_model = getTimeStamp() - phase_start;
  getModelSize_highs(model, &nCols_org, &nRows_org, NULL);
  nCols = nCols_org;

  model2solve = model;

  if (ifChangeIntParam[IF_PRESOLVE]) {
    ifPresolve = intParam[IF_PRESOLVE];
  }

  cupdlp_float presolve_time = getTimeStamp();
  if (ifPresolve) {
    presolvedmodel = createModel_highs();
    presolve_status = presolvedModel_highs(presolvedmodel, model);
    getModelSize_highs(presolvedmodel, &nCols_pre, &nRows_pre, NULL);
    // ok 0, timeout 1, infeasOrUnbounded 2, opt 3
    if (presolve_status == 2) {
      cupdlp_printf(
          "Infeasible or Unbounded LP detected by HiGHS presolver.\n");
      writeJsonFromHiGHS_highs(fout, model);
      if (ifSaveSol) {
        printf("--- no sol file saved.\n");
      }
      goto exit_cleanup;
    } else if (presolve_status == 3) {
      cupdlp_printf("Solved by HiGHS presolver.\n");
      // postsolve from a trivial solution
      postsolveModelFromEmpty_highs(model);
      writeJsonFromHiGHS_highs(fout, model);
      if (ifSaveSol) {
        // write out solution
        writeSolFromHiGHS_highs(fout_sol, model);
      }
      goto exit_cleanup;
    }
    model2solve = presolvedmodel;
    nCols = nCols_pre;
  }
  presolve_time = getTimeStamp() - presolve_time;
  phase_presolve = presolve_time;

  phase_start = getTimeStamp();
  CUPDLP_CALL(formulateLP_highs(model2solve, &cost, &nCols_pdlp, &nRows_pdlp,
                                &nnz_pdlp, &nEqs_pdlp, &csc_beg, &csc_idx,
                                &csc_val, &rhs, &lower, &upper, &offset, &sense,
                                &nCols, &constraint_new_idx, &constraint_type));
  phase_formulate = getTimeStamp() - phase_start;

  phase_start = getTimeStamp();
  CUPDLP_CALL(Init_Scaling(scaling, nCols_pdlp, nRows_pdlp, cost, rhs));
  phase_init_scaling = getTimeStamp() - phase_start;
  cupdlp_int ifScaling = 1;

  if (ifChangeIntParam[IF_SCALING]) {
    ifScaling = intParam[IF_SCALING];
  }

  if (ifChangeIntParam[IF_RUIZ_SCALING]) {
    scaling->ifRuizScaling = intParam[IF_RUIZ_SCALING];
  }

  if (ifChangeIntParam[IF_L2_SCALING]) {
    scaling->ifL2Scaling = intParam[IF_L2_SCALING];
  }

  if (ifChangeIntParam[IF_PC_SCALING]) {
    scaling->ifPcScaling = intParam[IF_PC_SCALING];
  }

  // the work object needs to be established first
  // free inside cuPDLP
  CUPDLPwork *w = cupdlp_NULL;
  CUPDLP_INIT_ZERO(w, 1);
#if !(CUPDLP_CPU)
  cupdlp_float cuda_prepare_time = getTimeStamp();
  CHECK_CUSPARSE(CUPDLP_SPARSE_CREATE(&w->cusparsehandle));
  CHECK_CUBLAS(CUPDLP_BLAS_CREATE(&w->cublashandle));
  cuda_prepare_time = getTimeStamp() - cuda_prepare_time;
  phase_gpu_setup = cuda_prepare_time;
#endif

  phase_start = getTimeStamp();
  CUPDLP_CALL(problem_create(&prob));

  // currently, only supprot that input matrix is CSC, and store both CSC and
  // CSR
  CUPDLP_CALL(csc_create(&csc_cpu));
  csc_cpu->nRows = nRows_pdlp;
  csc_cpu->nCols = nCols_pdlp;
  csc_cpu->nMatElem = nnz_pdlp;
  CUPDLP_INIT(csc_cpu->colMatBeg, 1 + nCols_pdlp)
  CUPDLP_INIT(csc_cpu->colMatIdx, nnz_pdlp)
  CUPDLP_INIT(csc_cpu->colMatElem, nnz_pdlp)
  memcpy(csc_cpu->colMatBeg, csc_beg, ((size_t)nCols_pdlp + 1) * sizeof(int));
  memcpy(csc_cpu->colMatIdx, csc_idx, nnz_pdlp * sizeof(int));
  memcpy(csc_cpu->colMatElem, csc_val, nnz_pdlp * sizeof(double));
#if !(CUPDLP_CPU)
  csc_cpu->cuda_csc = NULL;
#endif
  phase_csc_host_build = getTimeStamp() - phase_start;
  if (research_stats_enabled()) {
    print_matrix_statistics(nRows_pdlp, nCols_pdlp, nnz_pdlp, csc_beg, csc_idx);
  }

  cupdlp_float scaling_time = getTimeStamp();
  CUPDLP_CALL(PDHG_Scale_Data(csc_cpu, ifScaling, scaling, cost, lower, upper, rhs));
  scaling_time = getTimeStamp() - scaling_time;
  phase_scaling = scaling_time;

  cupdlp_float alloc_matrix_time = 0.0;
  cupdlp_float copy_vec_time = 0.0;

  phase_start = getTimeStamp();
  CUPDLP_CALL(problem_alloc(prob, nRows_pdlp, nCols_pdlp, nEqs_pdlp, cost,
                            offset, sense, csc_cpu, src_matrix_format,
                            dst_matrix_format, rhs, lower, upper,
                            &alloc_matrix_time, &copy_vec_time));
  phase_problem_alloc = getTimeStamp() - phase_start;

  // solve
  w->problem = prob;
  w->scaling = scaling;
  phase_start = getTimeStamp();
  PDHG_Alloc(w);
  w->timers->dScalingTime = scaling_time;
  w->timers->dPresolveTime = presolve_time;
  CUPDLP_COPY_VEC(w->rowScale, scaling->rowScale, cupdlp_float, nRows_pdlp);
  CUPDLP_COPY_VEC(w->colScale, scaling->colScale, cupdlp_float, nCols_pdlp);
  phase_solver_setup = getTimeStamp() - phase_start;

#if !(CUPDLP_CPU)
  w->timers->AllocMem_CopyMatToDeviceTime += alloc_matrix_time;
  w->timers->CopyVecToDeviceTime += copy_vec_time;
  w->timers->HIPPrepareTime = cuda_prepare_time;
#endif

  cupdlp_printf("--------------------------------------------------\n");
  cupdlp_printf("enter main solve loop\n");
  cupdlp_printf("--------------------------------------------------\n");

  CUPDLP_INIT_ZERO(col_value_org, nCols_org);
  CUPDLP_INIT_ZERO(col_dual_org, nCols_org);
  CUPDLP_INIT_ZERO(row_value_org, nRows_org);
  CUPDLP_INIT_ZERO(row_dual_org, nRows_org);

  if (ifPresolve) {
    CUPDLP_INIT_ZERO(col_value_pre, nCols_pre);
    CUPDLP_INIT_ZERO(col_dual_pre, nCols_pre);
    CUPDLP_INIT_ZERO(row_value_pre, nRows_pre);
    CUPDLP_INIT_ZERO(row_dual_pre, nRows_pre);

    col_value = col_value_pre;
    col_dual = col_dual_pre;
    row_value = row_value_pre;
    row_dual = row_dual_pre;
  } else {
    col_value = col_value_org;
    col_dual = col_dual_org;
    row_value = row_value_org;
    row_dual = row_dual_org;
  }

  phase_start = getTimeStamp();
  CUPDLP_CALL(LP_SolvePDHG(w, ifChangeIntParam, intParam, ifChangeFloatParam,
                           floatParam, fout, nCols, col_value, col_dual,
                           row_value, row_dual, &value_valid, &dual_valid, 0,
                           fout_sol, constraint_new_idx, constraint_type,
                           &status_pdlp));
  phase_solver_and_json = getTimeStamp() - phase_start;

  // // postsolve
  // if (ifPresolve) {
  //   postsolvedModel_highs(
  //       model, nCols_pre, nRows_pre, col_value_pre, col_dual_pre,
  //       row_value_pre, row_dual_pre, value_valid, dual_valid, nCols_org,
  //       nRows_org, col_value_org, col_dual_org, row_value_org, row_dual_org);
  // }

  // // write solution
  // if (ifSaveSol) {
  //   writeSol(fout_sol, nCols_org, nRows_org, col_value_org, col_dual_org,
  //            row_value_org, row_dual_org);
  // }

  if (ifSaveSol) {
    // infeasible or unbounded
    if (status_pdlp == 1 || status_pdlp == 2 || status_pdlp == 3) {
      printf("--- no sol file saved.\n");
      goto exit_cleanup;
    }

    if (ifPresolve) {
      // currently no postsolve
      phase_start = getTimeStamp();
      writeSol(fout_sol, nCols_pre, nRows_pre, col_value_pre, col_dual_pre,
               row_value_pre, row_dual_pre);
    } else {
      phase_start = getTimeStamp();
      writeSol(fout_sol, nCols_org, nRows_org, col_value_org, col_dual_org,
               row_value_org, row_dual_org);
    }
    phase_output = getTimeStamp() - phase_start;
  }

exit_cleanup:
  phase_cleanup_start = getTimeStamp();
  // free model and solution
  deleteModel_highs(model);
  if (ifPresolve) {
    deleteModel_highs(presolvedmodel);
    if (col_value_pre != NULL) cupdlp_free(col_value_pre);
    if (col_dual_pre != NULL) cupdlp_free(col_dual_pre);
    if (row_value_pre != NULL) cupdlp_free(row_value_pre);
    if (row_dual_pre != NULL) cupdlp_free(row_dual_pre);
  }
  if (col_value_org != NULL) cupdlp_free(col_value_org);
  if (col_dual_org != NULL) cupdlp_free(col_dual_org);
  if (row_value_org != NULL) cupdlp_free(row_value_org);
  if (row_dual_org != NULL) cupdlp_free(row_dual_org);
  col_value = NULL;
  col_dual = NULL;
  row_value = NULL;
  row_dual = NULL;

  // free problem
  if (scaling) {
    scaling_clear(scaling);
  }

  if (cost != NULL) cupdlp_free(cost);
  if (csc_beg != NULL) cupdlp_free(csc_beg);
  if (csc_idx != NULL) cupdlp_free(csc_idx);
  if (csc_val != NULL) cupdlp_free(csc_val);
  if (rhs != NULL) cupdlp_free(rhs);
  if (lower != NULL) cupdlp_free(lower);
  if (upper != NULL) cupdlp_free(upper);
  if (constraint_new_idx != NULL) cupdlp_free(constraint_new_idx);
  if (constraint_type != NULL) cupdlp_free(constraint_type);

  // free memory
  csc_clear_host(csc_cpu);
  problem_clear(prob);
  #if !(CUPDLP_CPU)
    CHECK_CUDA(CUPDLP_DEVICE_RESET())
  #endif

  if (ifPhaseTiming) {
    print_phase_timing("mps_load_model", phase_mps_load_model);
    print_phase_timing("presolve", phase_presolve);
    print_phase_timing("formulate_lp", phase_formulate);
    print_phase_timing("init_scaling", phase_init_scaling);
    print_phase_timing("gpu_setup", phase_gpu_setup);
    print_phase_timing("csc_host_build", phase_csc_host_build);
    print_phase_timing("scaling", phase_scaling);
    print_phase_timing("problem_alloc", phase_problem_alloc);
    print_phase_timing("solver_setup", phase_solver_setup);
    print_phase_timing("solver_and_json", phase_solver_and_json);
    print_phase_timing("output", phase_output);
    print_phase_timing("cleanup", getTimeStamp() - phase_cleanup_start);
    print_phase_timing("total_process", getTimeStamp() - phase_total_start);
  }

  return retcode;
}
