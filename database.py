### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
from pymongo import MongoClient
import config
import sys

DB_NAME = "AniReal_Filter_Bot"

try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]
    db.command('ping')
    print(f"✅ MongoDB Connected: {DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB Error: {e}")
    sys.exit(1)

users = db['users']
groups = db['groups']
filters = db['filters']
admins = db['admins']
fsub_col = db['fsub_channels']

# --- ADMIN LOGIC ---
def is_admin(uid):
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_admin(uid):
    admins.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def del_admin(uid):
    return admins.delete_one({"_id": str(uid)}).deleted_count

def get_all_admins():
    """Missing function fixed here"""
    return [a['_id'] for a in admins.find()]

# --- USER & GROUP ---
def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def present_user(uid):
    return users.find_one({"_id": str(uid)}) is not None

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

# --- FILTERS & INDEXING ---
def add_filter(keyword, data):
    if 'type' not in data: data['type'] = 'anime'
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": data}, upsert=True)

def get_filter(keyword):
    return filters.find_one({"keyword": keyword.lower().strip()})

def get_index_results(letter):
    """Fast indexing using Regex"""
    query = {"keyword": {"$regex": f"^{letter.lower()}"}}
    return list(filters.find(query))

def delete_filter(keyword):
    return filters.delete_one({"keyword": keyword.lower().strip()}).deleted_count

def delete_all_filters():
    return filters.delete_many({}).deleted_count

def get_all_keywords():
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    return list(filters.find({}, {"keyword": 1, "title": 1}))

# --- FSUB LOGIC ---
def add_fsub_chnl(chat_id, title, mode):
    fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"title": title, "mode": mode}}, upsert=True)

def get_all_fsub():
    return list(fsub_col.find())

def get_fsub_info(chat_id):
    return fsub_col.find_one({"_id": str(chat_id)})

def update_fsub_mode(chat_id, mode):
    fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"mode": mode}})

def del_fsub_chnl(chat_id):
    return fsub_col.delete_one({"_id": str(chat_id)}).deleted_count

def del_all_fsub_chnls():
    return fsub_col.delete_many({}).deleted_count

def toggle_fsub_mode(chat_id):
    curr = fsub_col.find_one({"_id": str(chat_id)})
    if not curr: return None
    new_mode = "request" if curr['mode'] == "normal" else "normal"
    fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"mode": new_mode}})
    return new_mode

# --- REQUESTS ---
def save_request(uid, name, query):
    db['requests'].insert_one({"uid": str(uid), "name": name, "query": query})
