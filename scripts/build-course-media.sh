#!/bin/sh
# Reassemble the reviewed MP4 exactly; publish only after its SHA-256 matches.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_dir="$root/media-source/probability-statistics/chapter8-introduction-2026-10-28"
target="$root/static/teaching/probability-statistics/videos/chapter8-introduction-2026-10-28.mp4"
expected=de2bf2570020f960d12079acbf3d985efe9e7d181a2d60af43513541a8af440e
mkdir -p "$(dirname -- "$target")"
tmp=$(mktemp "$target.tmp.XXXXXX")
trap 'rm -f "$tmp"' EXIT HUP INT TERM
cat "$source_dir"/part-[0-9][0-9][0-9] > "$tmp"
if command -v sha256sum >/dev/null 2>&1; then
  actual=$(sha256sum "$tmp" | cut -d ' ' -f 1)
else
  actual=$(shasum -a 256 "$tmp" | cut -d ' ' -f 1)
fi
if [ "$actual" != "$expected" ]; then
  echo 'Course recording checksum mismatch; refusing to publish.' >&2
  exit 1
fi
mv "$tmp" "$target"
printf '%s\n' 'Chapter 8 recording verified and assembled.'
