import re

class StringUtils(object):
    
    @staticmethod
    def remove_format(text):
        # Replace code blocks with placeholders
        code_block_pattern = re.compile(r'```(.*?)```', re.DOTALL)
        code_blocks = []
        def code_block_replacer(match):
            code_blocks.append(match.group(0))
            return f"CODEBLOCK_{len(code_blocks)-1}"
        text = code_block_pattern.sub(code_block_replacer, text)

        # Replace inline code segments with placeholders
        inline_code_pattern = re.compile(r'`([^`]+)`')
        inline_codes = []
        def inline_code_replacer(match):
            inline_codes.append(match.group(0))
            return f"INLINECODE_{len(inline_codes)-1}"
        text = inline_code_pattern.sub(inline_code_replacer, text)

        # Remove wrapping underscores, asterisks, and tildes
        text = re.sub(r'_(.*?)_', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'~(.*?)~', r'\1', text)

        # Process links
        # Replace <URL|DISPLAY_TEXT> with DISPLAY_TEXT
        text = re.sub(r'<[^|>]+\|([^>]+)>', r'\1', text)
        # Replace <URL> with URL
        text = re.sub(r'<([^|>]+)>', r'\1', text)

        # Restore inline code segments
        for i, code in enumerate(inline_codes):
            placeholder = f"INLINECODE_{i}"
            text = text.replace(placeholder, code)

        # Restore code blocks
        for i, code in enumerate(code_blocks):
            placeholder = f"CODEBLOCK_{i}"
            text = text.replace(placeholder, code)

        return text
