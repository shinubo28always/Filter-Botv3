### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
from pymongo import MongoClient
import config, sys, time

DB_NAME = "AniReal_Filter_Bot"
try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]; db.command('ping')
    print(f"✅ MongoDB Connected: {DB_NAME}")
except Exception as e:
    print(f"❌ MongoDB Error: {e}"); sys.exit(1)

users, groups, filters, admins, fsub_col, req_col, settings, banned_col, track_col = db['users'], db['groups'], db['filters'], db['admins'], db['fsub_channels'], db['requests'], db['settings'], db['banned'], db['top_searches']

def add_user(uid): users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)
def get_all_users(): return [u['_id'] for u in users.find()]
def del_user(uid): return users.delete_one({"_id": str(uid)}).deleted_count
def is_admin(uid): return str(uid) == str(config.OWNER_ID) or admins.find_one({"_id": str(uid)}) is not None
def add_admin(uid): admins.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)
def del_admin(uid): return admins.delete_one({"_id": str(uid)}).deleted_count
def get_all_admins(): return [a['_id'] for a in admins.find()]
def add_group(chat_id, title): groups.update_one({"_id": str(chat_id)}, {"$set": {"title": title}}, upsert=True)
def get_all_groups(): return [g['_id'] for g in groups.find()]
def del_group(chat_id): groups.delete_one({"_id": str(chat_id)})

def add_filter(keyword, data):
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": data}, upsert=True)

def get_filter(keyword): return filters.find_one({"keyword": keyword.lower().strip()})
def get_filter_by_mid(mid): return filters.find_one({"db_mid": int(mid)})
def get_all_keywords(): return [f['keyword'] for f in filters.find({}, {"keyword": 1})]
def get_all_filters_list(): return list(filters.find({}, {"keyword": 1, "title": 1}))

# --- FIXED INDEX QUERY ---
def get_index_results(letter): 
    # Logic: Match keyword starting with letter AND (Not hidden by user)
    query = {
        "keyword": {"$regex": f"^{letter.lower()}"},
        "show_in_index": {"$ne": False} # Sab dikhao, jab tak explicitly False na ho
    }
    return list(filters.find(query))

def delete_filter(keyword): return filters.delete_one({"keyword": keyword.lower().strip()}).deleted_count
def delete_all_filters(): return filters.delete_many({}).deleted_count
def add_fsub_chnl(chat_id, title, mode): fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"title": title, "mode": mode}}, upsert=True)
def get_all_fsub(): return list(fsub_col.find())
def get_fsub_info(chat_id): return fsub_col.find_one({"_id": str(chat_id)})
def update_fsub_mode(chat_id, mode): fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"mode": mode}})
def del_fsub_chnl(chat_id): return fsub_col.delete_one({"_id": str(chat_id)}).deleted_count
def del_all_fsub_chnls(): return fsub_col.delete_many({}).deleted_count

def present_user(uid): return users.find_one({"_id": str(uid)}) is not None
def present_group(chat_id): return groups.find_one({"_id": str(chat_id)}) is not None

def save_request(uid, first_name, query):
    req_col.insert_one({
        "uid": str(uid),
        "first_name": first_name,
        "query": query,
        "time": time.time()
    })

def get_pending_requests(): return list(req_col.find().sort("time", -1))
def delete_request(uid, query): return req_col.delete_one({"uid": str(uid), "query": query}).deleted_count
def delete_all_requests(): return req_col.delete_many({}).deleted_count
def cleanup_old_requests(days=30):
    limit = time.time() - (days * 24 * 3600)
    return req_col.delete_many({"time": {"$lt": limit}}).deleted_count

def set_maintenance(status): settings.update_one({"_id": "maintenance"}, {"$set": {"status": bool(status)}}, upsert=True)
def get_maintenance():
    data = settings.find_one({"_id": "maintenance"})
    return data['status'] if data else False

def ban_user(uid): banned_col.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)
def unban_user(uid): return banned_col.delete_one({"_id": str(uid)}).deleted_count
def is_banned(uid): return banned_col.find_one({"_id": str(uid)}) is not None

def track_search(keyword): track_col.update_one({"keyword": keyword.lower().strip()}, {"$inc": {"count": 1}}, upsert=True)
def get_top_searches(limit=10): return list(track_col.find().sort("count", -1).limit(limit))
