### This bot is Created By UNRATED CODER --- Join @UNRATED_CODER ###
from pymongo import MongoClient
import config, sys

DB_NAME = "AniReal_Filter_Bot"
try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]; db.command('ping')
except Exception as e:
    print(f"❌ MongoDB Error: {e}"); sys.exit(1)

users, groups, filters, admins, fsub_col = db['users'], db['groups'], db['filters'], db['admins'], db['fsub_channels']

def add_user(uid): users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)
def get_all_users(): return [u['_id'] for u in users.find()]
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
def get_index_results(letter): return list(filters.find({"keyword": {"$regex": f"^{letter.lower()}"}, "$or": [{"show_in_index": True}, {"type": "anime"}]}))

def add_fsub_chnl(chat_id, title, mode): fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"title": title, "mode": mode}}, upsert=True)
def get_all_fsub(): return list(fsub_col.find())
def del_fsub_chnl(chat_id): return fsub_col.delete_one({"_id": str(chat_id)}).deleted_count
