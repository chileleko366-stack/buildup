"""Common interface every asset-source client implements."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import SourcedAsset, VisualKeyword


class AssetClient(ABC):
    name: str

    @abstractmethod
    def search(self, keyword: VisualKeyword) -> list[SourcedAsset]:
        """Return candidate assets for a keyword, unscored, unfiltered.

        Must raise (not return an empty-looking placeholder) if the client
        can't reach its API for a reason other than "no results" -- e.g.
        NotConfiguredError for a missing key, or the underlying network/HTTP
        error uncaught, so callers see the real failure.
        """
        raise NotImplementedError
