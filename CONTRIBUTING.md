# Contributing to Forms Pro

Thanks for contributing to `forms_pro`.

## Getting Started

1. Fork the repository and create a branch from `develop`.
2. Install the app in your Bench environment.
3. Install local checks:

```bash
pre-commit install
```

## Local Checks

Run the checks relevant to your change before opening a pull request.

```bash
pre-commit run --all-files
cd frontend && yarn typecheck
bench --site <site> run-tests --app forms_pro
```

## Pull Requests

- Keep changes focused and easy to review.
- Include a short summary of what changed and why.
- Add screenshots for UI changes when helpful.
- Use a conventional PR title such as `fix: handle empty submission state`.

## Security

If you find a security issue, do not open a public issue. Follow the process in [`SECURITY.md`](SECURITY.md).
