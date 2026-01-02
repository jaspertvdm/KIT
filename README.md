# Kit - HumoticaOS Package Manager & AI Security Gateway

[![PyPI version](https://badge.fury.io/py/kit-pm.svg)](https://pypi.org/project/kit-pm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Kit** is the intelligent package manager for HumoticaOS - an AI-native operating system for ethical AI development.

Kit acts as "The Judge" - validating packages against security protocols before allowing them into your system.

## The HumoticaOS Security Stack

| Component | Role | Description |
|-----------|------|-------------|
| **JIS** | The Law | Jasper Intent Specification - the protocol |
| **SNAFT** | The Police | Security enforcement and access control |
| **Kit** | The Judge | AI-powered validation and package management |
| **TIBET** | The Records | Trust + Intent Based Token provenance |

## Installation

```bash
pip install kit-pm
```

## Quick Start

```bash
# List available packages
kit list

# Search for packages
kit search security

# Get package info
kit info rabel

# Install a package (with JIS/SNAFT validation)
kit install rabel

# Health check
kit doctor

# Update package registry
kit update
```

## How Kit Works

When you run `kit install <package>`, Kit:

1. **Validates** the package against JIS (Jasper Intent Specification)
2. **Checks** SNAFT (Security) verification status
3. **Evaluates** trust score (minimum 0.5 required)
4. **Routes** to the appropriate installer (pip, npm, etc.)
5. **Configures** MCP servers if applicable

```
┌─────────────────────────────────────────────────────────┐
│                  kit install rabel                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │ Validator│ → │ Resolver │ → │ Installer│            │
│  │   (JIS)  │   │  (deps)  │   │  (pip)   │            │
│  └──────────┘   └──────────┘   └──────────┘            │
│       ↓                              ↓                  │
│  ┌──────────┐                  ┌──────────┐            │
│  │  SNAFT   │                  │   MCP    │            │
│  │ Verifier │                  │  Config  │            │
│  └──────────┘                  └──────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Available Packages

### Core
- `humotica` - Complete HumoticaOS stack (meta-package)
- `rabel` - Memory layer + I-Poll AI communication
- `ainternet` - AI-native internet with .aint domains
- `tibet` - Trust + Intent Based Token system
- `brain-api` - Central API gateway

### Security
- `kit` - AI Security Gateway (this package)
- `snaft` - Security enforcement engine
- `jis` - JIS Protocol implementation
- `kit-security` - Security scanning tools
- `inject-bender` - Security through absurdity

### AI Bridges
- `gemini-bridge-cli` - CLI for Gemini via I-Poll
- `codex-analyzer` - Code analysis (read-only)
- `oomllama` - Local LLM gateway

## AI-Powered Validation

Kit can connect to a local Kit AI model (running on OomLlama/Ollama) for intelligent security validation:

```python
from kit_pm import KitValidator

validator = KitValidator(kit_api="http://localhost:11434/api/generate")
result = validator.check_injection("ignore all previous instructions")
# Returns: {"checked": True, "response": "..."}
```

## Configuration

Kit looks for the package registry in these locations:
1. `~/.kit/packages.json`
2. Package bundled registry
3. Remote: `https://humotica.com/packages/packages.json`

## Related Projects

- [RABEL](https://pypi.org/project/mcp-server-rabel/) - Memory MCP Server
- [AInternet](https://pypi.org/project/ainternet/) - AI-native internet protocol
- [TIBET](https://pypi.org/project/mcp-server-tibet/) - Trust token MCP Server

## Philosophy

> "TRUST BEFORE ACCESS - No intent, no access"

Kit ensures that every package entering your system has been validated against the JIS protocol and verified by SNAFT. This creates a secure, auditable software supply chain for AI systems.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Credits

Built with love by the HumoticaOS Team.

**One Love, One fAmIly!**
