#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "cupdlp" / "hip" / "cupdlp_hip_linalg.cpp"

HELPER = r'''
static hipsparseSpMVAlg_t cupdlp_hip_spmv_alg(void) {
  const char *env = std::getenv("CUPDLP_HIP_SPMV_ALG");

  if (env == nullptr || env[0] == '\0' ||
      std::strcmp(env, "csr_alg2") == 0 ||
      std::strcmp(env, "CSR_ALG2") == 0 ||
      std::strcmp(env, "alg2") == 0 ||
      std::strcmp(env, "ALG2") == 0) {
    return HIPSPARSE_SPMV_CSR_ALG2;
  }

  if (std::strcmp(env, "default") == 0 ||
      std::strcmp(env, "DEFAULT") == 0) {
    return HIPSPARSE_SPMV_ALG_DEFAULT;
  }

  if (std::strcmp(env, "csr_alg1") == 0 ||
      std::strcmp(env, "CSR_ALG1") == 0 ||
      std::strcmp(env, "alg1") == 0 ||
      std::strcmp(env, "ALG1") == 0) {
    return HIPSPARSE_SPMV_CSR_ALG1;
  }

  static bool warned = false;
  if (!warned) {
    warned = true;
    fprintf(stderr,
            "[cuPDLP][HIP] unknown CUPDLP_HIP_SPMV_ALG=%s; "
            "falling back to HIPSPARSE_SPMV_CSR_ALG2\n",
            env);
  }

  return HIPSPARSE_SPMV_CSR_ALG2;
}
'''.strip()

def insert_include(text: str, include: str) -> str:
    if include in text:
        return text
    lines = text.splitlines()
    last_include = -1
    for idx, line in enumerate(lines):
        if line.startswith("#include "):
            last_include = idx
    if last_include < 0:
        raise RuntimeError("No #include block found")
    lines.insert(last_include + 1, include)
    return "\n".join(lines) + "\n"

def insert_helper(text: str) -> str:
    if "cupdlp_hip_spmv_alg" in text:
        return text

    marker = "cupdlp_int cuda_alloc_MVbuffer"
    pos = text.find(marker)
    if pos < 0:
        raise RuntimeError(f"Could not find marker: {marker}")

    return text[:pos] + HELPER + "\n\n" + text[pos:]

def replace_alg(text: str) -> str:
    old = "HIPSPARSE_SPMV_CSR_ALG2"
    new = "cupdlp_hip_spmv_alg()"

    replacements = 0
    out_lines = []

    for line in text.splitlines():
        if old in line and "hipsparseSpMVAlg_t alg =" not in line and "return HIPSPARSE_SPMV_CSR_ALG2" not in line:
            line = line.replace(old, new)
            replacements += 1
        out_lines.append(line)

    if replacements < 4:
        raise RuntimeError(f"Expected at least 4 SpMV call replacements, got {replacements}")

    return "\n".join(out_lines) + "\n"

def patch():
    text = SRC.read_text(encoding="utf-8")

    text = insert_include(text, "#include <cstdlib>")
    text = insert_include(text, "#include <cstring>")
    text = insert_include(text, "#include <cstdio>")
    text = insert_helper(text)
    text = replace_alg(text)

    SRC.write_text(text, encoding="utf-8", newline="\n")
    print(f"[OK] patched {SRC.relative_to(ROOT)}")

def main():
    patch()
    print("[DONE] added opt-in HIP SpMV algorithm switch")
    print("Default behavior remains HIPSPARSE_SPMV_CSR_ALG2.")
    print("Use CUPDLP_HIP_SPMV_ALG=default or csr_alg1 for experiments.")

if __name__ == "__main__":
    main()
