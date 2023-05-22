import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

print(os.environ.get('MONGO_DB_URL'))

# Get environment variables
openai_api_key = os.environ.get('OPENAI_API_KEY')
discord_bot_token = os.environ.get('DISCORD_BOT_TOKEN')
mongo_db_url = os.environ.get('MONGO_DB_URL')
mongo_db = os.environ.get('MONGO_DB')
conversation_list_collection = os.environ.get('CONVERSATION_LIST_COLLECTION')
conversations_collection = os.environ.get('CONVERSATIONS_COLLECTION')

# Connect to MongoDB
mongo_client = MongoClient(mongo_db_url)
deus_db = mongo_client[mongo_db]
user_conversation_list = deus_db[conversation_list_collection]
conversations = deus_db[conversations_collection]