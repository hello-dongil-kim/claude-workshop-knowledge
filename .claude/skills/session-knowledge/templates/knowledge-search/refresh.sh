#!/usr/bin/env bash
# 한 방 갱신: 인덱스(증분+prune+FTS) → [선택] 주제 MOC.
# 새 노트를 추가한 뒤 이거 한 번이면 의미검색·지도가 최신화된다.
#
#   bash refresh.sh                  # 증분 인덱스
#   bash refresh.sh --moc            # 인덱스 + 주제 MOC 재생성
#   bash refresh.sh --dry-run        # 인덱스 미리보기는 미지원, 그냥 인덱스만
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HOME/.local/share/knowledge-search/.venv/bin/python"
DO_MOC=0
MOC_OUT="${KS_VAULT:-$HOME/Documents/MyVault}/_moc"
for a in "$@"; do [ "$a" = "--moc" ] && DO_MOC=1; done

if [ ! -x "$PY" ]; then echo "venv 없음. 먼저: bash setup.sh" >&2; exit 1; fi
if [ -z "${OPENAI_API_KEY:-}" ]; then echo "OPENAI_API_KEY 미설정" >&2; exit 1; fi

echo "▶ 1/2 인덱스 (증분+prune+FTS)"
( cd "$HERE" && "$PY" index.py ) || echo "  ! index 실패"

echo "▶ 2/2 MOC"
if [ "$DO_MOC" = "1" ]; then
  ( cd "$HERE" && "$PY" moc.py --out "$MOC_OUT" --k 50 --llm )
else
  echo "  skip (--moc 주면 실행)"
fi
echo "✓ refresh 완료"
