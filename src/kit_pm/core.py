"""
Kit Core - Package Registry and Validation

Kit = De Rechter
JIS = De Wet
SNAFT = De Politie
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import requests


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
        # Check multiple locations
        locations = [
            Path(__file__).parent / "packages.json",
            Path.home() / ".kit" / "packages.json",
            Path("/srv/jtel-stack/kit-model/datasets/packages.json"),
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
    """Kit AI Security Validator."""

    DEFAULT_KIT_API = "http://192.168.4.85:11434/api/generate"

    def __init__(self, kit_api: Optional[str] = None):
        self.kit_api = kit_api or self.DEFAULT_KIT_API

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

        # Try Kit AI validation
        try:
            response = requests.post(
                self.kit_api,
                json={
                    "model": "kit",
                    "prompt": f"[CHECK] {action} {package.name}",
                    "stream": False,
                    "options": {"num_predict": 100}
                },
                timeout=30
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
                timeout=30
            )
            if response.ok:
                return {
                    "checked": True,
                    "response": response.json().get("response", "")
                }
        except Exception:
            pass

        return {"checked": False, "response": "Kit AI unavailable"}
