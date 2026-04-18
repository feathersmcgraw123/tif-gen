{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pyqt5
    python3Packages.pyqtwebengine
    python3Packages.rasterio
    python3Packages.pillow
    python3Packages.requests
    python3Packages.numpy
  ];

  shellHook = ''
    echo "============================================================"
    echo " Satellite Imagery Export Tool - NixOS"
    echo "============================================================"
    echo ""
    echo " Run with: python main.py"
    echo ""
  '';
}
