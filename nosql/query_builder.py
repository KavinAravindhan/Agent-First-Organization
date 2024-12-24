from agentorg.nosql.keywords import KeywordExtractor

class QueryBuilder:
    """
    Converts the user text + detected intent into a NoSQL query object (for Mongo or other).
    """

    def __init__(self):
        self.keyword_extractor = KeywordExtractor()

    def build_query(self, text: str, intent: str):
        """
        For 'find', we build a Mongo filter dict.
        For 'update', we parse what fields to update.
        For 'delete', we parse what filter to remove docs.
        """

        # parse user text for field-value pairs
        pairs = self.keyword_extractor.extract_pairs(text)

        if intent == "find":
            # Build a simple filter: {field: value}
            mongo_filter = {}
            for p in pairs:
                field = p["field"]
                op = p["op"]
                val = p["value"]
                # Convert to int if numeric
                if val.isdigit():
                    val = int(val)
                if op == "=":
                    mongo_filter[field] = val
                elif op == ">":
                    mongo_filter[field] = {"$gt": val}
                elif op == "<":
                    mongo_filter[field] = {"$lt": val}
            return {"filter": mongo_filter}

        elif intent == "update":
            # update set for all extracted pairs
            update_filter = {}
            update_set = {}
            for p in pairs:
                if p["op"] == "=":
                    # assume field=val is the update target
                    update_set[p["field"]] = p["value"]
                else:
                    # or skip other ops
                    pass
            # Hard-code filter or parse from text
            # For demonstration, let's say we also parse "where field=val" separately
            # but we'll keep it simple here
            update_filter = {"status": "inactive"}  # example condition
            return {"filter": update_filter, "update": {"$set": update_set}}

        elif intent == "delete":
            # build a filter from pairs for deleting
            delete_filter = {}
            for p in pairs:
                field = p["field"]
                op = p["op"]
                val = p["value"]
                if val.isdigit():
                    val = int(val)
                if op == "=":
                    delete_filter[field] = val
            return {"filter": delete_filter}

        else:
            # default
            return {}
