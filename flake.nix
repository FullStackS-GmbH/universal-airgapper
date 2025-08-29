{
  description = "Airgapper dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.python312
            pkgs.python312Packages.pip
            pkgs.poetry
          ];
          shellHook = ''
            export AIRGAPPER_CONFIG=$(pwd)/config.yaml
            export AIRGAPPER_CREDS=$(pwd)/creds
            export PYTHONPATH=$(pwd)
            poetry config virtualenvs.in-project true
            if [ -f pyproject.toml ]; then
              poetry install --no-root
            fi
          '';
        };
      }
    );
}
