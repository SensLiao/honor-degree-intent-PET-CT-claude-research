"""Read-only copy of server files to this machine, with sha256 checked against the server.

Usage: python fetch_remote.py <host> <local_dir> <remote_file> [<remote_file> ...]
  --prefix-ok   for a file that is still growing (a training log): the server hash is taken over the first N bytes,
                N = the size of the local copy, so the check proves the local copy is an exact prefix.
Writes <local_dir>/TRANSFER_VERIFICATION.json (appends rows).  Nothing on the server is written.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(r"C:/Users/廖神/Desktop/Honor degree/.agents/skills/server-status")))
import remote_exec  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    prefix_ok = "--prefix-ok" in sys.argv
    host, local_dir, remotes = args[0], Path(args[1]), args[2:]
    local_dir.mkdir(parents=True, exist_ok=True)
    client = remote_exec.connect(host)
    sftp = client.open_sftp()
    rows = []
    bad = 0
    for remote in remotes:
        target = local_dir / os.path.basename(remote)
        sftp.get(remote, str(target))
        size = target.stat().st_size
        command = (f"head -c {size} '{remote}' | sha256sum" if prefix_ok else f"sha256sum '{remote}'")
        _, stdout, _ = client.exec_command(command, timeout=600)
        remote_hash = stdout.read().decode().split()[0]
        local_hash = sha256_file(target)
        same = remote_hash == local_hash
        bad += 0 if same else 1
        rows.append({"host": host, "source": remote, "file": target.name, "bytes": size,
                     "check": "prefix of a growing file" if prefix_ok else "whole file",
                     "local_sha256": local_hash, "remote_sha256": remote_hash, "same": same})
        print(f"{'OK ' if same else 'BAD'} {target.name} {size} bytes local={local_hash[:16]} remote={remote_hash[:16]}")
    sftp.close()
    client.close()
    record = local_dir / "TRANSFER_VERIFICATION.json"
    old = json.loads(record.read_text(encoding="utf-8")) if record.exists() else {"files": []}
    old.setdefault("files", []).extend(rows)
    old["captured_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    old["method"] = "SFTP get (read-only), sha256 of the local copy compared with sha256sum on the server"
    record.write_text(json.dumps(old, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
