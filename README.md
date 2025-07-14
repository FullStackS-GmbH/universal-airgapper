# Universal Airgapper

A CLI tool for syncing Docker images, Helm charts, and Git repositories across air-gapped environments.

- [Features](#features)
- [Usage](#usage)
- [Credential Management](./docs/credentials.md)
- [Sync Config File](./docs/configuration.md)
- [Debug Mode](#debug-mode)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [GitLab CI Component Usage](./docs/gitlab-ci.md)
- [Contributing](#contributing)

## Features

- sync Docker container images from one registry to another
- sync Helm charts from one registry to another (including OCI registries)
- sync Git repositories from one host to another
    - support wildcards for ref specification
- YAML configuration
- Flexible credential management

## Usage

You must provide exactly one option from each of these groups:

### Credentials (mutually exclusive)

| Argument               | Description                                       |
|------------------------|---------------------------------------------------|
| `--credentials-file`   | Path to a YAML credentials file                   |
| `--credentials-folder` | Path to a folder containing YAML credential files |

### Configuration (mutually exclusive)

| Argument          | Description                                        |
|-------------------|----------------------------------------------------|
| `--config-file`   | Path to a YAML sync config file                    |
| `--config-folder` | Path to a folder containing YAML sync config files |

## Optional Arguments

| Argument  | Description                                  |
|-----------|----------------------------------------------|
| `--debug` | Enable debug logging (flag, no value needed) |

```shell
docker run \
  -v $(pwd)/.ssh:/home/airgapper/.ssh \ # optional if you use git over SSH
  -v $(pwd)/creds:/mnt/creds \
  -v $(pwd)/config.yaml:/mnt/config.yaml \
  airgapper:local \
  --credentials-folder /mnt/creds/ \
  --config-file /mnt/config.yaml
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

## Contributing

Contributions are welcome! Please refer to our [CONTRIBUTING guid](CONTRIBUTING.md).

## Feature Requests / Ideas

We welcome feature requests! Please use the issue template and provide:

- A clear description of the feature
- Why it would be valuable
- Any implementation ideas you might have
