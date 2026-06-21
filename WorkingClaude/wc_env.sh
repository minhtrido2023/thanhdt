# Shared env for WorkingClaude server jobs (source this in every wrapper / cron)
export WORKDIR_8L=/home/trido/thanhdt/WorkingClaude
export PATH="$PATH:/home/trido/google-cloud-sdk/bin"
export CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh   # dtienthanh@gmail.com = BQ read-WRITE
export DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export TZ=Asia/Ho_Chi_Minh
VENV_PY=/home/trido/thanhdt/wc_venv/bin/python
cd "$WORKDIR_8L"
