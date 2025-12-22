from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client['anime_pro_v4'] # Fresh DB name for testing

users = db['users']
filters = db['filters']
admins = db['admins']
settings = db['settings']

def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def is_admin(uid):
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_filter(keyword, data):
    # Data save karte waqt integer force karna
    filter_data = {
        "title": str(data['title']),
        "db_mid": int(data['db_mid']),
        "source_cid": int(data['source_cid'])
    }
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": filter_data}, upsert=True)

def get_filter(keyword):
    return filters.find_one({"keyword": keyword.lower().strip()})

def delete_filter(keyword):
    return filters.delete_one({"keyword": keyword.lower().strip()}).deleted_count

def get_all_keywords():
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    return list(filters.find({}, {"keyword": 1, "title": 1}))
