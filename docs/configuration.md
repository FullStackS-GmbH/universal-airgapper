## Config File

```yaml
# config.yaml

# neuvector stanza is only necessary if you want to scan images
scanners:
  - name: neuvector-lab
    type: neuvector
    hostname: neuvector-api.dev01.atelier.cloudstacks.eu
    port: 443
    verify_tls: false
    threshold_critical: -1 # no threshold
    threshold_high: 3 # max 3 high issues for scan to be okay
    threshold_medium: -1
    threshold_low: 99999

resources:
  - type: docker
    source: ubuntu
    target: registry.lab.cloudstacks.eu/ddrack/ubuntu
    scan: neuvector-lab
    tags:
      - "20.04"
      - "22.04"
      - "latest"


  - type: helm
    source_registry: registry.fullstacks.eu
    source_chart: ddrack/mariadb
    target_registry: registry.lab.cloudstacks.eu
    target_repo: ddrack
    target_repo_type: nexus
    versions:
      - "20.2.1"
      - "20.2.0"
      - "20.1.1"

  - type: git
    source_repo: git@github.com:cloud-native-austria/cna-website.git
    target_repo: git@gitlab.com:fullstacks-gmbh/fullstacks-lab/sandboxes/ddrack/airgapper-cna-website.git
    push_mode: skip # [skip, push, force], default "skip"
    refs:
      - "main"
      - "task/nix"

  - type: git
    source_repo: https://github.com/DrackThor/home-setup.git
    target_repo: https://gitlab.com/fullstacks-gmbh/fullstacks-lab/sandboxes/ddrack/airgapper-juice-shop.git
    push_mode: skip
    refs:
      - "v.*" # <- yes, regex support for git refs
```

## Advanced Usage

Using Multiple Credential and Config Files:

Create separate credential/config files for different environments or use-cases

```
/creds/
  ├── prod.yaml
  ├── staging.yaml
  └── dev.yaml
/configs/
  ├── git.yaml
  ├── helm.yaml
  └── images.yaml
```

```shell
airgapper sync \
  --credentials-folder /creds \
  --config-folder /configs
```
