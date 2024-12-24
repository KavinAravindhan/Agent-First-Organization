import re

class KeywordExtractor:
    """
    Extracts potential field-value pairs from user text, e.g. 'status=active', 'age > 30'
    or simpler tokens that might appear.
    """

    def extract_pairs(self, text: str):
        """
        Simple demonstration:
        - Finds 'field=value' or 'field>value' or 'field<value'
        - Returns a list of dicts like [{'field': 'status', 'op': '=', 'value': 'active'}]
        """

        pattern = r"(\w+)\s*(=|>|<)\s*([\w\d]+)"
        matches = re.findall(pattern, text)
        results = []
        for field, op, val in matches:
            results.append({"field": field, "op": op, "value": val})
        return results
