# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
from pymongo import MongoClient
import config
import sys
import time

# --- DATABASE CONFIGURATION ---
DB_NAME = "AniReal_Filter_Bot"

try:
    # 10s timeout taaki Render par bot stuck na ho
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]
    db.command('ping')
    print(f"✅ MongoDB Connected: {DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    sys.exit(1)

# Collections
users = db['users']
groups = db['groups']
filters = db['filters']
admins = db['admins']
settings = db['settings']
requests_db = db['requests']
fsub_col = db['fsub_channels']

# ==========================================
# 👮 ADMIN & USER LOGIC
# ==========================================

def is_admin(uid):
    """Owner ya Database Admin check karein"""
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_admin(uid):
    admins.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def del_admin(uid):
    return admins.delete_one({"_id": str(uid)}).deleted_count

def get_all_admins():
    return [a['_id'] for a in admins.find()]

def add_user(uid):
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def present_user(uid):
    return users.find_one({"_id": str(uid)}) is not None

def get_all_users():
    return [u['_id'] for u in users.find()]

def del_user(uid):
    users.delete_one({"_id": str(uid)})

# ==========================================
# 🏘️ GROUP TRACKING
# ==========================================

def add_group(chat_id, title):
    groups.update_one({"_id": str(chat_id)}, {"$set": {"title": title}}, upsert=True)

def del_group(chat_id):
    groups.delete_one({"_id": str(chat_id)})

def get_all_groups():
    return [g['_id'] for g in groups.find()]

# ==========================================
# 📂 FILTER LOGIC
# ==========================================

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

# ==========================================
# 📢 MULTI-FSUB LOGIC
# ==========================================

def add_fsub_chnl(chat_id, title, mode):
    fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"title": title, "mode": mode}}, upsert=True)

def update_fsub_mode(chat_id, mode):
    fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"mode": mode}})

def get_fsub_info(chat_id):
    return fsub_col.find_one({"_id": str(chat_id)})

def get_all_fsub():
    return list(fsub_col.find())

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

# ---- MAINTENANCE MODE ----

def set_maintenance(status: bool):
    db.config.update_one(
        {"_id": "maintenance"},
        {"$set": {"status": status}},
        upsert=True
    )

def is_maintenance():
    data = db.config.find_one({"_id": "maintenance"})
    return data.get("status", False) if data else False
    
# ==========================================
# 📩 REQUEST LOGIC
# ==========================================

def save_request(uid, name, query):
    requests_db.insert_one({"uid": str(uid), "name": name, "query": query, "time": time.ctime()})

# Join & Support Us! @DogeshBhai_Pure_Bot
