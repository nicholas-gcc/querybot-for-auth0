import logging
import os

from pymongo.mongo_client import MongoClient

from ..utils.constants import MONGODB_DB_NAME, MONGODB_URI_ENV_VAR

logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    MongoDB Client to handle database connections and operations.
    """

    def __init__(self):
        """
        Initialize the MongoDB client with the provided URI and database name.
        """
        mongo_uri = os.getenv(MONGODB_URI_ENV_VAR)
        if not mongo_uri:
            logger.error(f"{MONGODB_URI_ENV_VAR} environment variable not set.")
            raise ValueError(f"{MONGODB_URI_ENV_VAR} environment variable not set.")

        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[MONGODB_DB_NAME]
            logger.info("MongoDB client initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize MongoDB client.")
            raise

    def get_collection(self, collection_name: str):
        """
        Get a MongoDB collection.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection object.
        """
        if not collection_name:
            logger.error("Collection name must be provided.")
            raise ValueError("Collection name must be provided.")

        return self.db[collection_name]


mongo_client = MongoDBClient()

