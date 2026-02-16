# 🐍 Snakeer

A Node.js-style package manager for Python. Manage your Python dependencies with a familiar, modern workflow.

## Features

- 📦 **Node.js-style package management** - Familiar commands like `install`, `add`, `remove`, `update`
- 🔒 **Lock file support** - Exact version tracking in `project_packages.json`
- 🚀 **GitHub-based registry** - Store packages in a GitHub repository
- ⚡ **Serverless functions** - Upload/download via Netlify or Vercel
- 🔄 **Semantic versioning** - Support for `>=`, `^`, `~` version specifiers
- 📁 **Flat installation** - All packages in `snakeer_modules/` (no nesting)

## Installation

```bash
# Clone the repository
git clone https://github.com/andy64lol/snakeer.git
cd snakeer

# Install the package
pip install -e .

# Or install from source
python setup.py install
```

## Quick Start

1. **Initialize your project** (creates `project_packages.json`):
```bash
snakeer install
```

2. **Add a dependency**:
```bash
snakeer add coolpkg@1.0.0
snakeer add utilpkg@^2.0.0
```

3. **Install all dependencies**:
```bash
snakeer install
```

4. **Use in your code**:
```python
from snakeer import require

coolpkg = require("coolpkg")
result = coolpkg.some_function()
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `snakeer install` | Install all dependencies from `project_packages.json` |
| `snakeer add <pkg>@<version>` | Add a new package to dependencies |
| `snakeer remove <pkg>` | Remove a package from dependencies |
| `snakeer update [pkg]` | Update packages according to version ranges |
| `snakeer list` | List installed packages |
| `snakeer publish` | Publish current package to registry |

## Project Structure

```
my_project/
├── main.py                        # Your entry point
├── project_packages.json           # Config + lock file
├── snakeer_modules/               # Installed packages
│   ├── coolpkg/
│   │   ├── index.py               # Package entry
│   │   └── metadata.json          # Package metadata
│   └── utilpkg/
└── .snakeer_cache/                # Cached downloads
```

## Configuration (`project_packages.json`)

```json
{
  "name": "my_project",
  "version": "1.0.0",
  "snakeer_dependencies": {
    "coolpkg": ">=1.0.0",
    "utilpkg": "^2.1.0"
  },
  "installed_dependencies_versions": {
    "coolpkg": "1.2.3",
    "utilpkg": "2.1.5"
  }
}
```

## Package Format

Each package in `snakeer_modules/` contains:

- `index.py` - Main module with functions/classes
- `metadata.json` - Package metadata and dependencies

Example `metadata.json`:
```json
{
  "name": "coolpkg",
  "version": "1.2.3",
  "dependencies": {
    "utilpkg": ">=2.0.0"
  }
}
```

## Serverless Deployment

### Netlify
Deploy the `functions/` directory to Netlify Functions.

### Vercel
Deploy the `api/` directory to Vercel Serverless Functions.

Required environment variable:
- `GITHUB_TOKEN` - GitHub personal access token with repo access

## Version Specifiers

- `1.0.0` - Exact version
- `>=1.0.0` - Greater than or equal
- `^1.0.0` - Compatible with (same major version)
- `~1.0.0` - Approximately equivalent (same major.minor)
- `latest` - Latest available version

## Development

```bash
# Run the demo
python main.py

# Run CLI commands
python -m snakeer install
python -m snakeer add coolpkg@1.0.0
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

---

Made with 🐍 by andy64lol
