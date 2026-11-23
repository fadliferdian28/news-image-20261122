#!/usr/bin/env python3
"""Copy the v2 front page into the grader's output directory.

The sheet itself is entry.png, drawn by build_entry.py. This entrypoint
does nothing but place a verified copy where the grader expects it.
Standard library only: the grading sandbox has no third-party packages,
the repo is mounted read-only, and the output directory comes from the
MAKEFUN_OUTPUT_DIR environment variable.
"""

import hashlib
import os
import shutil
import sys

SOURCE_NAME = "entry.png"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, SOURCE_NAME)
    try:
        shutil.copyfile(source, target)
    except shutil.SameFileError:
        # Output directory is the repo itself; the file is already there.
        pass
    before = sha256_of(source)
    after = sha256_of(target)
    if before != after:
        print("checksum mismatch after copy", file=sys.stderr)
        return 1
    size = os.path.getsize(target)
    print("wrote %s (%d bytes, sha256 %s)" % (target, size, after))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
