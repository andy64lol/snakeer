# 🐍 Snakeer

A Node.js-style package manager for Python with zero configuration required.

## Architecture

Snakeer uses a **serverless-first, zero-config architecture**:

```
┌─────────────┐      HTTP API       ┌─────────────────┐
│   Python    │ ──────────────────> │  Serverless     │
│   Client    │                     │  Functions      │
│  (snakeer)  │ <────────────────── │ (Netlify/Vercel)│
└─────────────┘                     └────────┬────────┘
      │                                    │
      │ No env vars needed                 │ GITHUB_TOKEN
      │                                    v
      │                           ┌──────────────┐
      │                           │  GitHub      │
      │                           │  Repository  │
      │                           │ Package Store│
      │                           └──────────────┘
      │
      ▼
Automatic fallback:
- Primary: https://snakeer.vercel.app/
- Fallback: https://snakeer-package-api.netlify.app/functions/
```

**Key Design**: 
- **Zero configuration** - No environment variables needed on client
- **Automatic fallback** - If Vercel fails, automatically tries Netlify
- **Secure** - GITHUB_TOKEN only exists in serverless environment

## Features

- 📦 **Node.js-style package management** - Familiar commands like `install`, `add`, `remove`, `update`
- 🔒 **Lock file support** - Exact version tracking in `project_packages.json`
- 🚀 **Zero configuration** - Works out of the box, no setup needed
- 🔄 **Automatic failover** - Vercel primary, Netlify backup
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

**No configuration needed!** Just use it:

```bash
# Install all dependencies from project_packages.json
snakeer install

# Add a dependency
snakeer add coolpkg@1.0.0
snakeer add utilpkg@^2.0.0

# List installed packages
snakeer list

# Publish your package
snakeer publish
```

**Use in your code:**
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

## How It Works

### Automatic API Selection
The client automatically tries APIs in this order:
1. **Primary**: `https://snakeer.vercel.app/api/`
2. **Fallback**: `https://snakeer-package-api.netlify.app/functions/`

If the primary API fails, it automatically falls back to the secondary.

### Serverless Functions
All GitHub API interactions happen in serverless functions:

| Function | Vercel URL | Netlify URL |
|----------|-----------|-------------|
| Download | `/api/download` | `/functions/download.js` |
| Upload | `/api/upload` | `/functions/upload.js` |

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

## Version Specifiers

- `1.0.0` - Exact version
- `>=1.0.0` - Greater than or equal
- `^1.0.0` - Compatible with (same major version)
- `~1.0.0` - Approximately equivalent (same major.minor)
- `latest` - Latest available version

## Serverless Deployment (For Maintainers)

If you're maintaining the Snakeer registry:

### Netlify
- Deploy `functions/` directory
- Set `GITHUB_TOKEN` in environment variables
- URL: `https://snakeer-package-api.netlify.app/functions/`

### Vercel
- Deploy `api/` directory
- Set `GITHUB_TOKEN` in environment variables
- URL: `https://snakeer.vercel.app/api/`

### Required Serverless Environment Variables
- `GITHUB_TOKEN` - GitHub personal access token with repo access (server-side only!)

## Development

```bash
# Run the demo
python main.py

# Run CLI commands
python -m snakeer install
python -m snakeer add coolpkg@1.0.0
```

## Security

- ✅ **No client-side credentials** - Users don't need any tokens
- ✅ **Automatic failover** - Works even if one service is down
- ✅ **Server-side only tokens** - GITHUB_TOKEN never exposed to clients

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

---

Made with 🐍 by andy64lol
