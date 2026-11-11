#!/usr/bin/env python3
"""Makes PKGBUILD from PKGBUILD.in and Arch's packaging of the package named in package.conf.

update.py [<arch tag>]   default: Arch's newest tag (epoch-pkgver-pkgrel, e.g. 1-4.24.1-1)

package.conf (KEY=value lines): ARCH (Arch's package, e.g. gtk4), FILES (files of Arch's packaging
used here, copied over so they follow Arch), DROP_MAKEDEPENDS (Arch's build tools not needed here,
e.g. the docs'). The version, epoch and both dependency lists come from Arch's PKGBUILD at that tag,
so a new release or a changed dependency in Arch carries over. Checksums are filled in afterwards
by `makepkg -g` (scripts/build.sh). Prints the tag it used; fails loudly when Arch's PKGBUILD no
longer looks as expected.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def config():
    values = {}
    with open(os.path.join(ROOT, "package.conf")) as file:
        for line in file:
            line = line.split("#")[0].strip()
            if line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    return values["ARCH"], values.get("FILES", "").split(), values.get("DROP_MAKEDEPENDS", "").split()


def newest_tag(url):
    out = subprocess.run(["git", "ls-remote", "--tags", "--refs", url], check=True,
                         capture_output=True, text=True).stdout
    tags = [line.split("refs/tags/")[1] for line in out.splitlines() if "refs/tags/" in line]
    tags = [tag for tag in tags if re.fullmatch(r"\d+-[\d.]+-\d+", tag)]
    if not tags:
        sys.exit(f"no tags found in {url}")
    return max(tags, key=lambda tag: [int(part) for part in re.split(r"[-.]", tag)])


def field(text, name):
    match = re.search(rf"^{name}=(\S+)$", text, re.M)
    if not match:
        sys.exit(f"Arch's PKGBUILD has no {name}=")
    return match.group(1)


def array(text, name):
    match = re.search(rf"^{name}=\(\n(.*?)\n\)", text, re.M | re.S)
    if not match:
        sys.exit(f"Arch's PKGBUILD has no {name}=( ... ) list")
    items = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    if not items or any(" " in item or item.startswith("#") for item in items):
        sys.exit(f"Arch's {name} list looks different than expected: {items}")
    return items


def main():
    arch_name, files, drop = config()
    url = f"https://gitlab.archlinux.org/archlinux/packaging/packages/{arch_name}.git"
    tag = sys.argv[1] if len(sys.argv) > 1 else newest_tag(url)
    with tempfile.TemporaryDirectory() as work:
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--branch", tag, url, work],
                       check=True, stderr=subprocess.DEVNULL)
        with open(os.path.join(work, "PKGBUILD")) as file:
            arch = file.read()
        for name in files:
            shutil.copyfile(os.path.join(work, name), os.path.join(ROOT, name))

    epoch, pkgver, pkgrel = field(arch, "epoch"), field(arch, "pkgver"), field(arch, "pkgrel")
    if tag != f"{epoch}-{pkgver}-{pkgrel}":
        sys.exit(f"tag {tag} does not match Arch's PKGBUILD ({epoch}-{pkgver}-{pkgrel})")
    makedepends = [item for item in array(arch, "makedepends") if item not in drop]

    with open(os.path.join(ROOT, "PKGBUILD.in")) as file:
        text = file.read()
    sources = 1 + len(re.findall(r"^  [^\s\"#][^\n]*$", text.split("source=(")[1].split(")")[0], re.M))
    for key, value in {
        "ARCH_TAG": tag, "EPOCH": epoch, "PKGVER": pkgver, "PKGREL": pkgrel,
        "DEPENDS": "\n".join("  " + item for item in array(arch, "depends")),
        "MAKEDEPENDS": "\n".join("  " + item for item in makedepends),
        "B2SUMS": " ".join(["'SKIP'"] * sources),
    }.items():
        text = text.replace(f"@{key}@", value)
    if re.search(r"@[A-Z0-9_]+@", text):
        sys.exit("a placeholder was left in PKGBUILD")
    with open(os.path.join(ROOT, "PKGBUILD"), "w") as file:
        file.write(text)
    print(tag)


if __name__ == "__main__":
    main()
