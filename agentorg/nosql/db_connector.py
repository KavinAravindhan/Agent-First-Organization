import pymongo

class DBConnector:
    """
    A minimal example of how you can connect to a MongoDB instance and run queries.
    Modify host, database, collection to your environment.
    """

    def __init__(self, uri="mongodb://localhost:27017", db_name="test_db", collection_name="test_col"):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = pymongo.MongoClient(self.uri)
        self.collection = self.client[self.db_name][self.collection_name]

    def execute_query(self, query_dict: dict, intent: str):
        """
        Based on the intent, run the appropriate MongoDB command 
        (find, update, or delete) and return results.
        """
        if intent == "find":
            mongo_filter = query_dict.get("filter", {})
            results_cursor = self.collection.find(mongo_filter)
            return list(results_cursor)
        
        elif intent == "update":
            mongo_filter = query_dict.get("filter", {})
            update_doc = query_dict.get("update", {})
            result = self.collection.update_many(mongo_filter, update_doc)
            return {
                "matched": result.matched_count,
                "modified": result.modified_count
            }
        
        elif intent == "delete":
            mongo_filter = query_dict.get("filter", {})
            result = self.collection.delete_many(mongo_filter)
            return {
                "deleted_count": result.deleted_count
            }

        else:
            return {"error": "Unrecognized intent for DB query."}
