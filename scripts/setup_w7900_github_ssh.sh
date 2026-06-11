#!/usr/bin/env bash
set -Eeuo pipefail

WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
REPO_DIR="${REPO_DIR:-${WORK_ROOT}/src/cuPDLP-C-ROCm}"
GIT_USER_EMAIL="${GIT_USER_EMAIL:-1599441272@qq.com}"
REPO_SSH_URL="${REPO_SSH_URL:-git@github.com:UTZZTU/cuPDLP-C-ROCm.git}"

SSH_DIR="${WORK_ROOT}/.ssh"
KEY="${SSH_DIR}/github_w7900_ephemeral"

mkdir -p "${SSH_DIR}"
chmod 700 "${SSH_DIR}"

if [[ ! -f "${KEY}" ]]; then
  ssh-keygen -t ed25519 -C "${GIT_USER_EMAIL}" -f "${KEY}" -N ""
fi

chmod 600 "${KEY}"
chmod 644 "${KEY}.pub"

echo
echo "Add this public key to GitHub:"
echo "GitHub -> Settings -> SSH and GPG keys -> New SSH key"
echo
echo "----- PUBLIC KEY BEGIN -----"
cat "${KEY}.pub"
echo "----- PUBLIC KEY END -----"
echo
read -r -p "After adding the key to GitHub, press Enter to configure this repo..."

cd "${REPO_DIR}"

git remote set-url origin "${REPO_SSH_URL}"
git config core.sshCommand "ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

echo
echo "Testing GitHub SSH auth..."
ssh -i "${KEY}" -o IdentitiesOnly=yes -T git@github.com || true

echo
echo "Current remote:"
git remote -v

echo
echo "[done] GitHub SSH configured for this repo."
echo "You can now run: git push"
