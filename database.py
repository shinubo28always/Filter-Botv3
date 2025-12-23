from pymongo import MongoClient
import config
import sys

DB_NAME = "AniReal_Filter_Bot"

try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]
    db.command('ping')
    print(f"✅ MongoDB Connected to: {DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB Error: {e}")
    sys.exit(1)

users = db['users']
groups = db['groups']
filters = db['filters']
admins = db['admins']
settings = db['settings']

# --- ADMIN LOGIC ---
def is_admin(uid):
    # Owner ya Admin collection mein check karna
    if str(uid) == str(config.OWNER_ID):
        return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_admin(uid):
    admins.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def del_admin(uid):
    return admins.delete_one({"_id": str(uid)}).deleted_count

def get_all_admins():
    return [a['_id'] for a in admins.find()]

# --- USER & GROUP ---
def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def get_all_users():
    return [u['_id'] for u in users.find()]

def del_user(uid):
    users.delete_one({"_id": str(uid)})

def add_group(chat_id, title):
    groups.update_one({"_id": str(chat_id)}, {"$set": {"title": title}}, upsert=True)

def get_all_groups():
    return [g['_id'] for g in groups.find()]

def del_group(chat_id):
    groups.delete_one({"_id": str(chat_id)})

# --- FILTERS ---
def add_filter(keyword, data):
    payload = {
        "title": data['title'],
        "db_mid": int(data['db_mid']),
        "source_cid": int(data['source_cid'])
    }
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": payload}, upsert=True)

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

# --- FSUB ---
def set_fsub(cid):
    settings.update_one({"key": "fsub"}, {"$set": {"value": str(cid)}}, upsert=True)

def get_fsub():
    res = settings.find_one({"key": "fsub"})
    return res['value'] if res else None
