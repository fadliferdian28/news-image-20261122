"""Entry program for the 22 November 2026 one-day news image.

The image is drawn once, by hand, in this repository's entry.png. All this
program does is place an exact copy of it where the grader expects it:
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png when the variable is
unset). It uses only the Python standard library, reads nothing from the
network, and writes nothing else. After copying it hashes both files and
refuses to report success unless the copy is byte-for-byte identical.
"""

import hashlib
import os
import shutil
import sys


def _digest(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    if os.path.abspath(source) == os.path.abspath(target):
        return 0
    shutil.copyfile(source, target)
    if _digest(source) != _digest(target):
        print("entry.png copy failed its sha256 check", file=sys.stderr)
        return 1
    print("entry.png sha256: " + _digest(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
