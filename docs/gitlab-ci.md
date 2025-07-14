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
