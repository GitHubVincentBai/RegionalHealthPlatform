from __future__ import annotations

import sys
from pathlib import Path


def _host_site_packages() -> Path:
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    return Path(sys.base_prefix) / "lib" / version / "site-packages"


host_site_packages = _host_site_packages()
if host_site_packages.is_dir():
    site_packages = str(host_site_packages)
    if site_packages not in sys.path:
        sys.path.append(site_packages)
