"""하이브리드 시맨틱 검색.

    python search.py "질문"               # 하이브리드(벡터+BM25, RRF) top-5
    python search.py "질문" -k 8 --json
    python search.py "질문" --rerank       # + gpt-4o-mini 재순위화
    python search.py "질문" --tag 브랜드     # 태그 필터
    python search.py "질문" --since 2025-01 # date >= 필터
    python search.py "질문" --type clipping
    python search.py "질문" --vector-only   # 순수 벡터
"""
from __future__ import annotations

import argparse
import json
import sys

import common as C

RRF_K = 60


def _key(r):
    return (r["path"], r.get("chunk_id", 0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--rerank", action="store_true")
    ap.add_argument("--vector-only", action="store_true")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--since", default=None)
    ap.add_argument("--type", dest="dtype", default=None)
    args = ap.parse_args()

    d = C.db()
    if C.TABLE not in d.list_tables().tables:
        print("no index yet. run: python index.py", file=sys.stderr)
        return 2
    tbl = d.open_table(C.TABLE)

    where = []
    if args.tag:
        where.append(f"tags LIKE '%{args.tag}%'")
    if args.dtype:
        where.append(f"doc_type = '{args.dtype}'")
    if args.since:
        where.append(f"date >= '{args.since}'")
    flt = " AND ".join(where) if where else None

    pool = args.k * 6
    qvec = C.embed([args.query])[0]

    vq = tbl.search(qvec).metric("cosine").limit(pool)
    if flt:
        vq = vq.where(flt)
    vec_hits = vq.to_list()

    fts_hits = []
    if not args.vector_only:
        try:
            fq = tbl.search(args.query, query_type="fts").limit(pool)
            if flt:
                fq = fq.where(flt)
            fts_hits = fq.to_list()
        except Exception:
            fts_hits = []

    fused: dict = {}
    for rank, r in enumerate(vec_hits):
        fused.setdefault(_key(r), {"r": r, "s": 0.0})["s"] += 1.0 / (RRF_K + rank)
    for rank, r in enumerate(fts_hits):
        fused.setdefault(_key(r), {"r": r, "s": 0.0})["s"] += 1.0 / (RRF_K + rank)
    ranked_chunks = sorted(fused.values(), key=lambda x: x["s"], reverse=True)

    best: dict = {}
    for item in ranked_chunks:
        r = item["r"]
        if r["path"] not in best:
            best[r["path"]] = {
                "title": r["title"], "rel": r["rel"], "path": r["path"],
                "heading": r.get("heading", ""), "date": r.get("date", ""),
                "tags": r.get("tags", ""), "score": round(item["s"], 4),
                "snippet": " ".join(r["text"].split())[:240],
            }
    hits = list(best.values())

    if args.rerank and hits:
        cands = [{"title": h["title"], "snippet": h["snippet"], **h}
                 for h in hits[:max(args.k * 4, 20)]]
        hits = C.llm_rerank(args.query, cands, args.k)
    else:
        hits = hits[:args.k]

    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return 0
    if not hits:
        print("(no matches)")
        return 0
    for i, h in enumerate(hits, 1):
        meta = " · ".join(x for x in [h.get("date", ""), h.get("heading", "")] if x)
        print(f"{i}. [{h.get('score','')}] {h['title']}")
        print(f"   {h['rel']}" + (f"  ({meta})" if meta else ""))
        print(f"   {h['snippet']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
