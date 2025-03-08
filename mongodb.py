import pymongo
import datetime
import typing
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/',maxPoolSize=None)  # Replace with your MongoDB connection string


def check_db(db_name):
    if db_name in mongo_client.list_database_names():
        pass
    else:
        # Create the database if it doesn't exist
        print(f"The database '{db_name}' does not exist. Creating it...")

    return mongo_client[db_name]


def check_collection(db,collection_name):
    if collection_name in db.list_collection_names():
        collection = db[collection_name]
    else:
        # Create the collection if it doesn't exist
        print(f"The collection '{collection_name}' does not exist in the '{db.name}' database. Creating it...")
        db.create_collection(collection_name)
        collection = db[collection_name]
        collection.create_index([('timestamp', pymongo.ASCENDING)], unique=True)
    return collection