from pymongo import MongoClient
import config

# MongoDB Connection
client = MongoClient(config.MONGO_URI)
db = client['anime_filter_bot']

users = db['users']
filters = db['filters']
settings = db['settings']
admins = db['admins']

def add_user(uid):
    users.update_one({"_id": uid}, {"$set": {"_id": uid}}, upsert=True)

def is_admin(uid):
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_filter(keyword, data):
    filters.update_one({"keyword": keyword.lower()}, {"$set": data}, upsert=True)

def get_filter(keyword):
    return filters.find_one({"keyword": keyword.lower()})

def get_all_keywords():
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def set_fsub(cid):
    settings.update_one({"key": "fsub"}, {"$set": {"value": cid}}, upsert=True)

def get_fsub():
    res = settings.find_one({"key": "fsub"})
    return res['value'] if res else None
