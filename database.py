from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client['anime_filter_pro'] # New DB for clean start

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
    # Ensure IDs are integers before saving
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
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    return list(filters.find({}, {"keyword": 1, "title": 1}))from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client['anime_filter_pro'] # New DB for clean start

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
    # Ensure IDs are integers before saving
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
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    return list(filters.find({}, {"keyword": 1, "title": 1}))
