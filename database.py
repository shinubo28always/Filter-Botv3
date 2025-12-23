from pymongo import MongoClient
import config
import sys

try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client['anime_permanent_db']
    db.command('ping')
    print("✅ MongoDB Connected")
except Exception as e:
    print(f"❌ MongoDB Error: {e}")
    sys.exit(1)

users = db['users']
groups = db['groups']
filters = db['filters']
admins = db['admins']
requests_db = db['requests']

# --- FUNCTIONS ---
def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def get_all_users():
    return [u['_id'] for u in users.find()]

def add_group(chat_id, title):
    groups.update_one({"_id": str(chat_id)}, {"$set": {"title": title}}, upsert=True)

def remove_group(chat_id):
    groups.delete_one({"_id": str(chat_id)})

def get_all_groups():
    return [g['_id'] for g in groups.find()]

def is_admin(uid):
    return str(uid) == str(config.OWNER_ID) or admins.find_one({"_id": str(uid)}) is not None

def add_filter(keyword, data):
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": data}, upsert=True)

def get_filter(keyword):
    return filters.find_one({"keyword": keyword.lower().strip()})

def get_all_keywords():
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    return list(filters.find({}, {"keyword": 1, "title": 1}))

def delete_filter(keyword):
    return filters.delete_one({"keyword": keyword.lower().strip()}).deleted_count

def delete_all_filters():
    return filters.delete_many({}).deleted_count
