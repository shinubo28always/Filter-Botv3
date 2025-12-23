from pymongo import MongoClient
import config
import sys

# --- DATABASE CONFIGURATION (DO NOT CHANGE NAME) ---
DB_NAME = "AniReal_Filter_Bot"

try:
    # Connection with 10s timeout to prevent hanging on Render
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]
    # Ping test to confirm connection
    client.admin.command('ping')
    print(f"✅ MongoDB Connected Successfully to: {DB_NAME}")
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
# 👮 ADMIN MANAGEMENT
# ==========================================

def is_admin(uid):
    """Check if a user is the Owner or an Authorized Admin"""
    if str(uid) == str(config.OWNER_ID):
        return True
    return admins.find_one({"_id": str(uid)}) is not None

def add_admin(uid):
    """Add a new admin to the database"""
    admins.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def del_admin(uid):
    """Remove an admin from the database"""
    return admins.delete_one({"_id": str(uid)}).deleted_count

def get_all_admins():
    """Get list of all admin IDs"""
    return [a['_id'] for a in admins.find()]

# ==========================================
# 👤 USER MANAGEMENT
# ==========================================

def add_user(uid):
    """Register a new user in the database"""
    users.update_one({"_id": str(uid)}, {"$set": {"_id": str(uid)}}, upsert=True)

def present_user(uid):
    """Check if a user exists in the database (has started the bot)"""
    return users.find_one({"_id": str(uid)}) is not None

def get_all_users():
    """Get list of all registered user IDs"""
    return [u['_id'] for u in users.find()]

def del_user(uid):
    """Delete a user from the database"""
    users.delete_one({"_id": str(uid)})

# ==========================================
# 🏘️ GROUP MANAGEMENT
# ==========================================

def add_group(chat_id, title):
    """Register a group for broadcasting"""
    groups.update_one({"_id": str(chat_id)}, {"$set": {"title": title}}, upsert=True)

def del_group(chat_id):
    """Remove a group from the database"""
    groups.delete_one({"_id": str(chat_id)})

def get_all_groups():
    """Get list of all authorized group IDs"""
    return [g['_id'] for g in groups.find()]

# ==========================================
# 📂 FILTER MANAGEMENT
# ==========================================

def add_filter(keyword, data):
    """Save a filter with Post ID and Source Channel ID"""
    payload = {
        "title": data['title'],
        "db_mid": int(data['db_mid']),     # Message ID in DB Channel
        "source_cid": int(data['source_cid']) # Original Anime Channel ID
    }
    filters.update_one({"keyword": keyword.lower().strip()}, {"$set": payload}, upsert=True)

def get_filter(keyword):
    """Fetch filter data for a specific keyword"""
    return filters.find_one({"keyword": keyword.lower().strip()})

def delete_filter(keyword):
    """Delete a specific filter keyword"""
    return filters.delete_one({"keyword": keyword.lower().strip()}).deleted_count

def delete_all_filters():
    """Clear all filters from the database"""
    return filters.delete_many({}).deleted_count

def get_all_keywords():
    """Get all saved keywords for fuzzy search"""
    return [f['keyword'] for f in filters.find({}, {"keyword": 1})]

def get_all_filters_list():
    """Get full list of keywords and their titles"""
    return list(filters.find({}, {"keyword": 1, "title": 1}))

# ==========================================
# 📢 FSUB MANAGEMENT (MULTI-CHANNEL)
# ==========================================

def add_fsub_chnl(chat_id, title, mode):
    """Add a new Force Subscribe channel"""
    fsub_col.update_one(
        {"_id": str(chat_id)}, 
        {"$set": {"title": title, "mode": mode}}, 
        upsert=True
    )

def update_fsub_mode(chat_id, mode):
    """Change mode (Normal/Request) of an FSub channel"""
    fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"mode": mode}})

def get_fsub_info(chat_id):
    """Get details of a specific FSub channel"""
    return fsub_col.find_one({"_id": str(chat_id)})

def get_all_fsub():
    """Get all FSub channels"""
    return list(fsub_col.find())

def del_fsub_chnl(chat_id):
    """Delete an FSub channel"""
    return fsub_col.delete_one({"_id": str(chat_id)}).deleted_count

def del_all_fsub_chnls():
    """Clear all FSub channels"""
    return fsub_col.delete_many({}).deleted_count

def toggle_fsub_mode(chat_id):
    """Switch between Normal and Request mode"""
    curr = fsub_col.find_one({"_id": str(chat_id)})
    if not curr: return None
    new_mode = "request" if curr['mode'] == "normal" else "normal"
    fsub_col.update_one({"_id": str(chat_id)}, {"$set": {"mode": new_mode}})
    return new_mode

# ==========================================
# 📩 REQUEST MANAGEMENT
# ==========================================

def save_request(uid, name, query):
    """Store anime requests for admin review"""
    import time
    requests_db.insert_one({
        "uid": str(uid), 
        "name": name, 
        "query": query, 
        "time": time.ctime()
    })
