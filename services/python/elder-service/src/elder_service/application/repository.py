from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from elder_service.domain.models import ElderProfile


class ElderProfileRepository(Protocol):
    def save(self, profile: ElderProfile) -> ElderProfile:
        ...

    def get(self, elder_id: str) -> ElderProfile | None:
        ...

    def list_all(self) -> list[ElderProfile]:
        ...


@dataclass(slots=True)
class InMemoryElderProfileRepository:
    _store: dict[str, ElderProfile] = field(default_factory=dict)

    def save(self, profile: ElderProfile) -> ElderProfile:
        self._store[profile.elder_id] = profile
        return profile

    def get(self, elder_id: str) -> ElderProfile | None:
        return self._store.get(elder_id)

    def list_all(self) -> list[ElderProfile]:
        return list(self._store.values())
