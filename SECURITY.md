# Security Policy

## Reporting a Vulnerability

We take the security of Universal Airgapper seriously.
If you believe you've found a security vulnerability, please follow these steps to report it:

### Direct Reporting Process

1. **Do not disclose the vulnerability publicly** until it has been addressed by the maintainers.
2. **Send details of the vulnerability** to [engineering@fullstacks.eu](mailto:engineering@fullstacks.eu) with the following
   information:
    - A clear description of the vulnerability
    - Steps to reproduce the issue
    - Potential impact of the vulnerability
    - Any potential mitigations you've identified
    - Your contact information for follow-up (optional)

3. **Use a descriptive subject line** such as "Airgapper Security Vulnerability: [Brief Description]"

### What to Expect

- **Initial Response**: We aim to acknowledge your report within 72 hours.
- **Updates**: We will keep you informed about our progress in addressing the vulnerability.
- **Resolution Timeline**: The time to fix will vary based on severity and complexity.
- **Disclosure**: We will coordinate with you on the public disclosure of the vulnerability after it has been fixed.

## Security Best Practices for Using Universal Airgapper

When using this tool, please follow these security best practices:

1. **Credential Management**:
    - Store credentials in secure locations with appropriate permissions
    - Rotate credentials regularly
    - Use separate credentials for different environments

2. **SSH Keys and Authentication**:
    - Use SSH keys for Git operations instead of passwords when possible
    - Secure your SSH private keys with strong passphrases
    - Ensure appropriate permissions are set on SSH key files

3. **Docker Security**:
    - Run the container with the principle of least privilege
    - Keep the container image updated to the latest version
    - Use volume mounts with appropriate permissions

4. **Network Security**:
    - Consider using VPNs or secure networks when syncing between environments
    - Validate TLS certificates when connecting to secure endpoints

## Supported Versions

Only the latest release of Universal Airgapper receives security updates.
We encourage users to stay updated with the latest version.

## Security Updates

Security updates will be announced through:

- Release notes
- The repository's security advisories
- Direct communication to reported email (if provided)

## Acknowledgments

We appreciate the responsible disclosure of security vulnerabilities and will acknowledge researchers who report valid
security issues.
Thank you for helping keep Universal Airgapper and its users secure!
