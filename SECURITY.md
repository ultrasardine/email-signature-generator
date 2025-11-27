# Security Policy

## Supported Versions

We take security seriously and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

**Note**: As the project is currently in early development (0.1.x), we support only the latest release. Once we reach version 1.0.0, we will support the current major version and the previous major version.

## Reporting a Vulnerability

We appreciate your efforts to responsibly disclose security vulnerabilities. If you discover a security issue in the Email Signature Generator, please follow these steps:

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **Opening a GitHub Security Advisory** (preferred):
   - Go to the [Security tab](https://github.com/ultrasardine/email-signature-generator/security/advisories) of the repository
   - Click "Report a vulnerability"
   - Fill out the advisory form with details about the vulnerability

2. **Contacting the maintainers directly**:
   - Open a private issue in the GitHub repository and mention that it's security-related
   - Contact the project maintainer: [@ultrasardine](https://github.com/ultrasardine)

### What to Include

When reporting a vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: What an attacker could potentially do with this vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions of the software are affected
- **Proof of Concept**: If possible, include a proof of concept (code, screenshots, etc.)
- **Suggested Fix**: If you have ideas on how to fix the issue, please share them

### Response Timeline

We are committed to responding to security reports promptly:

- **Initial Response**: Within **48 hours** of receiving your report, we will acknowledge receipt and provide an initial assessment
- **Status Updates**: We will provide regular updates (at least every 5 business days) on our progress
- **Resolution Timeline**: We aim to resolve critical vulnerabilities within **7 days** and other vulnerabilities within **30 days**
- **Disclosure**: Once a fix is available, we will coordinate with you on the disclosure timeline

### What to Expect

After you submit a vulnerability report:

1. **Acknowledgment**: We will confirm receipt of your report within 48 hours
2. **Investigation**: We will investigate the issue and determine its severity and impact
3. **Communication**: We will keep you informed of our progress and may ask for additional information
4. **Fix Development**: We will develop and test a fix for the vulnerability
5. **Release**: We will release a security update and publish a security advisory
6. **Credit**: With your permission, we will credit you in the security advisory and release notes

## Security Update Process

When a security vulnerability is confirmed:

1. **Patch Development**: We develop a fix in a private repository or branch
2. **Testing**: The fix is thoroughly tested to ensure it resolves the issue without introducing new problems
3. **Release**: A new version is released with the security fix
4. **Advisory**: A security advisory is published on GitHub with details about the vulnerability and the fix
5. **Notification**: Users are notified through GitHub releases and the CHANGELOG

## Disclosure Policy

We follow a **coordinated disclosure** approach:

- **Private Disclosure**: Security issues are handled privately until a fix is available
- **Coordinated Release**: We coordinate with the reporter on the disclosure timeline
- **Public Disclosure**: Once a fix is released, we publish a security advisory with:
  - Description of the vulnerability
  - Affected versions
  - Fixed versions
  - Mitigation steps (if any)
  - Credit to the reporter (with permission)

**Typical Disclosure Timeline**:
- Day 0: Vulnerability reported
- Day 1-2: Initial response and acknowledgment
- Day 3-7: Investigation and fix development
- Day 7-30: Testing and release preparation
- Day 30+: Public disclosure with security advisory

We may adjust this timeline based on the severity and complexity of the issue.

## Security Best Practices

When using the Email Signature Generator, we recommend:

### For Users

- **Keep Updated**: Always use the latest version to benefit from security fixes
- **Verify Downloads**: Download binaries only from official GitHub releases
- **Check Signatures**: Verify file integrity when possible
- **Review Permissions**: Be aware of file system permissions when running the application
- **Protect Profiles**: Profile files may contain personal information; store them securely

### For Developers

- **Dependencies**: Keep dependencies up to date to avoid known vulnerabilities
- **Code Review**: Review code changes carefully, especially those handling user input
- **Input Validation**: Always validate and sanitize user input
- **Secure Defaults**: Use secure defaults in configuration
- **Testing**: Include security considerations in testing (property-based tests help catch edge cases)

## Known Security Considerations

### Current Security Posture

The Email Signature Generator is a desktop application that:

- **Runs Locally**: Does not transmit data over the network
- **File System Access**: Reads configuration files and writes output images
- **User Input**: Processes user-provided text and image files
- **No Authentication**: Does not require or store credentials
- **No External APIs**: Does not communicate with external services

### Potential Security Concerns

While the application is designed to be safe, users should be aware of:

1. **File System Access**: The application can read and write files in the directories it has access to
2. **Image Processing**: Processing malformed image files could potentially cause issues (we use Pillow, which is regularly updated for security)
3. **Configuration Files**: YAML configuration files are parsed; malformed files could cause errors
4. **Profile Files**: Profile JSON files contain personal information and should be protected

## Security Tools and Practices

We use the following tools and practices to maintain security:

- **Dependency Scanning**: Regular updates to dependencies to address known vulnerabilities
- **Code Quality**: Static analysis with ruff and mypy to catch potential issues
- **Testing**: Comprehensive test suite including property-based tests to catch edge cases
- **Code Review**: All changes are reviewed before merging
- **Minimal Dependencies**: We keep dependencies minimal to reduce attack surface

## Contact

For security-related questions or concerns:

- **Security Issues**: Use GitHub Security Advisories (preferred) or contact maintainers privately
- **General Questions**: Open a regular GitHub issue or discussion
- **Project Maintainer**: [@ultrasardine](https://github.com/ultrasardine)

## Acknowledgments

We appreciate the security research community and will acknowledge researchers who responsibly disclose vulnerabilities (with their permission) in:

- Security advisories
- Release notes
- This SECURITY.md file

Thank you for helping keep the Email Signature Generator and its users safe!
