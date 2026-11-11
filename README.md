# mabos-gtk4

Arch Linux's `gtk4` with one change: open GTK 4 windows read `~/.config/gtk-4.0/gtk.css` again when
it changes, so switching a theme recolors the apps that are already open instead of only the ones
started afterwards. Plain GTK 4 reads that file once, when an app starts. Part of
[MabOS](https://github.com/mabasterYT); install it from MabOS's signed pacman repository
**[mabasterYT/mabos-packages](https://github.com/mabasterYT/mabos-packages)**.

## The change

`mabos-user-css-live-reload.patch` (in `gtk/gtksettings.c`) watches the `~/.config/gtk-4.0` folder with a
`GFileMonitor`, so a `gtk.css` written in place, replaced by a rename (how theme tools write it) or
removed is seen. 150 ms after the last change it loads the file again into the same style provider
(an empty style when it is gone), and GTK restyles every open window.

Everything else is Arch's `gtk4` (now 4.24.1). It replaces `gtk4`: it provides it and its
libraries, and `pacman -S gtk4` goes back. Demos, docs and tests are not built, and
`gtk-update-icon-cache` stays Arch's. Flatpak apps use their runtime's GTK and are not affected.

The idea comes from [saneaspect/gtk4-live-css](https://github.com/saneaspect/gtk4-live-css); the patch
here is MabOS's own.

## How it is built

`.github/workflows/build.yml` runs every day, on every push and by hand, in an
`archlinux:base-devel` container. `scripts/update.py` makes `PKGBUILD` from `PKGBUILD.in` and Arch's
packaging (`package.conf` names Arch's package and the files of its packaging used here), so new
releases and dependency changes follow Arch and are committed back; `scripts/build.sh` builds the
package when its version is new and puts it, unsigned, in the `package` release.
[mabos-packages](https://github.com/mabasterYT/mabos-packages) then signs it with MabOS's key and
adds it to `[mabos]`. If the patch stops applying to a new GTK, the build fails and `[mabos]` keeps
the last good version.

## Licenses

The patch is a change to GTK and under GTK's license, LGPL-2.1-or-later. The packaging follows Arch's
(0BSD); the scripts here are 0BSD too.
