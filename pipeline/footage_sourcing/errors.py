"""Fail-loud error types for the footage-sourcing module.

Per CLAUDE.md ground rule #2 ("fail loud — no silent fallback, no soft-skip,
no close-enough substitution"), every failure mode below is a raised
exception, never a silently-returned default/placeholder value.
"""


class FootageSourcingError(Exception):
    """Base class for all footage-sourcing failures."""


class NotConfiguredError(FootageSourcingError):
    """Raised when a client needs a credential that isn't set.

    This is the correct outcome when an API key is genuinely missing --
    NOT a fallback to fake/mock data. Callers must treat this the same as
    any other sourcing failure: flag the beat for manual review, don't
    substitute anything.
    """


class DomainRoutingViolation(FootageSourcingError):
    """Raised if code attempts to route a keyword to a source forbidden for
    its domain (e.g. a `space` or `historical-*` keyword sent to a
    geocoder). This is the structural guard from
    04_ASSET_ACCURACY_BIBLE.md §1 -- it must be impossible to bypass, so it
    raises rather than logging a warning and continuing.
    """


class NoConfidentMatchError(FootageSourcingError):
    """Raised when no candidate asset clears the confidence threshold.

    Per 04_ASSET_ACCURACY_BIBLE.md §3 point 5: "Below-threshold results are
    rejected, not accepted as close enough. The shot gets flagged for
    manual review rather than silently getting a wrong or generic image."
    """
