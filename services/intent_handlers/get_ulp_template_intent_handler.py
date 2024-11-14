import json
from .base_intent_handler import BaseIntentHandler
from ...utils.constants import (
    MULTILINE_CODE_DELIMITER,
    GET_ULP_TEMPLATE_INTENT,
    MAX_MESSAGE_LENGTH,
    NO_DATA_MESSAGE
)

class GetULPTemplateIntentHandler(BaseIntentHandler):
    INTENT_NAME = GET_ULP_TEMPLATE_INTENT

    def can_handle(self, intent_name):
        """
        Determines if the intent passed to the class matches the handler.
        """
        return intent_name == self.INTENT_NAME

    def handle_intent(self, parameters, auth0_service):
        """
        Liaises with the Management API to get the Universal Login Page template,
        prettifies the HTML and CSS, and determines if file upload is needed.
        """
        endpoint = 'branding/templates/universal-login'

        response_data = auth0_service.get(endpoint)
        if not response_data:
            return NO_DATA_MESSAGE, False

        body_html = response_data.get('body')
        if not body_html:
            return NO_DATA_MESSAGE, False

        formatted_html = self.format_response(body_html)
        if not formatted_html:
            return NO_DATA_MESSAGE, False

        needs_file_upload = True

        return formatted_html, needs_file_upload

    def format_response(self, html_string):
        """
        Parses and formats the HTML string with proper indentations,
        including formatting CSS inside <style> tags.
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_string, 'html.parser')

            # Find all <style> tags and format their content
            for style_tag in soup.find_all('style'):
                css_content = style_tag.string
                if css_content:
                    formatted_css = self.format_css(css_content)
                    # Replace the style tag's content with formatted CSS
                    style_tag.string.replace_with(formatted_css)

            prettified_html = soup.prettify()
            return prettified_html
        except ImportError as e:
            # Handle ImportError if BeautifulSoup is not installed
            return f"An error occurred: {str(e)}"
        except Exception as e:
            # Handle any other exceptions
            return f"An error occurred while formatting the HTML: {str(e)}"

    def format_css(self, css_content):
        """
        Formats CSS content with proper indentation.
        """
        css_content = css_content.strip()
        # Add newlines and indentation
        css_content = css_content.replace('}', '\n}\n')
        css_content = css_content.replace('{', ' {\n    ')
        css_content = css_content.replace(';', ';\n    ')
        # Remove extra spaces
        lines = css_content.split('\n')
        formatted_lines = []
        indent_level = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if '}' in line:
                indent_level -= 1
            formatted_lines.append('    ' * indent_level + line)
            if '{' in line and not '}' in line:
                indent_level += 1
        return '\n'.join(formatted_lines)
