from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client['anime_pro_database']

users = db['users']
filters = db['filters']
admins = db['admins']
settings = db['settings']
requests_db = db['requests']

# User
def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def get_all_users():
    return [u['_id'] for u in users.find()]

# Admin
def is_admin(uid):
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_admin(uid):
    admins.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def del_admin(uid):
    return admins.delete_one({"_id": str(uid)}).deleted_count

def get_all_admins():
    return [a['_id'] for a in admins.find()]

# Filter
def add_filter(keyword, data):
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

# FSub & Request
def set_fsub(cid):
    settings.update_one({"key": "fsub"}, {"$set": {"value": str(cid)}}, upsert=True)

def get_fsub():
    res = settings.find_one({"key": "fsub"})
    return res['value'] if res else None

def save_request(uid, name, query):
    requests_db.insert_one({"uid": str(uid), "name": name, "query": query})
