class IntentDetector:
    """
    A simple approach to detect whether the user wants to 'find', 'update', or 'delete'
    based on keywords in the text. This is a very minimalistic approach.
    """

    def get_intent(self, text: str) -> str:
        text_lower = text.lower()

        # Just a naive keyword-based approach
        if "update" in text_lower:
            return "update"
        elif "delete" in text_lower or "remove" in text_lower:
            return "delete"
        else:
            # default to 'find'
            return "find"
