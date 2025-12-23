from pymongo import MongoClient
import config
import sys

try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client['AniReal_Filter_Bot']
    db.command('ping')
except Exception as e:
    print(f"❌ MongoDB Error: {e}")
    sys.exit(1)

users = db['users']
groups = db['groups']
filters = db['filters']
admins = db['admins']
requests_db = db['requests']

# Users
def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def get_all_users():
    return [u['_id'] for u in users.find()]

def del_user(uid):
    users.delete_one({"_id": str(uid)})

# Groups
def add_group(chat_id, title):
    groups.update_one({"_id": str(chat_id)}, {"$set": {"title": title}}, upsert=True)

def get_all_groups():
    return [g['_id'] for g in groups.find()]

def del_group(chat_id):
    groups.delete_one({"_id": str(chat_id)})

# Admins
def is_admin(uid):
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_admin(uid):
    admins.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def del_admin(uid):
    return admins.delete_one({"_id": str(uid)}).deleted_count

def get_all_admins():
    return [a['_id'] for a in admins.find()]

# Filters
def add_filter(keyword, data):
    data['db_mid'] = int(data['db_mid'])
    data['source_cid'] = int(data['source_cid'])
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": data}, upsert=True)

def get_filter(keyword):
    return filters.find_one({"keyword": keyword.lower().strip()})

def delete_filter(keyword):
    return filters.delete_one({"keyword": keyword.lower().strip()}).deleted_count

def delete_all_filters():
    return filters.delete_many({}).deleted_count

def get_all_keywords():
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    return list(filters.find({}, {"keyword": 1, "title": 1}))

# Requests
def save_request(uid, name, query):
    requests_db.insert_one({"uid": str(uid), "name": name, "query": query})
