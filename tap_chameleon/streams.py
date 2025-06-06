"""Stream class for tap-chameleon."""

from typing import Dict, Any, Iterable, Union, List, Optional

from singer_sdk import typing as th
from singer_sdk.streams import RESTStream
from singer_sdk.pagination import BaseHATEOASPaginator

import logging
logging.basicConfig(level=logging.INFO)

class CustomHATEOASPaginator(BaseHATEOASPaginator):

    def get_next_url(self, response) -> Optional[str]:
        """
        Fetch the next page URL based on the cursor.
        
        Args:
            response: The API response object
            
        Returns:
            Optional[str]: The next page URL or None if no more pages
        """
        cursor = response.json().get("cursor", {})
        return cursor.get("before")

    def get_next_token(self, response) -> Optional[str]:
        """
        Retrieve the next token for pagination.
        
        Args:
            response: The API response object
            
        Returns:
            Optional[str]: The next pagination token or None if no more pages
        """
        cursor = response.json().get("cursor", {})
        return cursor.get("before")


class TapChameleonStream(RESTStream):
    """tap-chameleon stream class"""

    _LOG_REQUEST_METRIC_URLS: bool = True

    @property
    def url_base(self) -> str:
        """
        Return the base URL for API requests.
        
        Returns:
            str: The base URL, defaults to 'https://api.chameleon.io' if not specified
            
        Raises:
            Exception: If there's an error accessing configuration
        """
        try:
            return self.config.get("api_base_url", "https://api.chameleon.io")
        except Exception as e:
            logging.exception("Error retrieving base URL from configuration")
            raise

    @property
    def http_headers(self) -> Dict[str, str]:
        """
        Return the HTTP headers needed for API requests.
        
        Returns:
            Dictionary containing required HTTP headers
            
        Raises:
            Exception: If there's an error accessing configuration
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if api_secret := self.config.get("api_account_secret"):
                headers["X-Account-Secret"] = api_secret
                
            return headers
            
        except Exception as e:
            logging.exception("Error generating HTTP headers")
            raise

    
    def get_new_paginator(self) -> CustomHATEOASPaginator:
        """
        Return a new instance of the custom HATEOAS paginator.
        
        Returns:
            CustomHATEOASPaginator: A paginator instance for handling API pagination
        """
        return CustomHATEOASPaginator()

class MicroSurveyResponses(TapChameleonStream):

    """Stream for handling Chameleon micro-survey responses."""
    
    # Stream configuration
    name: str = "survey_responses"
    path: str = "/v3/analyze/responses"
    primary_keys: List[str] = ["id"]
    replication_key: Optional[str] = "created_at"
    
    # JSON response parsing
    records_jsonpath: str = "$.responses[*]"
    next_page_token_jsonpath: str = "$.cursor.before"

    # Stream schema definition
    schema: Dict[str, Any] = th.PropertiesList(
        # Response metadata
        th.Property("id", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("finished_at", th.DateTimeType),
        
        # Survey details
        th.Property("survey_id", th.StringType),
        th.Property("profile_id", th.StringType),
        th.Property("button_text", th.StringType),
        th.Property("input_text", th.StringType),
        
        # Profile information
        th.Property("profile", th.ObjectType(
            th.Property("id", th.StringType),  # Profile ID
            th.Property("browser_l", th.StringType),  # Browser language
            th.Property("created_at", th.StringType),  # Other details
            th.Property("updated_at", th.StringType),  # Other details
            # Company details
            th.Property("company", th.ObjectType(
            th.Property("uid", th.StringType)
        ))),
    )).to_dict()
    
    def get_url_params(
        self,
        context: Optional[Dict[str, Any]],
        next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """
        Get URL parameters for the API request.

        Args:
            context: The stream context dictionary
            next_page_token: Token for pagination

        Returns:
            Dictionary of URL parameters

        Raises:
            ValueError: If survey_id is not provided in config
        """
        try:
            params = {
                "limit": self.config.get("limit", 50),
                "expand[profile]":"all"
            }

            survey_id = self.config.get("survey_id")
            if not survey_id:
                raise ValueError("survey_id is required in config")
            params["id"] = survey_id

            # GIO TEST
            logging.info("### Printing stream state")
            if self.stream_state:
                logging.info(f"Stream state: {self.stream_state}")
            logging.info("############################")
            # GIO TEST

            start_date = None
            # Check if 'bookmarks' and 'survey_responses' exist in stream_state
            if "bookmarks" in self.stream_state and "survey_responses" in self.stream_state["bookmarks"]:
                replication_state = self.stream_state["bookmarks"]["survey_responses"]
                if "replication_key_value" in replication_state:
                    logging.info(f"replication_key_value: {replication_state['replication_key_value']}")
                    start_date = replication_state['replication_key_value']
            elif "replication_key_value" in self.stream_state:
                logging.info(f"replication_key_value: {self.stream_state['replication_key_value']}")
                start_date= self.stream_state['replication_key_value']

            if start_date:
                params["after"] = start_date
                logging.info(f"Adding {start_date} replication key as start date")

            # Add optional parameters if they exist, this is for testing purposes. using this will interepret the incremental load.
            for param_name, config_key in [
                ("before", "created_before"),
                ("after", "created_after")
            ]:
                if value := self.config.get(config_key):
                    params[param_name] = value
                    logging.info(f"Adding {param_name} parameter: {value}")

            # Override 'before' parameter if next_page_token exists
            if next_page_token:
                params["before"] = next_page_token

            return params

        except Exception as e:
            logging.exception("Error generating URL parameters")
            raise
