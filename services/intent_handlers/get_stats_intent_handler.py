import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from .base_intent_handler import BaseIntentHandler
from ...utils.constants import (
    DATE_PERIOD_PARAM,
    GET_STATS_INTENT,
    MAX_MESSAGE_LENGTH,
    MULTILINE_CODE_DELIMITER,
    NO_DATA_MESSAGE,
)

logger = logging.getLogger(__name__)


class GetStatsIntentHandler(BaseIntentHandler):
    """
    Intent handler for retrieving daily statistics from Auth0.
    """

    INTENT_NAME = GET_STATS_INTENT

    def can_handle(self, intent_name: str) -> bool:
        """
        Determine if this handler can handle the given intent.

        Args:
            intent_name (str): The name of the intent.

        Returns:
            bool: True if it can handle the intent, False otherwise.
        """
        return intent_name == self.INTENT_NAME

    def handle_intent(
        self, parameters: Dict[str, Any], auth0_service
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Handle the 'GetStats' intent.

        Args:
            parameters (Dict[str, Any]): The parameters extracted from the user's message.
            auth0_service: The Auth0 service instance for making API calls.

        Returns:
            Tuple[str, bool, Optional[str]]: A tuple containing the formatted response,
            a flag indicating if file upload is needed, and any additional text.
        """
        date_period_list = parameters.get(DATE_PERIOD_PARAM)
        date_period = date_period_list[0] if date_period_list else None

        start_date_str = None
        end_date_str = None

        if date_period:
            start_date_str = date_period.get('startDate')
            end_date_str = date_period.get('endDate')

        # Build query parameters
        params = {}
        date_info = ""

        try:
            start_date = None
            end_date = None

            if start_date_str:
                start_date = self.parse_and_adjust_date(start_date_str)
                from_date = start_date.strftime('%Y%m%d')
                params['from'] = from_date

            if end_date_str:
                end_date = self.parse_and_adjust_date(end_date_str)
                to_date = end_date.strftime('%Y%m%d')
                params['to'] = to_date

            if start_date and end_date:
                # Ensure 'from' date is less than or equal to 'to' date
                if start_date > end_date:
                    # Swap dates in params
                    params['from'], params['to'] = params['to'], params['from']
                    start_date, end_date = end_date, start_date  # Swap dates

                # Apply inline code formatting to dates
                start_date_formatted = f"`{start_date.strftime('%d-%m-%Y')}`"
                end_date_formatted = f"`{end_date.strftime('%d-%m-%Y')}`"
                date_info = (
                    f"Daily stats from {start_date_formatted} to {end_date_formatted}"
                )
            elif start_date:
                start_date_formatted = f"`{start_date.strftime('%d-%m-%Y')}`"
                date_info = f"Daily stats from {start_date_formatted}"
            elif end_date:
                end_date_formatted = f"`{end_date.strftime('%d-%m-%Y')}`"
                date_info = f"Daily stats to {end_date_formatted}"
            else:
                date_info = "Daily stats:"

            # Call the Auth0 Management API
            endpoint = 'stats/daily'
            logger.debug(f"Requesting stats from Auth0 API with params: {params}")
            response_data = auth0_service.get(endpoint, query_params=params)

            if not response_data:
                logger.info("No data received from Auth0 API.")
                return NO_DATA_MESSAGE, False, None

            formatted_response = self.format_response(response_data)

            # Check if the formatted response exceeds Slack's limit
            if len(formatted_response) > MAX_MESSAGE_LENGTH:
                needs_file_upload = True
            else:
                needs_file_upload = False
                formatted_response = (
                    f"{MULTILINE_CODE_DELIMITER}{formatted_response}{MULTILINE_CODE_DELIMITER}"
                )

            return formatted_response, needs_file_upload, date_info

        except Exception as e:
            logger.exception("Error handling GetStats intent.")
            # Handle parsing errors or API errors
            return f"An error occurred: {str(e)}", False, None

    def parse_and_adjust_date(self, date_str: str) -> datetime:
        """
        Parse the date string and adjust the year to the current year if in the future.

        Args:
            date_str (str): The date string to parse.

        Returns:
            datetime: The parsed and adjusted datetime object.
        """
        # Parse the date string into a datetime object
        date = datetime.fromisoformat(date_str.rstrip('Z'))

        # Get current date in UTC
        current_date = datetime.now(timezone.utc)

        # Adjust year if date is in the future
        if date > current_date:
            date = date.replace(year=current_date.year)

        return date

    def format_response(self, res: Any) -> str:
        """
        Format the API response.

        Args:
            res (Any): The response data from the API.

        Returns:
            str: The formatted response string.
        """
        formatted_json = json.dumps(res, indent=4)
        return formatted_json
