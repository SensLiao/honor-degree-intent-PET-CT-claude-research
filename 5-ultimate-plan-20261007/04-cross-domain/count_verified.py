#!/usr/bin/env python3
"""Merge per-subtopic literature registers, dedupe, write per-domain CSV/JSON, and print counts.

Usage: python3 -I count_verified.py [--write]
Dedup key: DOI (lowercased) if present, else arXiv id in url, else normalized title.
Only records with source_page_opened == true and verification starting with 读了摘要 or 读了全文 count as verified.
"""
import csv, json, os, re, sys, glob
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "registers")
DOMAINS = ["psychology", "neuroscience", "llm", "medical-cv", "physics", "mathematics", "education"]
FIELDS = ["id", "domain", "subtopic", "title", "authors", "year", "venue", "url", "doi",
          "verification", "source_page_opened", "what_it_says", "target_module", "use_for_project", "transfer_risk"]
OK_PREFIX = ("读了摘要", "读了全文")

def norm_title(t):
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9一-鿿]+", " ", t)
    return " ".join(t.split())

def key_of(r):
    doi = (r.get("doi") or "").strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    if doi:
        return "doi:" + doi
    url = (r.get("url") or "").lower()
    m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", url)
    if m:
        return "arxiv:" + m.group(1)
    return "title:" + norm_title(r.get("title"))

def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("records") or data.get("papers") or list(data.values())
        return [r for r in data if isinstance(r, dict)]
    except Exception as e:
        print(f"  !! cannot read {path}: {e}", file=sys.stderr)
        return []

def main(write):
    totals = {}
    for d in DOMAINS:
        verified = OrderedDict()
        unverified = []
        bad = 0
        files = sorted(glob.glob(os.path.join(REG, d, "*.json")))
        for p in files:
            recs = load(p)
            is_unv = p.endswith(".unverified.json")
            for r in recs:
                v = (r.get("verification") or "").strip()
                opened = r.get("source_page_opened") in (True, "true", "True", 1)
                if is_unv or not v.startswith(OK_PREFIX) or not opened or not r.get("url") or not r.get("title"):
                    unverified.append(r)
                    continue
                k = key_of(r)
                if k in verified:
                    bad += 1
                    continue
                r = {f: r.get(f, "") for f in FIELDS}
                r["domain"] = d
                verified[k] = r
        totals[d] = (len(verified), len(unverified), bad, len(files))
        if write:
            out_json = os.path.join(HERE, f"literature-register-{d}.json")
            out_csv = os.path.join(HERE, f"literature-register-{d}.csv")
            rows = list(verified.values())
            for i, r in enumerate(rows, 1):
                r["id"] = f"{d}-{i:03d}"
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=1)
            with open(out_csv, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                for r in rows:
                    w.writerow(r)
            with open(os.path.join(HERE, f"literature-unverified-{d}.json"), "w", encoding="utf-8") as f:
                json.dump(unverified, f, ensure_ascii=False, indent=1)
    print("| 领域 | 已核实（去重） | 未核实 | 重复剔除 | 子文件数 | 达标 |")
    print("|---|---|---|---|---|---|")
    grand = 0
    for d in DOMAINS:
        v, u, b, nf = totals[d]
        grand += v
        print(f"| {d} | {v} | {u} | {b} | {nf} | {'是' if v >= 100 else '否'} |")
    print(f"\n合计已核实：{grand}")
    return totals

if __name__ == "__main__":
    main("--write" in sys.argv)
