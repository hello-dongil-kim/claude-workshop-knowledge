@echo off
REM knowledge-search 1회 셋업 (Windows). venv DB는 Vault 밖(%LOCALAPPDATA%)에 둔다.
setlocal

REM common.py의 DATA_DIR(~/.local/share/knowledge-search)와 동일 경로 사용
set "DATA=%USERPROFILE%\.local\share\knowledge-search"
set "VENV=%DATA%\.venv"
if not exist "%DATA%" mkdir "%DATA%"

where uv >nul 2>nul
if errorlevel 1 (
  echo uv가 필요합니다. 설치: https://docs.astral.sh/uv/  ^(또는 "winget install astral-sh.uv"^)
  exit /b 1
)

uv venv --python 3.13 "%VENV%"
uv pip install --python "%VENV%\Scripts\python.exe" lancedb openai google-genai tiktoken python-frontmatter pyarrow scikit-learn

echo ok. venv: %VENV%
echo 다음: set OPENAI_API_KEY=... 후  "%VENV%\Scripts\python.exe" index.py
endlocal
