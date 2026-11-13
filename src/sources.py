"""Select the source of dependency edges from validated settings."""

from typing import Protocol

from .config import Settings
from .maven import MavenRepository
from .test_repo import TestRepository


class DependencySource(Protocol):
    """Minimal common interface for real and test repositories."""

    def dependencies(self, name: str) -> tuple[str, ...]:
        """Return immediately required packages."""
        ...


def open_source(settings: Settings) -> DependencySource:
    """Instantiate a test source or a live Maven repository reader."""
    if settings.test_mode:
        return TestRepository(settings.repository)
    return MavenRepository(settings.repository)
