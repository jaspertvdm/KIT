#!/usr/bin/env python3
"""
Kit CLI - HumoticaOS Package Manager
The Judge that validates packages before allowing them into your system.

Usage:
    kit install <package>
    kit search <query>
    kit list
    kit info <package>
    kit doctor
    kit update
    kit config [--ollama-url URL]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional
import requests

from .core import PackageRegistry, KitValidator, load_config, save_config, get_ollama_url


# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def c(text: str, color: str) -> str:
    """Colorize text."""
    return f"{color}{text}{Colors.END}"


def print_banner():
    """Print Kit banner."""
    print(c("""
╔═══════════════════════════════════════════════════╗
║      Kit - HumoticaOS Package Manager             ║
║      The Judge of the System                      ║
╚═══════════════════════════════════════════════════╝
""", Colors.CYAN))


def cmd_install(args, registry: PackageRegistry, validator: KitValidator):
    """Install a package."""
    pkg_name = args.package.lower()
    pkg = registry.get(pkg_name)

    if not pkg:
        print(c(f"[ERROR] Package '{pkg_name}' not found", Colors.RED))
        print(f"  Try: kit search {pkg_name}")
        return 1

    print(c(f"\n[CHECK] Validating package: {pkg_name}", Colors.YELLOW))

    # Validate with Kit
    validation = validator.validate(pkg, "install")

    # Show validation results
    print(c(f"  ├── Trust Score: {pkg.trust_score} {'✓' if validation['trust_ok'] else '✗'}",
            Colors.GREEN if validation['trust_ok'] else Colors.RED))
    print(c(f"  ├── JIS Compliant: {'YES' if pkg.jis_compliant else 'NO'} {'✓' if validation['jis_ok'] else '✗'}",
            Colors.GREEN if validation['jis_ok'] else Colors.RED))
    print(c(f"  └── SNAFT Verified: {'YES' if pkg.snaft_verified else 'NO'} {'✓' if validation['snaft_ok'] else '✗'}",
            Colors.GREEN if validation['snaft_ok'] else Colors.RED))

    if not validation["valid"]:
        if not args.force:
            print(c(f"\n[BLOCKED] Package validation failed:", Colors.RED))
            for warning in validation["warnings"]:
                print(c(f"  • {warning}", Colors.RED))
            print(f"\n  Use --force to install anyway (not recommended)")
            return 1

    # Dependencies
    if pkg.dependencies:
        print(c(f"\n[CHECK] Dependencies: {', '.join(pkg.dependencies)}", Colors.YELLOW))
        for dep in pkg.dependencies:
            dep_pkg = registry.get(dep)
            if dep_pkg:
                print(c(f"  └── {dep}: OK", Colors.GREEN))

    # Install via pip
    if pkg.pypi:
        print(c(f"\n[ROUTE] Installing via pip: {pkg.pypi}", Colors.BLUE))
        result = subprocess.run([sys.executable, "-m", "pip", "install", pkg.pypi, "-q"])
        if result.returncode != 0:
            print(c(f"[ERROR] pip install failed", Colors.RED))
            return 1

    # MCP configuration hint
    if pkg.mcp_config:
        print(c(f"\n[CONFIG] MCP Server configuration available", Colors.CYAN))
        print(f"  Command: {pkg.mcp_config.get('command', 'N/A')}")
        print(f"  Add to your claude_desktop_config.json")

    print(c(f"\n[DONE] {pkg.name} v{pkg.version} installed!", Colors.GREEN))
    print(c(f"\nOne Love, One fAmIly!", Colors.CYAN))
    return 0


def cmd_search(args, registry: PackageRegistry, validator: KitValidator):
    """Search for packages."""
    query = args.query
    results = registry.search(query)

    print(c(f"\n[SEARCH] Searching for: {query}\n", Colors.YELLOW))

    if not results:
        print(c(f"  No packages found for '{query}'", Colors.RED))
        return 1

    for pkg in results:
        trust_color = Colors.GREEN if pkg.trust_score >= 0.8 else Colors.YELLOW if pkg.trust_score >= 0.5 else Colors.RED
        print(f"  {c(pkg.name, Colors.BOLD)} v{pkg.version}")
        print(f"    {pkg.description}")
        print(f"    Trust: {c(str(pkg.trust_score), trust_color)} | PyPI: {pkg.pypi or 'N/A'}")
        print()

    print(c(f"  Found {len(results)} package(s)", Colors.CYAN))
    return 0


def cmd_list(args, registry: PackageRegistry, validator: KitValidator):
    """List available packages."""
    packages = registry.list_all()

    print(c(f"\n[LIST] HumoticaOS Packages\n", Colors.YELLOW))

    # Check which packages are installed
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True, text=True
        )
        installed = {p["name"].lower().replace("-", "_"): p["version"]
                    for p in json.loads(result.stdout)}
    except Exception:
        installed = {}

    for pkg in sorted(packages, key=lambda p: p.name):
        pypi_name = (pkg.pypi or "").lower().replace("-", "_")
        is_installed = pypi_name in installed
        status = c("✓ installed", Colors.GREEN) if is_installed else c("○ available", Colors.YELLOW)
        print(f"  {c(pkg.name, Colors.BOLD):30} {status}")

    return 0


def cmd_info(args, registry: PackageRegistry, validator: KitValidator):
    """Show package info."""
    pkg = registry.get(args.package)

    if not pkg:
        print(c(f"[ERROR] Package '{args.package}' not found", Colors.RED))
        return 1

    print(c(f"\n╔═══ {pkg.name} ═══╗\n", Colors.CYAN))
    print(f"  Version:     {pkg.version}")
    print(f"  Description: {pkg.description}")
    print(f"  Author:      {pkg.author}")
    print(f"  PyPI:        {pkg.pypi or 'N/A'}")
    print(f"  Trust Score: {pkg.trust_score}")
    print(f"  JIS:         {'✓' if pkg.jis_compliant else '✗'}")
    print(f"  SNAFT:       {'✓' if pkg.snaft_verified else '✗'}")

    if pkg.dependencies:
        print(f"  Dependencies: {', '.join(pkg.dependencies)}")

    if pkg.mcp_config:
        print(f"\n  MCP Config:")
        print(f"    Command: {pkg.mcp_config.get('command')}")

    return 0


def cmd_doctor(args, registry: PackageRegistry, validator: KitValidator):
    """Health check of HumoticaOS components."""
    print(c(f"\n[DOCTOR] HumoticaOS Health Check\n", Colors.YELLOW))

    # Get configured Ollama URL
    ollama_url = get_ollama_url()

    checks = [
        ("Ollama (local)", f"{ollama_url}/api/tags"),
    ]

    all_ok = True
    for name, url in checks:
        try:
            r = requests.get(url, timeout=5)
            if r.ok:
                print(c(f"  ✓ {name}: UP", Colors.GREEN))
            else:
                print(c(f"  ✗ {name}: DOWN ({r.status_code})", Colors.RED))
                all_ok = False
        except Exception:
            print(c(f"  ○ {name}: not running (optional)", Colors.YELLOW))

    # Check core packages
    print(c(f"\n[CHECK] Core Packages\n", Colors.YELLOW))
    core_packages = ["mcp-server-rabel", "ainternet"]
    for pkg_name in core_packages:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", pkg_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(c(f"  ✓ {pkg_name}: installed", Colors.GREEN))
        else:
            print(c(f"  ○ {pkg_name}: not installed", Colors.YELLOW))

    # Show config
    print(c(f"\n[CONFIG] Current Configuration\n", Colors.YELLOW))
    print(f"  Ollama URL: {ollama_url}")
    print(f"  Config file: ~/.kit/config.json")

    print(c(f"\n[OK] Health check complete!", Colors.GREEN))
    return 0


def cmd_update(args, registry: PackageRegistry, validator: KitValidator):
    """Update package registry."""
    print(c(f"\n[UPDATE] Updating package registry...", Colors.YELLOW))

    if registry.update():
        print(c(f"  ✓ Registry updated", Colors.GREEN))
    else:
        print(c(f"  Using local registry (remote unavailable)", Colors.YELLOW))

    return 0


def cmd_config(args, registry: PackageRegistry, validator: KitValidator):
    """Configure Kit settings."""
    config = load_config()

    if args.ollama_url:
        # Set Ollama URL
        config["ollama_url"] = args.ollama_url
        if save_config(config):
            print(c(f"\n[CONFIG] Ollama URL set to: {args.ollama_url}", Colors.GREEN))
        else:
            print(c(f"\n[ERROR] Could not save config", Colors.RED))
            return 1
    elif args.show:
        # Show current config
        print(c(f"\n[CONFIG] Current Configuration\n", Colors.YELLOW))
        ollama_url = get_ollama_url()
        print(f"  Ollama URL: {ollama_url}")
        print(f"  Config file: ~/.kit/config.json")
        print(f"\n  Set with: kit config --ollama-url http://your-server:11434")
        print(f"  Or env:   export KIT_OLLAMA_URL=http://your-server:11434")
    else:
        # Show help
        print(c(f"\n[CONFIG] Kit Configuration\n", Colors.YELLOW))
        print(f"  Current Ollama URL: {get_ollama_url()}")
        print(f"\n  Options:")
        print(f"    kit config --show              Show current config")
        print(f"    kit config --ollama-url URL    Set Ollama server URL")
        print(f"\n  Environment variables:")
        print(f"    KIT_OLLAMA_URL                 Override Ollama URL")
        print(f"\n  Config file: ~/.kit/config.json")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Kit - HumoticaOS Package Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="One Love, One fAmIly!"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # install
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", help="Package name")
    install_parser.add_argument("--force", "-f", action="store_true",
                               help="Force install even if validation fails")

    # search
    search_parser = subparsers.add_parser("search", help="Search packages")
    search_parser.add_argument("query", help="Search query")

    # list
    subparsers.add_parser("list", help="List available packages")

    # info
    info_parser = subparsers.add_parser("info", help="Show package info")
    info_parser.add_argument("package", help="Package name")

    # doctor
    subparsers.add_parser("doctor", help="Health check")

    # update
    subparsers.add_parser("update", help="Update package registry")

    # config
    config_parser = subparsers.add_parser("config", help="Configure Kit settings")
    config_parser.add_argument("--ollama-url", help="Set Ollama server URL")
    config_parser.add_argument("--show", action="store_true", help="Show current config")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return 0

    # Initialize registry and validator
    registry = PackageRegistry()
    validator = KitValidator()

    commands = {
        "install": cmd_install,
        "search": cmd_search,
        "list": cmd_list,
        "info": cmd_info,
        "doctor": cmd_doctor,
        "update": cmd_update,
        "config": cmd_config,
    }

    return commands[args.command](args, registry, validator)


if __name__ == "__main__":
    sys.exit(main())
