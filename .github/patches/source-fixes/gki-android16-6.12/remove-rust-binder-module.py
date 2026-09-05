#!/usr/bin/env python3
"""Strip any common/modules.bzl entry referencing rust_binder.ko.

Used when the Rust Binder driver isn't enabled/buildable on this source
tree/config, so the Kleaf dist target (//common:kernel_aarch64_dist)
doesn't fail at packaging time with:

    ERROR: Unable to find drivers/android/binder/rust_binder.ko in any of
    the following directories: ...

This assumes modules.bzl lists module paths one per line (the normal
Starlark list-of-strings layout used by android16-6.12's common/modules.bzl).
If your tree formats the list differently (e.g. multiple entries per line),
adjust the matching logic below accordingly.

Usage:
    remove-rust-binder-module.py <modules.bzl>
"""
import sys


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} <modules.bzl>")

    path = sys.argv[1]

    with open(path) as fh:
        lines = fh.readlines()

    removed = 0
    kept = []
    for line in lines:
        if "rust_binder.ko" in line:
            removed += 1
            continue
        kept.append(line)

    if removed == 0:
        print("  no rust_binder.ko entries found, nothing to remove")
        return

    with open(path, "w") as fh:
        fh.writelines(kept)

    print(f"  removed {removed} line(s) referencing rust_binder.ko from {path}")


if __name__ == "__main__":
    main()
