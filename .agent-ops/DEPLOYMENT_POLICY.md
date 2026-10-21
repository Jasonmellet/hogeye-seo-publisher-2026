## Deployment policy

- Work on a branch; do not commit directly to the default branch.
- Open a pull request for every production-affecting change.
- Wait for all required CI checks to pass before merging.
- Deploy only from the protected default branch through the configured provider.
- Do not run direct production deploy commands from an agent shell.
- If a provider deploy is needed, update the repository workflow or provider
  configuration through a reviewed pull request.

The repository ruleset and provider settings enforce this policy. This file
documents the policy for agents; it is not a substitute for enforcement.
