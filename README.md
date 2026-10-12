# All PIP Installer

<p align="center">
  <strong>A small, opt-in CLI for installing a curated set of common Python packages.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Dependencies-Standard%20Library-444444?style=for-the-badge" alt="Standard library only">
  <a href="https://github.com/kaandgnsh/all-pip-installer/actions/workflows/tests.yml">
    <img src="https://github.com/kaandgnsh/all-pip-installer/actions/workflows/tests.yml/badge.svg?branch=main" alt="GitHub Actions">
  </a>
</p>

---

## Overview

**All PIP Installer** streamlines the setup of a small, predefined collection of third-party Python packages. It uses the active Python interpreter to invoke `pip`, supports a few practical package profiles, and lets you add package names when needed.

> **Important:** This tool does not and cannot install every package on PyPI. It installs only the packages in the selected profile and any additional package names you provide. The default mode is a dry run. No installation occurs unless you pass `--install` and confirm.

## Features

- **Safe by default:** previews the selected packages without installing them.
- **Explicit confirmation:** requires `--install` and a confirmation prompt before modifying the environment.
- **Curated profiles:** choose basic, web, scraping, terminal, or all listed packages.
- **Extra package names:** add trusted PyPI package names one at a time.
- **Interpreter-aware:** runs `python -m pip` using the current interpreter.
- **No runtime dependencies:** the installer itself uses the Python standard library.
- **Tested CLI:** unit tests run in GitHub Actions on Python 3.10, 3.11, and 3.12.

## Requirements

- Python 3.10 or newer
- `pip` available for the selected Python interpreter
- Internet access to download packages

Verify your environment:

```bash
python3 --version
python3 -m pip --version
```

A virtual environment is recommended to avoid changing packages in a system-managed Python installation.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/kaandgnsh/all-pip-installer.git
cd all-pip-installer
```

List the profiles:

```bash
python3 all-pip-installer/all-pip.py --list
```

Preview the default profile. This command makes no changes:

```bash
python3 all-pip-installer/all-pip.py
```

Install a profile after reviewing the package list:

```bash
python3 all-pip-installer/all-pip.py --profile web --install
```

The installer asks for confirmation by default. To skip that prompt explicitly:

```bash
python3 all-pip-installer/all-pip.py --profile terminal --install --yes
```

## Package Profiles

| Profile | Packages |
|:--|:--|
| `basic` | `requests`, `colorama`, `rich` |
| `web` | `requests`, `beautifulsoup4` |
| `scraping` | `requests`, `beautifulsoup4`, `mechanize` |
| `terminal` | `colorama`, `pyfiglet`, `rich` |
| `all` | Every package in the curated profiles above |

Add extra package names with repeated `--package` flags:

```bash
python3 all-pip-installer/all-pip.py --profile basic --package pytest --package packaging
```

This remains a dry run. Add `--install` when you are ready to proceed. Package names are treated as plain PyPI names; URLs, shell commands, and version specifiers are not accepted.

## CLI Reference

| Option | Description |
|:--|:--|
| `--profile NAME` | Select `basic`, `web`, `scraping`, `terminal`, or `all`. Default: `basic`. |
| `--package NAME` | Add a package name. May be repeated. |
| `--list` | Print all profiles and their package lists. |
| `--install` | Proceed to the installation confirmation. Without it, the command only previews the plan. |
| `--yes` | Skip confirmation; valid only with `--install`. |
| `-h, --help` | Show help. |

## Safety Notes

- Read the package list before approving an installation.
- Install packages only from projects and maintainers you trust; third-party packages execute code in your Python environment.
- Prefer a virtual environment for project-specific dependencies.
- The script uses the active interpreter's `sys.executable -m pip`; it does not create a virtual environment or elevate privileges.
- A successful pip exit code confirms the command completed, not that every installed package is safe or suitable for your project.

## Tests

Run the unit tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The test suite checks profile selection, de-duplication, dry-run behavior, confirmation, invalid package names, and pip error handling.

## Project Structure

```text
all-pip-installer/
├── .github/
│   └── workflows/
│       └── tests.yml
├── all-pip-installer/
│   └── all-pip.py
├── tests/
│   └── test_installer.py
├── .gitignore
└── README.md
```

## Author

**Kaan DOĞAN** · [GitHub](https://github.com/kaandgnsh) · [LinkedIn](https://www.linkedin.com/in/kaan-do%C4%9Fan-911663280/) · [Instagram](https://instagram.com/kaandgn.sh)

<p align="center">
  <sub>Small automation. Explicit consent. No unnecessary installs.</sub>
</p>
