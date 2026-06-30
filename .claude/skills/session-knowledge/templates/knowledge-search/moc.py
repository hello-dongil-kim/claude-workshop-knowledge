"""주제 MOC(Map of Content) 자동 생성.

인덱스 임베딩을 재활용해 문서를 주제 클러스터링(KMeans) → 주제별 MOC 마크다운 생성.
평면 더미 위에 '항해 가능한 지도'를 얹는다(②정보계층 = 지식그래프).

    python moc.py --out ~/Documents/MyVault/_moc          # 키워드 라벨
    python moc.py --out ~/Documents/MyVault/_moc --k 50 --llm   # gpt-4o-mini 주제명
"""
from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

import common as C

STOP = set("""
그리고 그러나 하지만 또한 그런 이런 저런 위한 통해 대한 관련 위해 더 안 못 수 것 등 및 의 가 이 그 저
the a an of for to in on and or with how why what is are be by from your you we it this that
""".split())
DATE_RE = re.compile(r"^\d{6,8}$")
NUM_RE = re.compile(r"^\d+$")
TOKEN_SPLIT = re.compile(r"[ _\-/\(\)\[\]·,.~!?…“”\"'’]+")


def label(titles: list[str], n: int = 3) -> str:
    cnt: Counter = Counter()
    for t in titles:
        for tok in TOKEN_SPLIT.split(t):
            tok = tok.strip()
            if len(tok) < 2 or tok in STOP or DATE_RE.match(tok) or NUM_RE.match(tok):
                continue
            cnt[tok] += 1
    top = [w for w, _ in cnt.most_common(n)]
    return "_".join(top) if top else "기타"


def llm_label(titles: list[str]) -> str:
    cl = C.client()
    prompt = ("다음은 한 주제 클러스터로 묶인 글 제목들이다. 이를 아우르는 간결한 한국어 "
              "주제명을 2~5어절로 하나만 출력하라. 매체명·날짜·기자명 제외, 설명 없이 주제명만.\n\n"
              + "\n".join(f"- {t}" for t in titles[:25]))
    try:
        r = cl.chat.completions.create(model=C.RERANK_MODEL, temperature=0.2,
                                       messages=[{"role": "user", "content": prompt}])
        return r.choices[0].message.content.strip().strip('"').strip("'").replace("\n", " ").strip()
    except Exception:
        return label(titles)


def slug(name: str) -> str:
    s = re.sub(r"[ /\\:|]+", "_", name.strip())
    return re.sub(r"[^\w가-힣_]", "", s) or "기타"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--llm", action="store_true")
    args = ap.parse_args()

    d = C.db()
    if C.TABLE not in d.list_tables().tables:
        print("no index. run index.py first.")
        return 2
    tbl = d.open_table(C.TABLE)
    rows = tbl.search().select(["doc_id", "rel", "title", "vector"]).limit(10_000_000).to_list()

    vecs: dict[str, list] = defaultdict(list)
    meta: dict[str, tuple[str, str]] = {}
    for r in rows:
        vecs[r["doc_id"]].append(r["vector"])
        meta[r["doc_id"]] = (r["title"], r["rel"])
    ids = list(vecs)
    if len(ids) < args.k:
        args.k = max(2, len(ids) // 2)
    X = np.array([np.mean(vecs[i], axis=0) for i in ids], dtype=np.float32)
    X /= (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    print(f"docs={len(ids)} dim={X.shape[1]} k={args.k}")

    km = KMeans(n_clusters=args.k, random_state=42, n_init=10).fit(X)
    clusters: dict[int, list[str]] = defaultdict(list)
    for did, lab in zip(ids, km.labels_):
        clusters[int(lab)].append(did)

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    idx = ["---", "title: 지식 지도 (MOC 인덱스)", "type: docs", "tags: [MOC]", "---", "",
           f"# 주제 지도 ({args.k}개 토픽)", ""]

    named = []
    for cid, members in clusters.items():
        name = llm_label([meta[m][0] for m in members]) if args.llm else label([meta[m][0] for m in members])
        named.append((name, members))
    named.sort(key=lambda x: -len(x[1]))

    seen: Counter = Counter()
    for rank, (name, members) in enumerate(named, 1):
        base = slug(name); seen[base] += 1
        if seen[base] > 1:
            base = f"{base}_{seen[base]}"
        slug_name = f"{rank:02d}_{base}"
        lines = ["---", f"title: 'MOC — {name}'", "type: docs", "tags: [MOC]", "---", "",
                 f"# MOC — {name}  ({len(members)}건)", ""]
        for title, rel in sorted((meta[m] for m in members), key=lambda x: x[0]):
            lines.append(f"- [[{Path(rel).stem}|{title}]]")
        (out / f"{slug_name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        idx.append(f"- [[{slug_name}|{name}]] — {len(members)}건")

    (out / "_index.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"wrote {len(named)} MOCs + _index.md to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
