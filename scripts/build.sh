#!/usr/bin/env bash
# Follows Arch's packaging and builds the package when its version is not in this repository's
# "package" release yet, then puts it there. Unsigned: mabasterYT/mabos-packages signs it with
# MabOS's key and adds it to the [mabos] pacman repository. Runs as root in an archlinux:base-devel
# container (the GitHub workflow); needs GH_TOKEN. FORCE=1 builds even when the version is there.
set -euo pipefail
cd "$(dirname "$0")/.."

release=package

pacman -Syu --noconfirm --needed git github-cli python >/dev/null

# makepkg refuses to run as root
id builder >/dev/null 2>&1 || useradd -m builder
echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder
chown -R builder: .
git config --global --add safe.directory "$PWD"
as_builder() { sudo -u builder -H "$@"; }

# Follow Arch's packaging: a new release or changed dependencies are committed back
tag=$(as_builder python3 -I scripts/update.py)
sums=$(as_builder makepkg -g 2>/dev/null)
python3 -I - "$sums" <<'PY'
import re, sys
text = open("PKGBUILD").read()
open("PKGBUILD", "w").write(re.sub(r"b2sums=\(.*?\)\n", sys.argv[1] + "\n", text, flags=re.S))
PY
# Only files already here: PKGBUILD and the ones copied from Arch (never makepkg's downloads)
if ! git diff --quiet; then
    git add -u
    git -c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
        commit -q -m "Follow Arch's packaging $tag"
    git push -q origin HEAD
fi

pkgname=$(sed -n 's/^pkgname=//p' PKGBUILD)
pkgver=$(sed -n 's/^pkgver=//p' PKGBUILD)
pkgrel=$(sed -n 's/^pkgrel=//p' PKGBUILD)
package="$pkgname-$pkgver-$pkgrel-x86_64.pkg.tar.zst"

if ! gh release view "$release" >/dev/null 2>&1; then
    gh release create "$release" --title "$pkgname package" \
        --notes "The newest build, unsigned. Install it from the signed [mabos] repository instead: see mabasterYT/mabos-packages."
fi
published=$(gh release view "$release" --json assets --jq '.assets[].name')
if grep -qxF "$package" <<<"$published" && [ "${FORCE:-0}" != 1 ]; then
    echo "$package is built already"
    exit 0
fi

as_builder makepkg -s --noconfirm
gh release upload "$release" --clobber "$package"
{ grep -E "^$pkgname-.*\.pkg\.tar\.zst$" <<<"$published" | grep -vxF "$package" || true; } |
    while read -r old; do gh release delete-asset "$release" "$old" --yes; done
echo "built $package"
