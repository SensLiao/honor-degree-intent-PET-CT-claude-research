"""List files changed since the 10-05 snapshot (5090 env-check copy) and build unified diffs for review."""
import base64, difflib, hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(r"C:/Users/廖神/Desktop/Honor degree")
CODE = ROOT / "projects/petct_textual_intent"
MANIFEST = CODE / "records/verification/ops-rtx5090-sirb-env-data-prep-20261005/code-manifest.sha256"
REMOTE_CODE = "/share/rlia4081/honor_degree/runs/editor-sirb-code-rtx5090-envcheck-20261005/code"
TREES = ("scripts", "configs", "tests", "schemas")
OUT = Path(__file__).resolve().parent
def norm(b): return b.replace(b"\r\n", b"\n")
before = {}
for line in MANIFEST.read_text(encoding="utf-8").splitlines():
    h, name = line.split("  ", 1)
    before[name] = h
now = {}
for tree in TREES:
    for p in (CODE / tree).rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            now[p.relative_to(CODE).as_posix()] = hashlib.sha256(norm(p.read_bytes())).hexdigest()
changed = sorted(n for n in now if n in before and now[n] != before[n])
added = sorted(n for n in now if n not in before)
removed = sorted(n for n in before if n not in now and n.split("/")[0] in TREES)
only = sys.argv[1:]  # optional path prefixes to keep
def keep(n): return not only or any(n.startswith(o) for o in only)
changed, added = [n for n in changed if keep(n)], [n for n in added if keep(n)]
print(f"changed={len(changed)} added={len(added)} removed={len(removed)}")
for n in changed: print("  M", n)
for n in added: print("  A", n)
for n in removed: print("  D", n)
# fetch before-versions of changed files from the 5090 snapshot
script = "set -e\ncd " + REMOTE_CODE + "\nfor f in " + " ".join(changed) + "; do echo \"@@FILE $f\"; base64 -w0 \"$f\"; echo; done\n"
res = subprocess.run([r"D:/Anaconda/python.exe", "-W", "ignore", str(ROOT / ".agents/skills/server-status/remote_exec.py"), "rtx5090"],
                     input=script.encode(), capture_output=True, timeout=300)
text = res.stdout.decode("utf-8", "replace")
olds, cur = {}, None
for line in text.splitlines():
    if line.startswith("@@FILE "): cur = line[7:].strip(); continue
    if cur and line.strip() and not line.startswith("---"):
        olds[cur] = base64.b64decode(line.strip()); cur = None
missing = [n for n in changed if n not in olds]
if missing: print("MISSING before-versions:", missing)
parts = []
for n in changed:
    a = norm(olds.get(n, b"")).decode("utf-8", "replace").splitlines(keepends=True)
    b = norm((CODE / n).read_bytes()).decode("utf-8", "replace").splitlines(keepends=True)
    parts.append("".join(difflib.unified_diff(a, b, f"a/{n}", f"b/{n}", n=3)))
for n in added:
    b = norm((CODE / n).read_bytes()).decode("utf-8", "replace").splitlines(keepends=True)
    parts.append("".join(difflib.unified_diff([], b, "/dev/null", f"b/{n}", n=3)))
(OUT / "k-code.diff").write_text("".join(parts), encoding="utf-8")
(OUT / "k-code-files.json").write_text(json.dumps({"changed": changed, "added": added, "removed": removed}, indent=1), encoding="utf-8")
print("diff bytes", (OUT / "k-code.diff").stat().st_size)
