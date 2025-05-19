"""chameleon tap class."""

from typing import List
from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_chameleon.streams import (
    MicroSurveyResponses
)
import logging
logging.basicConfig(level=logging.INFO)
PLUGIN_NAME = "tap-chameleon"

STREAM_TYPES = [
    MicroSurveyResponses
]


class TapChameleon(Tap):
    """chameleon tap class."""

    name = "tap-chameleon"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_account_secret",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "survey_id",
            th.StringType,
            required=True,
            description="The ID of the survey to fetch responses for"
        ),
        th.Property(
            "api_base_url",
            th.StringType,
            default="https://api.chameleon.io",
            description="The base URL for the API service"
        ),
        th.Property(
            "survey_name",
            th.StringType,
            required=False,
            description="Name of the survey to fetch responses for"
        ),
        th.Property(
            "limit",
            th.IntegerType,
            required=False,
            default=50,
            description="The survey response API limit"
        ),
        th.Property(
            "created_before",
            th.StringType,
            required=False,
            description="Read as created before and can be given as a timestamp or ID to get only limit items that were created before this time"
        ),
        th.Property(
            "created_after",
            th.StringType,
            required=False,
            description="Read as created after and can be given as a timestamp or ID to get only limit items that were created after this time"
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        try:
            streams = [stream_class(tap=self) for stream_class in STREAM_TYPES]
            return streams
        except Exception as e:
            logging.exception(f"Error in discover_streams: {e}")
            raise

# CLI Execution:
cli = TapChameleon.cli
