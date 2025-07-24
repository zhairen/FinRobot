from typing import Annotated

from myfinrobot.functional.json_parse import parse_relaxed_json

class TextUtils:

    def check_text_length(
        text: Annotated[str, "text to check"],
        min_length: Annotated[int, "minimum length of the text, default to 0"] = 0,
        max_length: Annotated[int, "maximum length of the text, default to 100000"] = 100000,
    ) -> str:
        """
        Check if the length of the text is exceeds than the maximum length.
        """
        length = len(text)#text.split()
        if length > max_length:
            return f"Text length {length} exceeds the maximum length of {max_length}."
        elif length < min_length:
            return f"Text length {length} is less than the minimum length of {min_length}."
        else:
            return f"Text length {length} is within the expected range."
    
    def fix_relaxed_json(json_string: str) -> str:        
        """
        Parse a JSON string that may have missing closing quotes or braces.
        Attempts to correct these issues and returns a valid JSON string or the original string if it cannot be parsed.
        """
        try:
            return parse_relaxed_json(json_string)
        except:
            return json_string  # Return the original string if parsing fails
    