# Airgapper

A CLI tool for syncing Docker images, Helm charts, and Git repositories across air-gapped environments.

- [Features](#features)
- [Usage](#usage)
- [Credential Management](#credential-management)
- [Sync Config File](#sync-config-file)
- [Advanced Usage](#advanced-usage)
- [Debug Mode](#debug-mode)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [GitLab CI Component Usage](#gitlab-ci-component-usage)
- [Contributing](#contributing)

## Features

- sync Docker container images from one registry to another
- sync Helm charts from one registry to another (including OCI registries)
- sync Git repositories from one host to another
  - support wildcards for ref specification
- YAML configuration
- Flexible credential management

## Usage

```shell
docker run \
  -v $(pwd)/.ssh:/home/airgapper/.ssh \ # optional if you use git over SSH
  -v $(pwd)/creds:/mnt/creds \
  -v $(pwd)/config.yaml:/mnt/config.yaml \
  airgapper:local \
  --credentials-folder /mnt/creds/ \
  --config /mnt/config.yaml
```

## Credential Management

Credentials can be provided in two ways:

- Single YAML file using `--credentials-file`
- Directory of YAML files using `--credentials-folder`

> BEWARE: Azure Repos HTTPS authentication is only supported for pulling repos.
> If you want to authenticate at Azure Repos with HTTPS, set the `username` to `AzureReposAuthnSucks`.
> You then need to make sure to set an environment variable with the HTTP header value you want to use to authenticate.
> Set the `password` field to the name of this env variable.
> Under the hood this hack works like this:

```python
if username and password:
    if username == "AzureReposAuthnSucks":
        git_options.append(f"--config-env=http.extraheader={password}")
git.Repo.clone_from(repo_url, target_path, branch=ref, single_branch=True,multi_options=git_options)
```

So you have to prepare an env var like this .. and specify the var name as `password`.

```shell
export REPO_AUTH_HEADER=$(echo -n "Authorization: Basic "$(printf ":%s" "$MY_PAT" | base64))
# password: REPO_AUTH_HEADER
```

[I didn't want to do this, but MS made me do it... I know, it sucks!](https://learn.microsoft.com/en-us/azure/devops/repos/git/auth-overview?view=azure-devops&tabs=Windows)

Example credentials file structure:

```yaml
image:
  - name: registry.example.com
    username: dockeruser
    password: dockerpass
  - name: docker.io
    username: hubuser
    password: hubpass
helm:
  - name: registry.helmrepo.com
    username: helmuser
    password: helmpass
git:
  - name: github.com
    username: gituser
    password: personaltoken
    ssh_key_path: /path/to/ssh/key
scanners:
  - name: neuvector-lab
    type: neuvector
    username: admin
    password: verySecurePassword
```

If you want to use git over SSH, you need to provide a valid SSH config.
Therefore, prepare a folder containing the used SSH keys, a SSH config and a known_hosts file.
If you run the airgapper locally via Python, you don't need to do that, since Python will use your local git setup.
If you use the container version of this airgapper, mount the resulting files in the `airgapper` users .ssh directory `/home/airgapper/.ssh`.

```
/.ssh/
  ├── config
  ├── id_ed25519
  └── known_hosts
```

```shell
# .ssh/config -> ssh config
Host github.com
    IdentityFile ~/.ssh/id_ecdsa
Host gitlab.com
    IdentityFile ~/.ssh/id_ecdsa

# --------
# .ssh/id_edxxx
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
-----END OPENSSH PRIVATE KEY-----

# --------
# .ssh/known_hosts
github.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=
github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl
gitlab.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBFSMqzJeV9rUzU4kWitGjeR4PWSa29SPqJ1fVkhtj3Hw9xjLVXVYrU9QlYWrOLXBpQ6KWjbjTDTdDkoohFzgbEY=
gitlab.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAfuCHKVTjquxvt6CM6tdG4SLp1Btn/nOeHHE5UOzRdf
# ...
```

To create the know_hosts file, use the `ssh-keyscan <hostname>` command.

## Sync Config File

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

## Debug Mode

Enable debug logging:

```shell
airgapper sync \
  --debug \
  --credentials-file creds.yaml \
  --config-file config.yaml
```

## Error Handling

The tool will:

- Validate all credential files against the required schema
- Exit with error if credential validation fails
- Provide detailed error messages for failed operations
- Continue with remaining items if one sync operation fails

## Security Considerations

- Store credentials in secure locations with appropriate permissions
- Use environment variables for sensitive information
- Consider using SSH keys for Git operations instead of passwords
- Rotate credentials regularly
- Use separate credentials for different environments

## GitLab CI Component Usage

```yaml
include:
  - component: <airgapper-repo-group>/universal-airgapper@1
    inputs:
      stage: run
      image: <registry>/<repo>/airgapper:latest
      config-folder: ${CI_PROJECT_DIR}
      # ${UNIVERSAL_AIRGAPPER_CREDS} <- set this GitLab CI variable
      credentials-file: ${UNIVERSAL_AIRGAPPER_CREDS}
      debug: '--debug'
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
