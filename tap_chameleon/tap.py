"""chameleon tap class."""

from typing import List
from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_chameleon.streams import (
    MicroSurveyResponses,
)

PLUGIN_NAME = "tap-chameleon"

STREAM_TYPES = [
    MicroSurveyResponses,
]


class TapChameleon(Tap):
    """chameleon tap class."""

    name = "tap-chameleon"

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        streams = [stream_class(tap=self) for stream_class in STREAM_TYPES]
        return streams


# CLI Execution:
cli = TapChameleon.cli
