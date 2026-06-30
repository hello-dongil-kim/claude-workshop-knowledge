---
name: session-knowledge
disable-model-invocation: true
compatibility: Claude Code project skill; designed for explicit slash command invocation.
description: |
  지식 검색 시스템 만들기 튜터. `/session-knowledge` 명령으로 시작한다.
  기본은 Claude Code만으로(설치·API키 없이) Vault 에이전트 검색·주제 지도를 만든다.
  심화(선택)에서 OpenAI/Gemini 등 멀티 LLM 임베딩으로 벡터 RAG를 추가한다.
  "session-knowledge", "vault 검색 만들기", "지식 검색 시스템", "에이전트 검색", "벡터 RAG" 키워드에 트리거.
---

# 세션. 지식 검색 시스템 만들기 — 두 번째 뇌 II

> **난이도:** 기본 ★★★☆☆ (Claude Code only) · 심화 ★★★★☆ (벡터 RAG) — **경로 이수자 기준**
> **소요:** 기본 ~70분 (B0~B5) + 선택 B6·B7 ~25분 + 심화 B8 ~30분
> **선행(전제):** 시리즈 lv1→lv2→obsidian 이수(또는 동급). Claude Code 유창성(lv2) + obsidian B7("Claude가 스킬 스캐폴딩") 경험 + 운영 중인 Vault.
> **기본 트랙은 설치·API 키·비용 0.** 심화(B8)만 OpenAI **또는** Gemini(또는 로컬) 키 필요.
> **핵심 메타포:** 1편이 "서재 정리"라면 이번은 서재에 **사서(검색)** 를 들인다. 기본 사서 = Claude. 심화 = 임베딩 색인까지.

## 두 트랙

| 트랙 | 검색 방식 | 설치/비용 | 블록 |
|---|---|---|---|
| **기본 (Claude Code only)** | Claude가 **질의확장→grep→읽기→추론**으로 찾음(에이전트 검색) | **0** | B0~B5 (+선택 B6·B7) |
| **심화 (선택)** | 임베딩 벡터 색인 + 하이브리드 + 재순위 | OpenAI/Gemini/로컬 택1 | B8 |

> 대부분은 **기본만으로 충분**하다. 노트가 수천 개로 커지거나 매번 빠른 시맨틱 검색이 필요할 때 심화(B8)로 간다.

## 진도 영속화 + 적응형 (세션 시작 시 적용)

- **ⓐ 이어가기:** 시작 시 `progress.md`가 있으면 읽고 "지난번 Block N까지 하셨네요. 이어서 할까요?" 제안.
- **ⓑ 진도 저장:** 각 블록 QUIZ(Phase B) 후 `progress.md` 갱신. 형식: `templates/progress-template.md`.
- **ⓒ 적응형 건너뛰기:** "이미 안다"고 하면 EXPLAIN 대신 핵심 1분 요약 후 QUIZ. 시작 시 한 번 안내.

## 용어 정리

| 용어 | 설명 |
|------|------|
| **에이전트 검색** | Claude가 질의를 넓혀 grep·읽기·추론으로 관련 노트를 찾는 방식(임베딩 없이) |
| **질의 확장** | "집값"→"부동산·전세·주거"처럼 동의어·연관어로 검색어를 넓히는 것 |
| **MOC** | Map of Content. 주제별 묶음 인덱스 노트 = 지식 지도 |
| **frontmatter** | 노트 상단 `---` 메타데이터. AI가 본문 전에 읽는 필터 |
| **(심화) 임베딩** | 문장을 의미 벡터로. 뜻이 가까우면 벡터도 가까움 |
| **(심화) 하이브리드** | 벡터(의미)+BM25(키워드) 결합 검색 |

---

## STOP PROTOCOL — 절대 위반 금지

각 블록은 반드시 **2턴**.

### Phase A (첫 턴)
1. references 파일의 **EXPLAIN**을 읽고 설명
2. **EXECUTE**를 읽고 "직접 실행해보세요" 안내
3. **반드시 STOP** — 퀴즈·AskUserQuestion·실행형 도구 호출 금지 (references/templates 읽기는 허용)

