#!/usr/bin/env bash
# knowledge-search 1회 셋업. venv·DB는 Vault 밖(~/.local/share/knowledge-search)에 둔다.
set -euo pipefail

DATA="$HOME/.local/share/knowledge-search"
VENV="$DATA/.venv"
mkdir -p "$DATA"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv가 필요합니다. 설치: brew install uv  (또는 https://docs.astral.sh/uv/)" >&2
  exit 1
fi

uv venv --python 3.13 "$VENV"
uv pip install --python "$VENV/bin/python" \
  lancedb openai google-genai tiktoken python-frontmatter pyarrow scikit-learn

echo "ok. venv: $VENV"
echo "다음: export OPENAI_API_KEY=... 후  \"$VENV/bin/python\" index.py"
