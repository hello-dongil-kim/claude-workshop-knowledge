"""증분 인덱서.

    python index.py                 # VAULT(common.py) 인덱싱
    python index.py --target DIR    # 다른 폴더(재귀 *.md)
    python index.py --rebuild       # 전체 재구축
    python index.py --no-prune      # 고아 청크 정리 생략

증분: 내용 해시가 같은 파일은 건너뜀. prune(기본 on): 삭제·이름변경된 파일의
벡터를 제거(고아 청크 방지). 끝에 FTS(BM25) 인덱스 생성 → 하이브리드 검색.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import common as C


def existing_hashes(tbl) -> dict[str, str]:
    try:
        rows = tbl.search().select(["doc_id", "fhash"]).limit(10_000_000).to_list()
    except Exception:
        return {}
    return {r["doc_id"]: r["fhash"] for r in rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=str(C.DEFAULT_TARGET))
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--no-prune", action="store_true")
    args = ap.parse_args()

    target = Path(args.target).expanduser()
    if not target.exists():
        print(f"target not found: {target}", file=sys.stderr)
        return 2

    tbl = C.open_table(overwrite=True) if args.rebuild else C.open_table()
    if args.rebuild:
        print("rebuilt table (overwrite)")

    have = existing_hashes(tbl)
    files = sorted(f for f in target.rglob("*.md") if "processed" not in f.parts)
    print(f"scanning {len(files)} md files under {target.name}/")

    seen_ids: set[str] = set()
    added = skipped = chunks_total = 0
    for n, f in enumerate(files, 1):
        try:
            doc = C.read_doc(f)
        except Exception as e:
            print(f"  ! read fail {f.name}: {e}", file=sys.stderr)
            continue
        did = C.doc_id(str(f))
        seen_ids.add(did)
        fh = C.file_hash(doc["raw"])
        if have.get(did) == fh:
            skipped += 1
            continue

        pieces = C.md_chunk(doc["content"])
        if not pieces:
            fallback = f"{doc['title']} {doc['tags']}".strip()
            if not fallback:
                skipped += 1
                continue
            pieces = [("", fallback)]
        embed_inputs = [f"{doc['title']}\n{ctx}\n{txt}" for ctx, txt in pieces]
        vecs = C.embed(embed_inputs)

        tbl.delete(f"doc_id = '{did}'")
        rel = str(f.relative_to(target))
        tbl.add([{
            "doc_id": did, "path": str(f), "rel": rel, "title": doc["title"],
            "heading": ctx, "chunk_id": i, "text": txt,
            "date": doc["date"], "tags": doc["tags"], "doc_type": doc["doc_type"],
            "mtime": f.stat().st_mtime, "fhash": fh, "vector": v,
        } for i, ((ctx, txt), v) in enumerate(zip(pieces, vecs))])
        added += 1
        chunks_total += len(pieces)
        if n % 200 == 0:
            print(f"  [{n}/{len(files)}] added={added} skipped={skipped} chunks={chunks_total}")

    pruned = 0
    if not args.no_prune:
        tgt = str(target)
        allrows = tbl.search().select(["doc_id", "path"]).limit(10_000_000).to_list()
        stale = {r["doc_id"] for r in allrows
                 if r["path"].startswith(tgt) and r["doc_id"] not in seen_ids}
        for sid in stale:
            tbl.delete(f"doc_id = '{sid}'")
        pruned = len(stale)

    try:
        tbl.create_fts_index("text", replace=True, use_tantivy=False)
        fts = "ok"
    except Exception as e:
        fts = f"skip ({e})"

    print(f"done. added/updated={added}, skipped={skipped}, chunks={chunks_total}, "
          f"pruned={pruned}, fts={fts}")
    print(f"table rows now: {tbl.count_rows()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