### Phase B (두 번째 턴)
1. **QUIZ** 출제(AskUserQuestion)
2. 정답/오답 피드백
3. **오답 remediation:** 해당 EXPLAIN 1~2줄 재설명 후 재시도, 2회 오답이면 해설 후 진행
4. `progress.md` 갱신
5. 다음 블록 확인

### 절대 하지 않을 것
- Phase A에서 AskUserQuestion/퀴즈, "실행해봤나요?" 질문, 한 턴에 EXPLAIN+QUIZ
- 학습자 실제 개인 데이터를 예시로 끌어오기 (reference 일반 예시만)

### 지휘자 톤 (전 블록 공통)
학습자는 명령을 직접 치지 않는다. **"Claude에게 이렇게 시키세요"**로 안내하고, Claude가 실행·디버깅을 대행, 학습자는 결과를 판정한다(PM처럼).

### 심화(B8) 전용 안전 규칙
- B8만 API 키·파이썬·venv 등장. **OS 확인**(mac/linux=`setup.sh`, Windows=`setup.bat`).
- 임베딩은 **비용** 발생(소액). 본 색인 전 규모·예상비용 한 줄 안내. 작은 폴더로 스모크 먼저.
- 키는 환경변수로만. 민감 노트 제외. venv·DB는 Vault 밖. 막히면 `templates/safety-cost-checklist.md`.

### Phase A 종료 시 필수 문구
```
---
위 내용을 직접 실행해보세요.
실행이 끝나면 "완료" 또는 "다음"이라고 입력해주세요.
```

---

## 시작 — 블록 선택

처음이면 **Block 0**. `progress.md` 있으면 이어가기 제안. 적응형(아는 블록 건너뛰기) 한 번 안내.

```text
[기본 — Claude Code only]
B0 → B1 → B2 → B3 → B4 → B5      (+선택 B6·B7)
누적의벽 구조화 에이전트검색 검색품질 지식지도 운영
 ~8    ~10    ~15      ~12    ~12   ~10

[심화 — 선택, 벡터 RAG · 멀티 LLM]
B8 임베딩 색인 + 하이브리드 + 재순위   ~30
```

## 블록 라우팅

| Block | 파일 | 주제 | 트랙 |
|------|------|------|------|
| 0 | `references/block0-wall.md` | 누적의 벽 — grep 한계, 왜 검색 체계가 필요한가 | 기본 |
| 1 | `references/block1-structure.md` | 검색을 위한 구조화 — index·frontmatter schema·MOC | 기본 |
| 2 | `references/block2-agent-search.md` | 에이전트 검색 — 질의확장→grep→읽기→추론 (무설치) | 기본 |
| 3 | `references/block3-search-quality.md` | 검색 품질 — 동의어·필터·MOC경유·한국어 (Claude only) | 기본 |
| 4 | `references/block4-moc.md` | 지식 지도 — Claude가 주제별 MOC 생성 | 기본 |
| 5 | `references/block5-operate.md` | 운영 — 인덱스·MOC 갱신, 점검 (Claude only) | 기본 |
| 6 | `references/block6-evaluate.md` | (선택) 자가평가 — 다관점 점검 | 선택 |
| 7 | `references/block7-team.md` | (선택) 팀으로 확장 — 승격·거버넌스 (개념) | 선택 |
| 8 | `references/block8-vector.md` | (심화) 벡터 RAG — 임베딩(OpenAI/Gemini/로컬)+하이브리드+재순위 | 심화 |

## 템플릿

- `templates/vault-search-skill/` — 기본 트랙 산출물: Vault에 설치하는 **에이전트 검색 스킬**(질의확장→grep→읽기→추론). 파이썬 없음
- `templates/knowledge-search/` — 심화(B8) 벡터 RAG 코드(common/index/search/moc/setup/refresh). OpenAI·Gemini 멀티 LLM
- `templates/progress-template.md` · `templates/vault-claude-md-snippet.md` · `templates/safety-cost-checklist.md`(심화용)
