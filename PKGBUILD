# MabOS's GTK 4: Arch's gtk4 with one patch, mabos-user-css-live-reload.patch: open windows read the
# user's ~/.config/gtk-4.0/gtk.css again when it changes, so a theme switch reaches running apps.
# PKGBUILD is made from this template by scripts/update.py (package.conf), which follows Arch's packaging
# (gitlab.archlinux.org/archlinux/packaging/packages/gtk4, the tag in _arch_tag): version and
# dependencies come from there. Only the gtk4 package is built: demos, docs and tests are left out,
# and gtk-update-icon-cache stays Arch's. `pacman -S gtk4` goes back to Arch's.

pkgname=mabos-gtk4
_arch_tag=1-4.24.1-1 # Arch's packaging this one follows (epoch-pkgver-pkgrel)
_arch_epoch=1
pkgver=4.24.1
pkgrel=1
pkgdesc="GObject-based multi-platform GUI toolkit (MabOS: the user's gtk.css reloads live)"
url="https://github.com/mabasterYT/mabos-gtk4"
arch=(x86_64)
license=(LGPL-2.1-or-later)
depends=(
  adwaita-fonts
  adwaita-icon-theme
  at-spi2-core
  bash
  cairo
  dconf
  desktop-file-utils
  fontconfig
  fribidi
  gdk-pixbuf2
  glib2
  glibc
  graphene
  gst-plugins-bad-libs
  gst-plugins-base-libs
  gstreamer
  gtk-update-icon-cache
  harfbuzz
  iso-codes
  libcloudproviders
  libcolord
  libcups
  libegl
  libepoxy
  libgcc
  libgl
  libjpeg-turbo
  libpng
  librsvg
  libtiff
  libx11
  libxcursor
  libxdamage
  libxext
  libxfixes
  libxi
  libxinerama
  libxkbcommon
  libxrandr
  libxrender
  pango
  shared-mime-info
  tinysparql
  vulkan-icd-loader
  wayland
  xdg-desktop-portal-gtk
)
makedepends=(
  git
  glib2-devel
  gobject-introspection
  hicolor-icon-theme
  libsysprof-capture
  meson
  python-docutils
  python-gobject
  sassc
  shaderc
  vulkan-headers
  wayland-protocols
)
optdepends=('papers: default print previewer')
provides=("gtk4=$_arch_epoch:$pkgver" libgtk-4.so)
conflicts=(gtk4)
options=(!debug)
source=(
  "git+https://gitlab.gnome.org/GNOME/gtk.git#tag=$pkgver"
  gtk4-querymodules.{hook,script}
  mabos-user-css-live-reload.patch
)
b2sums=('824667f399ee085521f149f5ed2bffeb52a72034dc59f25fc88beeefb567a37e70f30ec911e39a9b5b29ca8961795555c46d50a3b1d4e8dd5d9dd0b2e021ef5b'
        'dd589bd1ad2b13f0e06f6899776a083f20a1aac24d4308d666ffd0d1cff38457b8257b8366f92e767b4233b3d86b6b54fa50339faf84c4801a824986366dce30'
        '4b90eb8d582509b09aab401313d4399cc139ad21b5dd7d45d79860d0764c7494c60714e0794e09823e51d1894ac032a994f27d79d1499abf24ee6f59bdb0c243'
        'e534a40073398e107d8ea1562b39ee7e589afc36daebceb1e8163f15cc9476a33119cff97688a930818d8eeebe324674b981c3fc14ce8e6e2d26fa3eb600ae18')

prepare() {
  cd gtk
  patch -Np1 -i ../mabos-user-css-live-reload.patch
}

build() {
  local meson_options=(
    -D broadway-backend=true
    -D cloudproviders=enabled
    -D colord=enabled
    -D documentation=false
    -D man-pages=true
    -D sysprof=enabled
    -D tracker=enabled
    -D build-demos=false
    -D build-examples=false
    -D build-tests=false
    -D build-testsuite=false
  )

  CFLAGS+=" -DG_DISABLE_CAST_CHECKS"
  arch-meson gtk build "${meson_options[@]}"
  meson compile -C build
}

package() {
  meson install -C build --no-rebuild --destdir "$pkgdir"

  install -Dm644 /dev/stdin "$pkgdir/usr/share/gtk-4.0/settings.ini" <<END
[Settings]
gtk-icon-theme-name = Adwaita
gtk-theme-name = Adwaita
gtk-font-name = Adwaita Sans 11
END

  install -Dt "$pkgdir/usr/share/libalpm/hooks" -m644 gtk4-querymodules.hook
  install -D gtk4-querymodules.script "$pkgdir/usr/share/libalpm/scripts/gtk4-querymodules"

  # Arch's gtk-update-icon-cache package has these (built by GTK 4, shared with GTK 3)
  rm -f "$pkgdir/usr/bin/gtk4-update-icon-cache" "$pkgdir/usr/share/man/man1/gtk4-update-icon-cache.1"
}
