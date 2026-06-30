# 지식 검색 시스템 만들기 — 두 번째 뇌 II (Knowledge × Claude Code)

> **기본 트랙은 추가 설치·키·비용 0** — 이미 쓰는 Claude Code 외에 파이썬·임베딩 API 키·색인 비용이 들지 않는다.
> (※ Claude Code 자체는 계정/구독 또는 API 사용량 비용이 있습니다. "0"은 **그 위에 더 드는 게 없다**는 뜻.)
> **난이도:** 기본 ★★★☆☆ (Claude Code only) · 심화 ★★★★☆ (벡터 RAG) — **경로 이수자 기준**
> **소요:** 기본 ~70분 (B0~B5) + 선택 B6·B7 ~25분 + 심화 B8 ~30분
> **핵심 메타포:** 1편이 "서재 정리"라면, 2편은 서재에 **사서(검색)** 를 들인다.

> **시리즈 위치:** Lv.1(앱 기초) → Lv.2(Claude Code) → **Obsidian(두 번째 뇌 I, 구축·운영)** → **Knowledge(두 번째 뇌 II, 검색)** ← 이 워크샵
> **범위:** 쌓인 Vault에 **의미 검색**과 **주제 지도(MOC)** 를 붙인다. 1편의 라이트타임 정리는 전제, 빠졌던 절반(검색)을 채운다.

## 두 트랙

| 트랙 | 검색 방식 | 설치/비용 | 블록 |
|---|---|---|---|
| **기본 (Claude Code only)** | Claude가 **질의확장→grep→읽기→추론**으로 찾음(에이전트 검색) | **추가 0** (Claude Code 외 없음) | B0~B5 (+선택 B6·B7) |
| **심화 (선택)** | 임베딩 벡터 색인 + 하이브리드 + 재순위 (멀티 LLM) | OpenAI/Gemini/로컬 택1 | B8 |

> 대부분 **기본만으로 충분**. 노트가 수천+이거나 매번 빠른 시맨틱 검색이 필요하면 심화(B8).

## 사전 숙지 (거쳐온 편)

이 편은 시리즈의 **마지막 단계**. 아래를 이미 했다면 그대로 시작하세요.

