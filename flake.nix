{
  description = "FullStackS Universal Airgapper dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.python312
            pkgs.python312Packages.pip
            pkgs.uv
          ];
          shellHook = ''
            export AIRGAPPER_CONFIG=$(pwd)/config.yaml
            export AIRGAPPER_CREDS=$(pwd)/creds
            export PYTHONPATH=$(pwd)
            if [ -f pyproject.toml ]; then
              uv sync --frozen
            fi
          '';
        };
      }
    );
}
