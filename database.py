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

def is_admin(uid):
    if str(uid) == str(config.OWNER_ID): return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_user(uid): users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)
def get_all_users(): return [u['_id'] for u in users.find()]
def add_group(chat_id, title): groups.update_one({"_id": str(chat_id)}, {"$set": {"title": title}}, upsert=True)
def del_group(chat_id): groups.delete_one({"_id": str(chat_id)})
def get_all_groups(): return [g['_id'] for g in groups.find()]

def add_filter(keyword, data):
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": data}, upsert=True)

def get_filter(keyword): return filters.find_one({"keyword": keyword.lower().strip()})
def delete_filter(keyword): return filters.delete_one({"keyword": keyword.lower().strip()}).deleted_count
def delete_all_filters(): return filters.delete_many({}).deleted_count
def get_all_keywords(): return [f['keyword'] for f in filters.find({}, {"keyword": 1})]
def get_all_filters_list(): return list(filters.find({}, {"keyword": 1, "title": 1}))

def add_fsub_chnl(chat_id, title, mode): fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"title": title, "mode": mode}}, upsert=True)
def get_all_fsub(): return list(fsub_col.find())
def del_fsub_chnl(chat_id): return fsub_col.delete_one({"_id": str(chat_id)}).deleted_co
def get_index_results(letter):
    """MongoDB regex use karke fast results nikalna"""
    query = {"keyword": {"$regex": f"^{letter.lower()}"}}
    return list(filters.find(query))
