"""
Kit Core - Package Registry and Validation

Kit = The Judge
JIS = The Law
SNAFT = The Police
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import requests


# Configuration
CONFIG_DIR = Path.home() / ".kit"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    """Load Kit configuration from ~/.kit/config.json"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}


def save_config(config: Dict[str, Any]) -> bool:
    """Save Kit configuration to ~/.kit/config.json"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
        return True
    except Exception:
        return False


def get_ollama_url() -> str:
    """
    Get Ollama API URL from (in order of priority):
    1. Environment variable: KIT_OLLAMA_URL
    2. Config file: ~/.kit/config.json -> ollama_url
    3. Default: http://localhost:11434
    """
    # 1. Environment variable
    env_url = os.environ.get("KIT_OLLAMA_URL")
    if env_url:
        return env_url

    # 2. Config file
    config = load_config()
    if "ollama_url" in config:
        return config["ollama_url"]

    # 3. Default (localhost - works if user has Ollama installed)
    return "http://localhost:11434"


@dataclass
class Package:
    """A HumoticaOS package."""
    name: str
    version: str
    description: str
    trust_score: float
    jis_compliant: bool
    snaft_verified: bool
    pypi: Optional[str] = None
    npm: Optional[str] = None
    dependencies: List[str] = None
    mcp_config: Optional[Dict] = None
    author: str = "Unknown"

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    @property
    def is_trusted(self) -> bool:
        """Check if package meets minimum trust requirements."""
        return (
            self.trust_score >= 0.5 and
            self.jis_compliant and
            self.snaft_verified
        )


class PackageRegistry:
    """HumoticaOS Package Registry."""

    REGISTRY_URL = "https://humotica.com/packages/packages.json"

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or self._default_registry_path()
        self._packages: Dict[str, Package] = {}
        self._load()

    def _default_registry_path(self) -> Path:
        """Get default registry path."""
        locations = [
            Path(__file__).parent / "packages.json",
            Path.home() / ".kit" / "packages.json",
        ]
        for loc in locations:
            if loc.exists():
                return loc
        return locations[0]

    def _load(self):
        """Load packages from registry file."""
        if not self.registry_path.exists():
            self._packages = {}
            return

        try:
            data = json.loads(self.registry_path.read_text())
            for name, pkg_data in data.get("packages", {}).items():
                self._packages[name] = Package(
                    name=pkg_data.get("name", name),
                    version=pkg_data.get("version", "0.0.0"),
                    description=pkg_data.get("description", ""),
                    trust_score=pkg_data.get("trust_score", 0),
                    jis_compliant=pkg_data.get("jis_compliant", False),
                    snaft_verified=pkg_data.get("snaft_verified", False),
                    pypi=pkg_data.get("pypi"),
                    npm=pkg_data.get("npm"),
                    dependencies=pkg_data.get("dependencies", []),
                    mcp_config=pkg_data.get("mcp_config"),
                    author=pkg_data.get("author", "Unknown"),
                )
        except Exception as e:
            print(f"Warning: Could not load registry: {e}")
            self._packages = {}

    def get(self, name: str) -> Optional[Package]:
        """Get a package by name."""
        return self._packages.get(name.lower())

    def search(self, query: str) -> List[Package]:
        """Search packages by name or description."""
        query = query.lower()
        results = []
        for name, pkg in self._packages.items():
            if (query in name.lower() or
                query in pkg.description.lower() or
                query in pkg.name.lower()):
                results.append(pkg)
        return results

    def list_all(self) -> List[Package]:
        """List all packages."""
        return list(self._packages.values())

    def update(self) -> bool:
        """Update registry from remote."""
        try:
            response = requests.get(self.REGISTRY_URL, timeout=10)
            if response.ok:
                self.registry_path.parent.mkdir(parents=True, exist_ok=True)
                self.registry_path.write_text(response.text)
                self._load()
                return True
        except Exception:
            pass
        return False


class KitValidator:
    """Kit AI Security Validator.

    Connects to Ollama for AI-powered validation.

    Configuration (in priority order):
    1. Constructor argument: kit_api
    2. Environment variable: KIT_OLLAMA_URL
    3. Config file: ~/.kit/config.json -> ollama_url
    4. Default: http://localhost:11434

    Example:
        # Use local Ollama
        validator = KitValidator()

        # Use remote Ollama
        validator = KitValidator(kit_api="http://192.168.1.100:11434/api/generate")

        # Or set environment variable
        # export KIT_OLLAMA_URL=http://myserver:11434
        validator = KitValidator()
    """

    def __init__(self, kit_api: Optional[str] = None):
        if kit_api:
            self.kit_api = kit_api
        else:
            base_url = get_ollama_url()
            self.kit_api = f"{base_url}/api/generate"

    def validate(self, package: Package, action: str = "install") -> Dict[str, Any]:
        """
        Validate a package using Kit AI.

        Returns validation result with:
        - valid: bool
        - trust_ok: bool
        - jis_ok: bool
        - snaft_ok: bool
        - ai_response: str (if Kit AI available)
        """
        result = {
            "valid": True,
            "trust_ok": package.trust_score >= 0.5,
            "jis_ok": package.jis_compliant,
            "snaft_ok": package.snaft_verified,
            "ai_response": None,
            "warnings": [],
        }

        # Check trust score
        if not result["trust_ok"]:
            result["valid"] = False
            result["warnings"].append(f"Trust score {package.trust_score} below minimum 0.5")

        # Check JIS compliance
        if not result["jis_ok"]:
            result["valid"] = False
            result["warnings"].append("Package is not JIS compliant")

        # Check SNAFT verification
        if not result["snaft_ok"]:
            result["valid"] = False
            result["warnings"].append("Package is not SNAFT verified")

        # Try Kit AI validation (optional - works without it)
        try:
            response = requests.post(
                self.kit_api,
                json={
                    "model": "kit",
                    "prompt": f"[CHECK] {action} {package.name}",
                    "stream": False,
                    "options": {"num_predict": 100}
                },
                timeout=10
            )
            if response.ok:
                result["ai_response"] = response.json().get("response", "")
        except Exception:
            result["ai_response"] = "Kit AI offline, using local validation"

        return result

    def check_injection(self, text: str) -> Dict[str, Any]:
        """Check text for prompt injection attempts."""
        try:
            response = requests.post(
                self.kit_api,
                json={
                    "model": "kit",
                    "prompt": f"[CHECK] {text}",
                    "stream": False,
                    "options": {"num_predict": 50}
                },
                timeout=10
            )
            if response.ok:
                return {
                    "checked": True,
                    "response": response.json().get("response", "")
                }
        except Exception:
            pass

        return {"checked": False, "response": "Kit AI unavailable"}
