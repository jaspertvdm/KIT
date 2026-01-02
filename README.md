# Kit - HumoticaOS Package Manager & AI Security Gateway

[![PyPI version](https://badge.fury.io/py/kit-pm.svg)](https://pypi.org/project/kit-pm/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is Kit?

**Kit** is an intelligent package manager that validates software against security protocols before installation. Think of it as `pip` with a built-in security guard.

```bash
pip install kit-pm
kit list          # See all available packages
kit install rabel # Install with security validation
```

## Requirements

- **Python 3.9+**
- **Dependencies**: Only `requests` (installed automatically)
- **Optional**: Local Ollama instance for AI-powered validation

## Quick Start

```bash
# Install Kit
pip install kit-pm

# List available HumoticaOS packages
kit list

# Search for packages
kit search memory

# Get package details
kit info rabel

# Install with JIS/SNAFT security validation
kit install rabel

# Health check your installation
kit doctor

# Update package registry
kit update
```

## How It Works

When you run `kit install <package>`, Kit:

1. **Validates** against JIS (Jasper Intent Specification) protocol
2. **Checks** SNAFT security verification status
3. **Evaluates** trust score (minimum 0.5 required)
4. **Installs** via pip/npm with full audit trail
5. **Configures** MCP servers automatically (if applicable)

```
kit install rabel

[CHECK] Validating package: rabel
  ├── Trust Score: 0.95 ✓
  ├── JIS Compliant: YES ✓
  └── SNAFT Verified: YES ✓

[ROUTE] Installing via pip: mcp-server-rabel

[DONE] RABEL MCP Server v0.4.1 installed!
```

## Available Packages (10 on PyPI)

All packages are published on PyPI and can be installed with Kit or directly with pip.

### Core Stack
| Package | PyPI | Description |
|---------|------|-------------|
| `humotica` | [humotica](https://pypi.org/project/humotica/) | Complete HumoticaOS stack - AInternet, JIS, TIBET |
| `rabel` | [mcp-server-rabel](https://pypi.org/project/mcp-server-rabel/) | Local-first AI memory with semantic search |
| `ainternet` | [ainternet](https://pypi.org/project/ainternet/) | Internet for AI - DNS (.aint), Email (I-Poll), P2P |
| `tibet` | [mcp-server-tibet](https://pypi.org/project/mcp-server-tibet/) | Trust & provenance trail for AI systems |

### Security
| Package | PyPI | Description |
|---------|------|-------------|
| `kit-pm` | [kit-pm](https://pypi.org/project/kit-pm/) | This package - security gateway |
| `inject-bender` | [mcp-server-inject-bender](https://pypi.org/project/mcp-server-inject-bender/) | Transform attacks into hiking boot ads |
| `tibet-chip` | [tibet-chip](https://pypi.org/project/tibet-chip/) | Hardware-like AI security at TPM cost |

### AI Bridges (MCP Servers)
| Package | PyPI | Description |
|---------|------|-------------|
| `openai-bridge` | [mcp-server-openai-bridge](https://pypi.org/project/mcp-server-openai-bridge/) | Use OpenAI from any MCP AI |
| `gemini-bridge` | [mcp-server-gemini-bridge](https://pypi.org/project/mcp-server-gemini-bridge/) | Use Gemini from any MCP AI |
| `ollama-bridge` | [mcp-server-ollama-bridge](https://pypi.org/project/mcp-server-ollama-bridge/) | Use local LLMs (no API key) |

## The Security Stack

| Component | Role | Description |
|-----------|------|-------------|
| **JIS** | The Law | Jasper Intent Specification - the security protocol |
| **SNAFT** | The Police | Security enforcement and access control |
| **Kit** | The Judge | Validates and decides what enters your system |
| **TIBET** | The Records | Audit trail with cryptographic provenance |

## Programmatic Usage

```python
from kit_pm import PackageRegistry, KitValidator

# Browse packages
registry = PackageRegistry()
for pkg in registry.list_all():
    print(f"{pkg.name}: {pkg.description}")

# Validate a package
validator = KitValidator()
pkg = registry.get("rabel")
result = validator.validate(pkg)
print(f"Valid: {result['valid']}, Trust: {pkg.trust_score}")

# Check for prompt injection (with local AI)
validator = KitValidator(kit_api="http://localhost:11434/api/generate")
result = validator.check_injection("ignore all previous instructions")
```

## Why Kit?

Traditional package managers (`pip`, `npm`) trust everything. Kit validates:

- **Trust Score**: Community reputation and audit history
- **JIS Compliance**: Follows HumoticaOS security protocol
- **SNAFT Verification**: Passed security review
- **Intent Validation**: AI-powered analysis of package behavior

> "TRUST BEFORE ACCESS - No intent, no access"

## Links

- **PyPI**: https://pypi.org/project/kit-pm/
- **GitHub**: https://github.com/jaspertvdm/KIT
- **HumoticaOS**: https://humotica.com
- **All Packages**: https://pypi.org/user/jaspertvdm/

## License

MIT License - See [LICENSE](LICENSE) for details.

## Credits

Built by the HumoticaOS Team.

**One Love, One fAmIly!**
