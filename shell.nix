# A build environment for the Neuron firmware: GCC ARM 10.3 (the version
# Dygma builds with), make and Python with IntelHex, from the last nixpkgs
# release that still carried GCC ARM 10.
#   nix-shell --run "make -C build release"
let
  pkgs = import (fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-24.05.tar.gz";
  }) { };
in
pkgs.mkShell {
  packages = [
    pkgs.gcc-arm-embedded-10
    pkgs.gnumake
    (pkgs.python311.withPackages (ps: [ ps.intelhex ]))
    pkgs.unzip
    pkgs.curl
  ];
}
