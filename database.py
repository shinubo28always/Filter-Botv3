from pymongo import MongoClient
import config

# MongoDB Connection Setup
client = MongoClient(config.MONGO_URI)
db = client['anime_filter_pro'] # Database Name

# Collections
users = db['users']
filters = db['filters']
settings = db['settings']
admins = db['admins']

def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def is_admin(uid):
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_filter(keyword, data):
    # Ensure IDs are integers for Telegram functions
    data['db_mid'] = int(data['db_mid'])
    data['source_cid'] = int(data['source_cid'])
    filters.update_one({"keyword": keyword.lower()}, {"$set": data}, upsert=True)

def get_filter(keyword):
    return filters.find_one({"keyword": keyword.lower()})

def delete_filter(keyword):
    return filters.delete_one({"keyword": keyword.lower()}).deleted_count

def delete_all_filters():
    return filters.delete_many({}).deleted_count

def get_all_keywords():
    # Saare keywords ki list nikalne ke liye
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    # /filters command ke liye list nikalna
    return list(filters.find({}, {"keyword": 1, "title": 1}))

def set_fsub(cid):
    settings.update_one({"key": "fsub"}, {"$set": {"value": str(cid)}}, upsert=True)

def get_fsub():
    res = settings.find_one({"key": "fsub"})
    return res['value'] if res else None
