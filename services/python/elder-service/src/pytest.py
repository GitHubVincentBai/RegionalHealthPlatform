"""Compatibility shim for repository-level elder-service verification.

The elder-service test entrypoint uses unittest, but the shared verification
script also imports ``pytest`` as a dependency probe. Expose a tiny local
module so the isolated service environment stays self-contained offline.
"""

__all__: list[str] = []
__version__ = "0.0-local"
