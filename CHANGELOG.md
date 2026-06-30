# Changelog

이 워크샵의 주요 변경 이력. 형식은 [Keep a Changelog](https://keepachangelog.com/) 기반. 시리즈 공통 표준은 제작자 내부 문서 `workshop-series-standard`를 따른다.

## [2026-06-29] — 두 트랙 재구성 (기본 Claude-only / 심화 벡터)

### Changed (변경)

- **기본 트랙 = Claude Code only** 로 전면 재구성. 임베딩·API 키·파이썬·비용 없이 **에이전트 검색**(질의확장→grep→읽기→추론)으로 의미 검색. council ②(대상·환경 미스매치) 정면 해소.
- B0~B5 전면 재작성: B0 누적의벽(해법=구조화+에이전트검색) · B1 검색을 위한 구조화 · B2 에이전트 검색 · B3 검색 품질(Claude only) · B4 MOC(Claude가 생성, KMeans 제거) · B5 운영(색인 없어 갱신 부담 0).
- 기존 임베딩 중심 블록(구 B1 설계·B2 인덱스·B3 하이브리드) → **심화 B8 한 블록으로 통합·강등**.

### Added (추가)

- `references/block8-vector.md` — 심화 벡터 RAG(임베딩·하이브리드·재순위), **멀티 LLM(OpenAI/Gemini/로컬)**.
- `templates/vault-search-skill/SKILL.md` — 기본 산출물: Vault 에이전트 검색 스킬(`knowledge-find`). 파이썬 없음.
- `templates/knowledge-search/common.py`에 `EMBED_PROVIDER`(OpenAI↔Gemini) + `_embed_gemini` 추가. setup에 `google-genai`.
- B5에 **"사람용 의미 검색"** 섹션 격상 — Smart Composer(Vault RAG·멀티 LLM)·Smart Connections를 사람 뷰로, **로컬 임베딩(Ollama bge-m3 등)=키리스** 강조. 에이전트 검색과 짝.
- **페다고지 보강 (원리+스스로 설계):** B0에 "핵심 원리 6" 카드(단계 너머 추론용), B5 끝에 "내 지식체계를 직접 설계하기" 캡스톤 성찰 6문(복사 아닌 자기 설계 유도). 목표 = 똑같이 따라하기 아닌 "기본·원리 + 스스로 고민·구축".

### Removed (삭제)

- 구 `block1-design.md` · `block2-index.md` · `block3-quality.md` (신규 구조로 대체).

> 결정 근거: 사용자 요청 — 기본은 Claude Code only, 심화로 OpenAI/Gemini 등 멀티 LLM 추가. council 평가의 최대 약점(②대상적합성)을 구조적으로 해결.

## [2026-06-29] — 시리즈 정합성 (역방향 전제)

### Changed (변경)

- **별도 1.5편(브리지) 신설하지 않기로 결정.** 근거: 학습자는 lv1→lv2→obsidian을 거쳐 도착 — lv2(Claude Code 유창성) + **obsidian B7("Claude가 스킬 스캐폴딩")** 으로 런웨이가 이미 깔림. 이 편 B2~B5는 그 패턴의 반복. 진짜 새것은 API 키 하나뿐.
- **역방향 전제 정비** — README에 "사전 숙지(거쳐온 편)" 섹션 추가: lv1·lv2·obsidian 역방향 링크 + 각 편이 주는 전제 역량. (순방향 "다음 편" 링크는 의도적으로 두지 않음.)
- **프레이밍 전환** — "절벽"→"마지막 계단". 난이도 "★★★~★★★★ (경로 이수자 기준)". obsidian B7 ↔ 이 편 동일 패턴 연결을 README·SKILL에 명시.

## [2026-06-29] — council 평가 반영 (즉시 4건)

### Changed (변경)

- **난이도·시간 정직화** — README·SKILL: 난이도 ★★★☆☆~★★★★☆ 범위, 소요 ~90~150분(환경 셋업 포함). "솔직한 진입장벽" 콜아웃 + 대상에 "터미널·API 거부감 없는" 명시.
- **지휘자 톤** — "코드를 직접 치지 않고 Claude에게 시킨다(PM처럼)" 원칙을 SKILL 실행형 규칙 + B2~B5 콜아웃에 반영.

### Added (추가)

- `templates/knowledge-search/setup.bat` — Windows 셋업(기존 mac/linux `setup.sh`와 짝). common.py와 동일 경로(`~/.local/share/knowledge-search`).
- `templates/safety-cost-checklist.md` — 안전(키·민감노트·원본불변)·비용·흔한 오류표·한국어 검색 기대치 1장. SKILL·B2·B5·README에서 연결.
- README: OS 분기·비용 미리보기·Windows 문제해결 행.

> 근거: `00_inbox/2026-06-29_워크샵-knowledge-유효성-평가_council_v0.1.0.md` (3채널 종합 ~7.5/10, ④차별성 9.3 / ②대상적합성 5.0). 1.5편 브리지는 위 "시리즈 정합성" 항목대로 **불필요 결정**. 90분 다이어트(B4 KMeans 선택화)는 **미채택** — B4(지식지도)는 차별 요소라 필수 유지하되, 알고리즘 이해를 지휘자 톤(Claude에 시키고 결과만 판정)으로 경량화해 시간 부담을 낮춤.

## [2026-06-29] — 최초 작성 (v1.0)

### Added (추가)

- `session-knowledge` 튜터 스킬 — Vault에 쿼리타임 RAG(의미검색)·주제 지도(MOC)를 붙이는 Lv.3 세션. session-obsidian(두 번째 뇌 I)의 다음 레벨 확장.
- SKILL.md 라우터 (STOP PROTOCOL·진도 영속화·적응형·실행형 안전 규칙·블록 라우팅 B0~B7)
- references 전 8블록 (각 EXPLAIN→EXECUTE→QUIZ, P1 성공기준 + P3 회상·적용 퀴즈):
  - B0 누적의 벽 / B1 검색 레이어 설계 / B2 인덱스 구축 / B3 검색 품질(하이브리드·재순위)
  - B4 지식 지도(MOC) / B5 운영(refresh·prune·이원화) / B6(선택) 자가평가 / B7(선택) 팀 확장(개념)
- `templates/knowledge-search/` — 작동하는 검색 엔진 코드 (common·index·search·moc·setup·refresh + README). 하이브리드(벡터+BM25 RRF)·재순위·마크다운 청킹·증분·prune·FTS 포함. py_compile·bash -n 검증 통과
- `templates/progress-template.md`, `templates/vault-claude-md-snippet.md`
- README(자가학습 핸드북), LICENSE, `.markdownlint.jsonc`, `.gitignore` (시리즈 공통)

### 비고

- 시리즈 사슬: lv1 → lv2 → obsidian(두 번째 뇌 I) → **knowledge(두 번째 뇌 II)**
- 외부 의존: OpenAI API 키(임베딩·재순위), uv·Python 3.13, LanceDB
- 미발행: GitHub 푸시는 사용자 확인 후
