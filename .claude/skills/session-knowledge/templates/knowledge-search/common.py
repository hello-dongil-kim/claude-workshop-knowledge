"""knowledge-search: 설정·마크다운 청킹·임베딩·LanceDB 공용 모듈.

Vault 마크다운에 대한 쿼리타임 RAG 검색 레이어.
인덱스(venv·DB)는 Vault 밖에 둔다 — 클라우드 동기화 폴더의 바이너리 충돌·숨김파일 이슈 회피.

학습자 설정: 아래 VAULT 한 줄만 본인 경로로 바꾸면 된다 (또는 환경변수 KS_VAULT).
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import frontmatter
import lancedb
import pyarrow as pa
import tiktoken
from openai import OpenAI

# === 학습자 설정 ===========================================================
# 본인 Obsidian Vault(또는 검색 대상 폴더) 경로로 바꾸세요.
VAULT = Path(os.environ.get("KS_VAULT") or "~/Documents/MyVault").expanduser()
DEFAULT_TARGET = VAULT          # 하위 폴더만 인덱싱하려면 VAULT / "clippings" 등으로
# ==========================================================================

# 인덱스 데이터는 Vault 밖(동기화 폴더 밖)에 — 충돌·숨김파일 이슈 회피
DATA_DIR = Path.home() / ".local/share/knowledge-search"
DB_DIR = DATA_DIR / "db"
TABLE = "chunks"

# 임베딩 공급자 (멀티 LLM) — 여기만 바꾸면 교체. 공급자 바꾸면 index.py --rebuild 필요.
EMBED_PROVIDER = "openai"          # "openai" | "gemini"
EMBED_MODEL = "text-embedding-3-large"   # openai. gemini면 자동으로 GEMINI_EMBED_MODEL 사용
GEMINI_EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072                   # openai 3-large = 3072, gemini-embedding-001 = 3072 (동일)
RERANK_MODEL = "gpt-4o-mini"       # 재순위 LLM (OpenAI). Gemini로 바꾸려면 llm_rerank 수정

CHUNK_TOKENS = 500
CHUNK_OVERLAP = 80
EMBED_BATCH = 100

_enc = tiktoken.get_encoding("cl100k_base")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY 환경변수가 없습니다. 키를 설정한 뒤 다시 실행하세요.")
    return OpenAI(api_key=key)


def db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(DB_DIR))


def schema() -> pa.Schema:
    return pa.schema([
        pa.field("doc_id", pa.string()),
        pa.field("path", pa.string()),
        pa.field("rel", pa.string()),
        pa.field("title", pa.string()),
        pa.field("heading", pa.string()),
        pa.field("chunk_id", pa.int32()),
        pa.field("text", pa.string()),
        pa.field("date", pa.string()),
        pa.field("tags", pa.string()),
        pa.field("doc_type", pa.string()),
        pa.field("mtime", pa.float64()),
        pa.field("fhash", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), EMBED_DIM)),
    ])


def open_table(overwrite: bool = False):
    d = db()
    if overwrite:
        return d.create_table(TABLE, schema=schema(), mode="overwrite")
    if TABLE in d.list_tables().tables:        # lancedb는 ListTablesResponse 반환 → .tables
        return d.open_table(TABLE)
    return d.create_table(TABLE, schema=schema())


def doc_id(path: str) -> str:
    return hashlib.sha1(path.encode("utf-8")).hexdigest()


def file_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def read_doc(p: Path) -> dict:
    raw = p.read_text(encoding="utf-8", errors="replace")
    title, date, tags, dtype, content = p.stem, "", "", "", raw
    try:
        post = frontmatter.loads(raw)
        title = str(post.get("title") or p.stem)
        date = str(post.get("date") or post.get("created") or "")
        dtype = str(post.get("type") or "")
        t = post.get("tags") or []
        tags = " ".join(str(x) for x in t) if isinstance(t, list) else str(t)
        content = post.content
    except Exception:
        pass
    return {"title": title, "date": date, "tags": tags,
            "doc_type": dtype, "content": content, "raw": raw}


def _md_sections(content: str) -> list[tuple[str, str]]:
    out, buf, stack, cur = [], [], [], ""
    for ln in content.split("\n"):
        m = HEAD_RE.match(ln)
        if m:
            if "\n".join(buf).strip():
                out.append((cur, "\n".join(buf).strip()))
            buf = []
            level, htitle = len(m.group(1)), m.group(2).strip()
            stack = [s for s in stack if s[0] < level]
            stack.append((level, htitle))
            cur = " > ".join(t for _, t in stack)
        else:
            buf.append(ln)
    if "\n".join(buf).strip():
        out.append((cur, "\n".join(buf).strip()))
    return out or [("", content.strip())]


def md_chunk(content: str) -> list[tuple[str, str]]:
    """마크다운 헤딩 단위로 나누고, 긴 섹션만 토큰 윈도우로 분할. (heading, text) 리스트."""
    out, step = [], CHUNK_TOKENS - CHUNK_OVERLAP
    for ctx, sec in _md_sections(content):
        if not sec:
            continue
        toks = _enc.encode(sec)
        if len(toks) <= CHUNK_TOKENS:
            out.append((ctx, sec))
            continue
        for i in range(0, len(toks), step):
            out.append((ctx, _enc.decode(toks[i:i + CHUNK_TOKENS])))
            if i + CHUNK_TOKENS >= len(toks):
                break
    return out


def _embed_openai(texts: list[str]) -> list[list[float]]:
    cl = client()
    vecs: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        resp = cl.embeddings.create(model=EMBED_MODEL, input=texts[i:i + EMBED_BATCH])
        vecs.extend(d.embedding for d in resp.data)
    return vecs


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    # pip install google-genai ; GEMINI_API_KEY 필요
    from google import genai
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY 환경변수가 없습니다.")
    g = genai.Client(api_key=key)
    vecs: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        r = g.models.embed_content(
            model=GEMINI_EMBED_MODEL, contents=texts[i:i + EMBED_BATCH],
            config={"output_dimensionality": EMBED_DIM},
        )
        vecs.extend(e.values for e in r.embeddings)
    return vecs


def embed(texts: list[str]) -> list[list[float]]:
    if EMBED_PROVIDER == "gemini":
        return _embed_gemini(texts)
    return _embed_openai(texts)


def llm_rerank(query: str, cands: list[dict], k: int) -> list[dict]:
    cl = client()
    listing = "\n".join(f"[{i}] {c['title']} :: {c['snippet'][:160]}" for i, c in enumerate(cands))
    prompt = (
        f"질문: {query}\n\n다음 후보를 질문과의 관련도 순으로 재정렬하라. "
        f"가장 관련 높은 순으로 인덱스 번호만 쉼표로 출력(상위 {k}개). 예: 3,0,5\n\n{listing}"
    )
    try:
        r = cl.chat.completions.create(model=RERANK_MODEL, temperature=0,
                                       messages=[{"role": "user", "content": prompt}])
        order = [int(x) for x in re.findall(r"\d+", r.choices[0].message.content)]
        seen, ranked = set(), []
        for idx in order:
            if 0 <= idx < len(cands) and idx not in seen:
                seen.add(idx); ranked.append(cands[idx])
        for i, c in enumerate(cands):
            if i not in seen:
                ranked.append(c)
        return ranked[:k]
    except Exception:
        return cands[:k]
