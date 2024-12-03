import logging
from typing import Any, Dict, Optional, Tuple

from bs4 import BeautifulSoup

from .base_intent_handler import BaseIntentHandler
from ...utils.constants import (
    GET_ULP_TEMPLATE_INTENT,
    NO_DATA_MESSAGE,
)

logger = logging.getLogger(__name__)


class GetULPTemplateIntentHandler(BaseIntentHandler):
    """
    Intent handler for retrieving and formatting the Universal Login Page template.
    """

    INTENT_NAME = GET_ULP_TEMPLATE_INTENT

    def can_handle(self, intent_name: str) -> bool:
        """
        Determines if the intent passed to the class matches the handler.

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
        Liaises with the Auth0 Management API to get the Universal Login Page template,
        prettifies the HTML and CSS, and determines if file upload is needed.

        Args:
            parameters (Dict[str, Any]): Parameters extracted from the user's message.
            auth0_service: The Auth0 service instance for making API calls.

        Returns:
            Tuple[str, bool, Optional[str]]: A tuple containing the formatted HTML,
            a flag indicating if file upload is needed, and additional text (None).
        """
        endpoint = 'branding/templates/universal-login'

        try:
            logger.debug(f"Requesting Universal Login Page template from {endpoint}")
            response_data = auth0_service.get(endpoint)
            if not response_data:
                logger.info("No data received for Universal Login Page template.")
                return NO_DATA_MESSAGE, False, None

            body_html = response_data.get('body')
            if not body_html:
                logger.info("No 'body' key found in response data.")
                return NO_DATA_MESSAGE, False, None

            formatted_html = self.format_response(body_html)
            if not formatted_html:
                logger.info("Formatting of HTML failed or resulted in empty content.")
                return NO_DATA_MESSAGE, False, None

            needs_file_upload = True

            return formatted_html, needs_file_upload, None

        except Exception as e:
            logger.exception("Error handling GetULPTemplate intent.")
            return f"An error occurred: {str(e)}", False, None

    def format_response(self, html_string: str) -> str:
        """
        Parses and formats the HTML string with proper indentations,
        including formatting CSS inside <style> tags.

        Args:
            html_string (str): The raw HTML string to format.

        Returns:
            str: The formatted HTML string.
        """
        try:
            soup = BeautifulSoup(html_string, 'html.parser')

            # Format CSS inside <style> tags
            for style_tag in soup.find_all('style'):
                if style_tag.string:
                    formatted_css = self.format_css(style_tag.string)
                    # Replace the existing CSS with formatted CSS
                    style_tag.string.replace_with(formatted_css)

            # Prettify the HTML with proper indentation
            prettified_html = soup.prettify(formatter="html")

            return prettified_html

        except Exception as e:
            logger.exception("Error formatting the HTML content.")
            return ""

    def format_css(self, css_content: str) -> str:
        """
        Formats CSS content with proper indentation using cssutils.

        Args:
            css_content (str): The raw CSS content.

        Returns:
            str: The formatted CSS content.
        """
        try:
            import cssutils

            # Suppress cssutils warnings and errors
            cssutils.log.setLevel(logging.CRITICAL)

            # Set serializer preferences
            cssutils.ser.prefs.indent = '    '  # 4 spaces
            cssutils.ser.prefs.keepAllProperties = True
            cssutils.ser.prefs.lineSeparator = '\n'
            cssutils.ser.prefs.omitLastSemicolon = False
            cssutils.ser.prefs.validOnly = False  # Include all rules, even if invalid

            # Parse the CSS content
            sheet = cssutils.parseString(css_content, validate=False)
            formatted_css = sheet.cssText.decode('utf-8')

            # Post-process to add newlines between rules
            formatted_css = formatted_css.replace('}\n', '}\n\n')

            return formatted_css

        except ImportError as e:
            logger.exception("cssutils library is not installed.")
            raise ImportError("Please install 'cssutils' to format CSS.") from e
        except Exception as e:
            logger.exception("Error formatting the CSS content.")
            return css_content  # Return unformatted CSS as a fallback
