"""Stream class for tap-chameleon."""

import sys

from typing import Dict, Any
from singer_sdk import Tap, typing as th
from singer_sdk._singerlib import Schema
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import SimpleAuthenticator

from typing import Dict, Any


class CustomPaginator:
    def __init__(self, cursor: Dict[str, Any] = None, limit: int = 1):
        self.cursor = cursor or {}
        self.limit = limit

    def get_url_params(self) -> Dict[str, Any]:
        """
        Return URL parameters to be used for the next request.
        Includes pagination using the 'before' cursor.
        """
        url_params = {"limit": self.limit}
        if "before" in self.cursor:
            url_params["before"] = self.cursor["before"]
        return url_params


class TapChameleonStream(RESTStream):
    """tap-chameleon stream class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._paginator = CustomPaginator(limit=1)

    _LOG_REQUEST_METRIC_URLS: bool = True

    next_page_token_jsonpath = "$.cursor.before"

    @property
    def url_base(self) -> str:
        """Base URL of source"""
        return self.config.get("api_base_url", "https://api.chameleon.io")

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        return headers

    @property
    def authenticator(self):
        http_headers = {}

        # Setting tap specific auth method
        if self.config.get("api_account_secret"):
            http_headers["X-Account-Secret"] = self.config.get("api_account_secret")

        return SimpleAuthenticator(stream=self, auth_headers=http_headers)

    def get_new_paginator(self, response: Dict[str, Any]) -> CustomPaginator:
        """
        Use the custom paginator logic to handle pagination and return the updated paginator.
        """
        return self._paginator.get_new_paginator(response)


class MicroSurveyResponses(TapChameleonStream):
    name = "survey_responses"
    path = "/v3/analyze/responses"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.responses[*]"

    schema = th.PropertiesList(
        # TO DO
        th.Property("id", th.StringType),
    ).to_dict()

    def get_url_params(
        self, context: Dict | None, next_page_token: Any | None
    ) -> Dict[str, Any] | str:
        params: dict = {}
        survey_id = self.config.get("survey_id", None)
        limit = self.config.get("limit", 500)
        if survey_id is not None:
            params["id"] = survey_id
        else:
            self.logger.error(
                "The query stirng parameter 'survey_id' should be provided. Exiting application."
            )
            sys.exit()
        return params


# class Events(TapChameleonStream):
#     name = "events"  # Stream name
#     path = "/api/v2/logs/events/search"  # API endpoint after base_url
#     primary_keys = ["id"]
#     records_jsonpath = "$.data[*]"  # https://jsonpath.com Use requests response json to identify the json path
#     replication_key = None
#     # schema_filepath = SCHEMAS_DIR / "events.json"  # Optional: use schema_filepath with .json inside schemas/

#     # Optional: If using schema_filepath, remove the propertyList schema method below
#     schema = th.PropertiesList(
#         th.Property("id", th.NumberType),
#         th.Property("name", th.StringType),
#     ).to_dict()
#     # Overwrite GET here by updating rest_method
#     rest_method = "POST"

#     def prepare_request_payload(
#         self, context: Optional[dict], next_page_token: Optional[Any]
#     ) -> Optional[dict]:
#         """Define request parameters to return"""
#         payload = {
#             "filter": {
#                 "query": "source:degreed.api env:production",
#                 "from": self.config.get("start_date"),
#             },
#             "page": {"limit": 4},
#         }
#         return payload

# For passing url parameters:
# def get_url_params(
#     self, context: Optional[dict], next_page_token: Optional[Any]
# ) -> Dict[str, Any]:


### Template to use for new stream
# class TemplateStream(RESTStream):
#     """Template stream class."""

#     # TODO: Set the API's base URL here:
#     url_base = "https://api.mysample.com"

#     # OR use a dynamic url_base:
#     # @property
#     # def url_base(self) -> str:
#     #     """Return the API URL root, configurable via tap settings."""
#     #     return self.config["api_url"]

#     records_jsonpath = "$[*]"  # Or override `parse_response`.
#     next_page_token_jsonpath = "$.next_page"  # Or override `get_next_page_token`.

#     @property
#     def authenticator(self) -> BasicAuthenticator:
#         """Return a new authenticator object."""
#         return BasicAuthenticator.create_for_stream(
#             self,
#             username=self.config.get("username"),
#             password=self.config.get("password"),
#         )

#     @property
#     def http_headers(self) -> dict:
#         """Return the http headers needed."""
#         headers = {}
#         if "user_agent" in self.config:
#             headers["User-Agent"] = self.config.get("user_agent")
#         # If not using an authenticator, you may also provide inline auth headers:
#         # headers["Private-Token"] = self.config.get("auth_token")
#         return headers

#     def get_next_page_token(
#         self, response: requests.Response, previous_token: Optional[Any]
#     ) -> Optional[Any]:
#         """Return a token for identifying next page or None if no more pages."""
#         # TODO: If pagination is required, return a token which can be used to get the
#         #       next page. If this is the final page, return "None" to end the
#         #       pagination loop.
#         if self.next_page_token_jsonpath:
#             all_matches = extract_jsonpath(
#                 self.next_page_token_jsonpath, response.json()
#             )
#             first_match = next(iter(all_matches), None)
#             next_page_token = first_match
#         else:
#             next_page_token = response.headers.get("X-Next-Page", None)

#         return next_page_token

#     def get_url_params(
#         self, context: Optional[dict], next_page_token: Optional[Any]
#     ) -> Dict[str, Any]:
#         """Return a dictionary of values to be used in URL parameterization."""
#         params: dict = {}
#         if next_page_token:
#             params["page"] = next_page_token
#         if self.replication_key:
#             params["sort"] = "asc"
#             params["order_by"] = self.replication_key
#         return params

#     def prepare_request_payload(
#         self, context: Optional[dict], next_page_token: Optional[Any]
#     ) -> Optional[dict]:
#         """Prepare the data payload for the REST API request.

#         By default, no payload will be sent (return None).
#         """
#         # TODO: Delete this method if no payload is required. (Most REST APIs.)
#         return None

#     def parse_response(self, response: requests.Response) -> Iterable[dict]:
#         """Parse the response and return an iterator of result records."""
#         # TODO: Parse response body and return a set of records.
#         yield from extract_jsonpath(self.records_jsonpath, input=response.json())

#     def post_process(self, row: dict, context: Optional[dict]) -> dict:
#         """As needed, append or transform raw data to match expected structure."""
#         # TODO: Delete this method if not needed.
#         return row
