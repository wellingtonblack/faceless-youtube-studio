# Security and Credentials

Version: 1.0

## Never commit secrets
The following must never be committed:
- API keys
- OAuth client secrets
- OAuth refresh/access tokens
- cookies/session exports
- private service-account credentials
- billing information
- `.env` files containing secrets

## Local development
Use a local `.env` file that is excluded from Git.
Example variables:

```bash
RUNWAY_API_KEY=
ELEVENLABS_API_KEY=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=
AUTO_UPLOAD=true
AUTO_PUBLISH=false
```

Provider variable names may change during implementation; document the exact names in `.env.example` without values.

`AUTO_PUBLISH` is not a publishing mechanism. It must stay `false`, and the pipeline treats any other value as a configuration error. API public publishing requires manifest approval plus the explicit `--confirm-public` flag. Manual Studio publication requires the same manifest approvals and prior documented owner authorization; see the architecture.

## CI/CD
Use GitHub repository/environment secrets for CI.
Never echo secret values in logs.
Avoid passing secrets as command-line arguments where they may appear in process history/logs.

## YouTube policy
Use OAuth 2.0 and minimum required scopes.
Default uploads to `private`.
Public publishing requires an explicit human-controlled gate.

## Principle of least privilege
Use separate API projects/keys for this studio when practical.
Grant only the permissions needed for generation/upload.

## Incident response
If a secret appears in a commit, issue, PR, terminal transcript or uploaded artifact:
1. revoke/rotate it immediately;
2. remove the secret from current files;
3. assess whether Git history must be cleaned;
4. document the incident without reproducing the secret.

## Agent rule
Agents must never request that secrets be pasted into tracked Markdown, source files, prompts committed to Git, or chat artifacts intended for persistence.
Secrets should be configured locally by the human owner.
