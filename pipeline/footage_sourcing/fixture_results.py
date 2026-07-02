"""Hand-authored stand-ins for what a real source-client `.search()` call
would return, used ONLY by gate_test.py.

Why this exists: this session's egress policy denies every asset-source
host that was tested (api.nasa.gov, commons.wikimedia.org, www.loc.gov all
returned 403 from the proxy -- confirmed by direct curl during this build,
not assumed), and no Pexels/Pixabay keys are configured either. So there is
no way to produce real search results in this session. Rather than skip
the Phase 2 gate deliverable entirely, or silently fake it as if it were
live data, this file makes the substitution explicit and inspectable: every
entry below is something a person wrote, not something an API returned.

Some entries are deliberately built to FAIL confidence scoring or
domain-specific verification -- this is intentional, to prove the
reject-and-flag path actually rejects things rather than just existing as
unused code.
"""

from __future__ import annotations

from .types import SourcedAsset

FIXTURE_RESULTS: dict[str, list[SourcedAsset]] = {
    "CH1-hook": [
        SourcedAsset("pexels", "f1001", "Woman checking phone notification", "close up person checking phone screen", "https://example-fixture.invalid/1001", 0.79),
    ],
    "CH1-build": [
        SourcedAsset("pexels", "f1002", "Smartphone lock screen notifications", "smartphone screen with notification banners", "https://example-fixture.invalid/1002", 0.85),
    ],
    "CH1-escalation": [
        SourcedAsset("pexels", "f1003", "Person scrolling phone in bed at night", "scrolling social media phone dark room night", "https://example-fixture.invalid/1003", 0.71),
    ],
    "CH1-resolution": [
        SourcedAsset("pexels", "f1004", "Person holding phone neutral expression", "portrait holding phone looking at screen", "https://example-fixture.invalid/1004", 0.66),
    ],
    "CH1-closer": [
        SourcedAsset("pexels", "f1005", "Hand hovering over phone screen", "close up hand over smartphone screen", "https://example-fixture.invalid/1005", 0.74),
    ],
    "CH2-hook": [
        SourcedAsset("pexels", "f2001", "Young entrepreneur working late in office", "startup founder laptop late night office", "https://example-fixture.invalid/2001", 0.8),
    ],
    "CH2-build": [
        SourcedAsset("pexels", "f2002", "Small cluttered home office apartment", "small apartment desk office setup", "https://example-fixture.invalid/2002", 0.69),
    ],
    "CH2-escalation": [
        # Deliberately mismatched fixture (unrelated stock result) to
        # demonstrate the reject-and-flag path for a low overlap score.
        SourcedAsset("pexels", "f2003", "Birthday cake with candles", "celebration party cake photo", "https://example-fixture.invalid/2003", 0.12),
    ],
    "CH2-resolution": [
        SourcedAsset("pexels", "f2004", "Stock exchange trading floor screens", "trading floor stock exchange market screens", "https://example-fixture.invalid/2004", 0.83),
    ],
    "CH2-closer": [
        SourcedAsset("pexels", "f2005", "Framed document on wooden office desk", "framed paper document office desk", "https://example-fixture.invalid/2005", 0.7),
    ],
    "CH3-hook": [
        SourcedAsset("wikimedia", "f3001", "CIA classified document stamped SECRET, declassified 1994", "Central Intelligence Agency classified memo stamp", "https://example-fixture.invalid/3001", 0.77),
    ],
    "CH3-build": [
        SourcedAsset("wikimedia", "f3002", "Washington D.C. federal building, 1950s", "government office building Washington exterior 1950s", "https://example-fixture.invalid/3002", 0.62),
    ],
    "CH3-escalation": [
        # Deliberately missing the named entity ("Project MKUltra") from
        # title/description -- demonstrates §4's historical hard-verification
        # rejecting "thematically similar" results that don't name the entity.
        SourcedAsset("wikimedia", "f3003", "Typewritten government memo, redacted", "declassified government memorandum redacted text", "https://example-fixture.invalid/3003", 0.58),
    ],
    "CH3-resolution": [
        SourcedAsset("loc", "f3004", "United States Senate hearing room, Church Committee 1977", "Senate hearing room 1977 committee session", "https://example-fixture.invalid/3004", 0.72),
    ],
    "CH3-closer": [
        SourcedAsset("wikimedia", "f3005", "Burned paper fragments in a metal bin", "burned paper documents ashes fragments", "https://example-fixture.invalid/3005", 0.61),
    ],
    "CH4-hook": [
        SourcedAsset("pexels", "f4001", "Colorized MRI brain scan cross-section", "MRI brain scan medical imaging", "https://example-fixture.invalid/4001", 0.81),
    ],
    "CH4-build": [
        SourcedAsset("pexels", "f4002", "Person flinching startled reaction closeup", "startled reaction face closeup person", "https://example-fixture.invalid/4002", 0.68),
    ],
    "CH4-escalation": [
        SourcedAsset("pexels", "f4003", "Neuroscience laboratory equipment and monitors", "lab equipment neuroscience research monitors", "https://example-fixture.invalid/4003", 0.7),
    ],
    "CH4-resolution": [
        SourcedAsset("pexels", "f4004", "Researcher reviewing data at clinical desk", "clinical researcher desk lab coat reviewing", "https://example-fixture.invalid/4004", 0.65),
    ],
    "CH4-closer": [
        SourcedAsset("pexels", "f4005", "Calm close up portrait neutral lighting", "person calm expression close up portrait", "https://example-fixture.invalid/4005", 0.73),
    ],
    "CH5-hook": [
        SourcedAsset("loc", "f5001", "Women Airforce Service Pilots (WASP) portrait, 1943", "WASP pilot portrait World War II female aviator", "https://example-fixture.invalid/5001", 0.8),
    ],
    "CH5-build": [
        SourcedAsset("loc", "f5002", "Avenger Field, Sweetwater, Texas, 1943 training base", "Avenger Field Texas WASP training airbase 1943", "https://example-fixture.invalid/5002", 0.76),
    ],
    "CH5-escalation": [
        SourcedAsset("wikimedia", "f5003", "Wrecked training aircraft, WWII era, unidentified location", "aircraft wreckage World War II training accident", "https://example-fixture.invalid/5003", 0.55),
    ],
    "CH5-resolution": [
        SourcedAsset("loc", "f5004", "United States Congress in session, 1977", "Congress session chamber 1977 United States", "https://example-fixture.invalid/5004", 0.69),
    ],
    "CH5-closer": [
        SourcedAsset("loc", "f5005", "Elderly WASP veteran at reunion event, 2000s", "Women Airforce Service Pilots veteran elderly portrait", "https://example-fixture.invalid/5005", 0.71),
    ],
    "CH6-hook": [
        SourcedAsset("nasa", "f6001", "Jupiter in true color, Voyager 1", "Full-disk view of the planet Jupiter", "https://example-fixture.invalid/6001", None, catalog_id="PIA02873"),
    ],
    "CH6-build": [
        # Deliberately missing catalog_id -- demonstrates §4's "space domain
        # requires a real NASA catalog ID" hard rejection.
        SourcedAsset("nasa", "f6002", "Night sky with visible planet", "Night sky photography with planet visible", "https://example-fixture.invalid/6002", None, catalog_id=None),
    ],
    "CH6-escalation": [
        SourcedAsset("nasa", "f6003", "Jupiter's Great Red Spot in close-up, Juno spacecraft", "Great Red Spot storm close-up Juno mission", "https://example-fixture.invalid/6003", None, catalog_id="PIA21776"),
    ],
    "CH6-resolution": [
        SourcedAsset("nasa", "f6004", "Great Red Spot detail, enhanced color", "Great Red Spot Jupiter storm enhanced color detail", "https://example-fixture.invalid/6004", None, catalog_id="PIA22946"),
    ],
    "CH6-closer": [
        SourcedAsset("nasa", "f6005", "Jupiter size comparison with Earth and inner planets", "Jupiter scale comparison diagram inner solar system Earth", "https://example-fixture.invalid/6005", None, catalog_id="PIA17012"),
    ],
}
