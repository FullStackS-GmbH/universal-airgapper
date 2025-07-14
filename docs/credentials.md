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
