# knowledge-search (워크샵 템플릿 — 심화 B8 전용)

Vault 마크다운에 대한 **벡터 RAG** 검색 엔진. `session-knowledge`의 **심화 트랙(B8)** 산출물이다.
기본 트랙(B0~B5, 에이전트 검색)은 이 코드가 필요 없다 — 노트가 수천+이고 빠른 시맨틱 검색이 필요할 때만 쓴다.
세션이 이 코드를 학습자 환경으로 복사·설명하며 진행한다.

**멀티 LLM:** 임베딩 공급자는 `common.py`의 `EMBED_PROVIDER`로 OpenAI ↔ Gemini 전환(로컬도 추가 가능). 공급자를 바꾸면 `index.py --rebuild` 필요.

## 구성

| 파일 | 역할 |
|------|------|
| `common.py` | 설정·마크다운 청킹·임베딩·LanceDB·재순위 (← **VAULT 경로 한 줄만 수정**) |
| `index.py` | 증분 인덱서 (해시 skip · prune · FTS) |
| `search.py` | 하이브리드 검색 (벡터+BM25 RRF · 필터 · `--rerank`) |
| `moc.py` | 주제 MOC 자동 생성 (KMeans + gpt-4o-mini 네이밍) |
| `setup.sh` | venv 1회 셋업 (Vault 밖) |
| `refresh.sh` | 한 방 갱신 (index → [--moc]) |

## 빠른 시작

```bash
export KS_VAULT="$HOME/Documents/MyVault"   # 본인 Vault (또는 common.py 직접 수정)
export OPENAI_API_KEY="sk-..."
bash setup.sh
"$HOME/.local/share/knowledge-search/.venv/bin/python" index.py
"$HOME/.local/share/knowledge-search/.venv/bin/python" search.py "찾을 내용"
```

## 설계 메모

- 인덱스(venv·DB)는 **Vault 밖**(`~/.local/share/knowledge-search`) — 클라우드 동기화 폴더의 바이너리 충돌·숨김파일 이슈 회피
- 임베딩 기본 = OpenAI `text-embedding-3-large`. 로컬/타 모델로 교체는 `common.py` 상단
- 원본 마크다운이 진실의 원천 — DB는 언제든 `index.py --rebuild`로 재생성 가능한 캐시