| 거쳐온 편 | 여기서 가져오는 전제 |
| ---- | ---- |
| [Lv.1 — 앱 기초](https://github.com/hello-dongil-kim/claude-workshop-lv1) | Claude와 대화·문서 작업 기본 |
| [Lv.2 — Claude Code](https://github.com/hello-dongil-kim/claude-workshop-lv2) | **Claude Code 유창성** — "Claude에게 시키는" 감각 |
| [Obsidian — 두 번째 뇌 I](https://github.com/hello-dongil-kim/claude-workshop-obsidian) | 운영 중인 Vault + **B7 "Claude가 스킬 스캐폴딩" 경험** |

> "처음 코딩"이 아닙니다. obsidian B7에서 한 일(Claude로 스킬 만들기)을, 이번엔 검색으로 한 번 더.

---

## 핵심 요약 — 꼭 할 것 vs 하지 말 것

| 구분 | 항목 | 이유 |
| ---- | ---- | ---- |
| ✅ DO | **기본은 Claude Code only로 시작** | Claude Code 외 추가 설치·키·비용 0. 대부분 충분 |
| ✅ DO | **검색 전에 구조부터** (index·frontmatter·MOC) | 임베딩 없이도 품질 절반은 구조에서 |
| ✅ DO | **질의 확장 + 필터 + 근거 요구** | 단어 달라도 의미로 찾고, 환각 막음 |
| ✅ DO | **원본은 진실의 원천** | 색인(심화)은 재생성 가능한 캐시 |
| ✅ DO | **(심화) 키·DB는 Vault 밖, 멀티 LLM로 분산** | 동기화 충돌·공급자 종속 회피 |
| ❌ DON'T | **무작정 벡터부터** | 수백 규모면 에이전트 검색으로 충분. 벡터는 수천+ |
| ❌ DON'T | **(심화) API 키·민감정보를 Vault·색인에 넣기** | 키는 환경변수로만 |
| ❌ DON'T | **검색 점수에 과몰입** | 순위·체감으로 판단 |

---

## 이 과정을 마치면

- 왜 grep만으로 안 되고 의미 검색이 필요한지 설명할 수 있다
- **설치·키 없이** Claude Code로 Vault 의미 검색(에이전트 검색)을 만든다
- 검색 잘 되는 구조(index·frontmatter schema·MOC)를 설계한다
- 질의확장·필터·근거로 검색 품질을 끌어올린다
- Claude로 주제 지도(MOC)를 만든다
- 색인 없이도 도는 가벼운 운영 루프를 갖춘다
- (선택) 다관점 자가평가 / 팀 확장 청사진
- (심화) 임베딩 벡터 RAG를 멀티 LLM(OpenAI/Gemini/로컬)로 추가한다

## 사전 준비

| 항목 | 요구사항 |
| ---- | -------- |
| 선행 | lv1→lv2→obsidian 이수(권장) 또는 운영 중인 Vault |
| Claude Code | 설치 완료 |
| Vault | 노트 수백 개 이상 권장 |
| **기본 트랙** | **추가 준비 없음** (Claude Code 외 임베딩 API 키·파이썬·색인 비용 없음) |
| 심화(B8)만 | OpenAI **또는** Gemini 키 1개(또는 로컬) + uv·Python |

---

## 사용 방법

이 폴더(`claude-workshop-knowledge`)를 Claude Code에서 열고:

```text
/session-knowledge
```

처음이면 Block 0부터.

---

## 커리큘럼

```text
[기본 — Claude Code only]   B0 → B1 → B2 → B3 → B4 → B5   (+선택 B6·B7)
                           누적의벽 구조화 에이전트검색 검색품질 지식지도 운영
[심화 — 선택]               B8  임베딩 색인 + 하이브리드 + 재순위 (멀티 LLM)
```

| Block | 주제 | 트랙 | 산출물 |
| ---- | ---- | ---- | ------ |
| **0** | 누적의 벽 — grep 한계, 왜 검색 체계 | 기본 | (개념) |
| **1** | 검색을 위한 구조화 — index·schema·MOC | 기본 | 검색되는 구조 |
| **2** | 에이전트 검색 — 질의확장→grep→읽기→추론 | 기본 | **무설치 의미 검색 + 검색 스킬** |
| **3** | 검색 품질 — 동의어·필터·근거 | 기본 | 고도화된 검색 |
| **4** | 지식 지도 — Claude가 MOC 생성 | 기본 | 주제 지도 |
| **5** | 운영 — 갱신·점검 | 기본 | 운영 루프 + CLAUDE.md |
| **6** | (선택) 자가평가 | 선택 | 개선 1회 |
| **7** | (선택) 팀 확장 (개념) | 선택 | 청사진 |
| **8** | (심화) 벡터 RAG — 임베딩·하이브리드·재순위 | 심화 | 벡터 검색 엔진 |

---

## 진행 방법

각 블록은 **2턴**(Phase A 설명+실습 → Phase B 퀴즈). 실행 후 "완료"/"다음" 입력. 진도는 `progress.md`로 저장(템플릿 제공).

---

## 파일 구조

```text
claude-workshop-knowledge/
├── README.md
└── .claude/skills/session-knowledge/
    ├── SKILL.md                       (튜터 라우터)
    ├── references/ (9)                (block0~8: 기본 B0~B5 · 선택 B6·B7 · 심화 B8)
    └── templates/
        ├── vault-search-skill/        (기본 산출물: 에이전트 검색 스킬, 파이썬 없음)
        ├── knowledge-search/ (8)      (심화 B8: 벡터 RAG 코드 — OpenAI/Gemini 멀티 LLM)
        ├── progress-template.md
        ├── vault-claude-md-snippet.md
        └── safety-cost-checklist.md   (심화 전용)
```

---

## 문제 해결

| 증상 | 해결 |
| ---- | ---- |
| 스킬 인식 안 됨 | `claude-workshop-knowledge` 폴더를 열었는지 확인 |
| `/session-knowledge` 안 됨 | `/` 자동완성 확인, 없으면 폴더 다시 열기 |
| 퀴즈가 Phase A에서 나옴 | "STOP PROTOCOL 따라줘" 리마인드 |
| 에이전트 검색 후보가 너무 많음 | frontmatter 필터·MOC로 좁히기 (B3) |
| (심화) `OPENAI_API_KEY`/`GEMINI_API_KEY` 오류 | 환경변수 설정 확인 (B8) |
| (심화) Windows에서 `setup.sh` 안 됨 | `setup.bat` 사용 |
| (심화) 그 외 막힘 | `templates/safety-cost-checklist.md` |

---

## 만든 사람

**김동일 (Dongil Kim)**

- Email: <hello@dongil.kim>
- LinkedIn: <https://www.linkedin.com/in/hellodongilkim/>
- GitHub: <https://github.com/hello-dongil-kim/>
