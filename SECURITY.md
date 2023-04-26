# Security Policy for UpTrain Repository

## Reporting a Vulnerability

If you discover a security vulnerability in the UpTrain repository, please send an email to [tech AT uptrain.ai] with a detailed description of the issue. We appreciate your help in identifying and resolving any security risks.

## Supported Versions

We're committed to providing security updates for the following versions of the project:

| Version | Supported          |
| ------- | ------------------ |
| >1.0.x   | :white_check_mark: |
| <0.9.x   | :x:                |

## Security Best Practices

### Access Control

- Limit repository access to only necessary collaborators.
- Enforce two-factor authentication (2FA) for all collaborators.
- Assign appropriate roles (admin, write, read) to collaborators based on their responsibilities.

### Code Review

- Require mandatory code reviews before merging any pull request.
- Use branch protection rules to prevent direct pushes to the main branch.
- Ensure that only trusted collaborators can approve pull requests.

### Dependency Management

- Regularly update dependencies to the latest, stable, and secure versions.
- Use tools like Dependabot to automatically detect and update vulnerable dependencies.

### Security Testing

- Integrate security testing into your CI/CD pipeline to detect vulnerabilities early in the development process.
- Use tools like Snyk, OWASP ZAP, or other open-source security scanners.

## Incident Response

In case of a security breach or vulnerability exploitation, we will:

1. Investigate the incident and determine its scope and impact.
2. Notify affected users and provide guidance on necessary actions.
3. Implement fixes or mitigations to address the vulnerability.
4. Review and update security practices to prevent similar incidents in the future.

