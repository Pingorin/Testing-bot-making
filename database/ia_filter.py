from pymongo import MongoClient
from info import DB_URI, DB_NAME

# MongoDB Connection
client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db["files"]

# Files ko save karne ka function
async def add_file(file_id, file_unique_id, file_name, caption):
    try:
        # Duplicate check
        if await collection.find_one({"file_unique_id": file_unique_id}):
            return "duplicate"
        
        await collection.insert_one({
            "file_id": file_id,
            "file_unique_id": file_unique_id,
            "file_name": file_name,
            "caption": caption
        })
        return "saved"
    except Exception as e:
        print(f"Error saving file: {e}")
        return "error"

# Query ke basis par files search karna
async def find_files(query, max_results=10, page=0):
    # Spelling check ke liye aap MongoDB Atlas $search (text) ka upyog kar sakte hain
    # Ya simple regex ka upyog kar sakte hain
    
    query_regex = f".*{query}.*" # Simple regex search
    
    cursor = collection.find({
        "$or": [
            {"file_name": {"$regex": query_regex, "$options": "i"}},
            {"caption": {"$regex": query_regex, "$options": "i"}}
        ]
    })
    
    total_files = await collection.count_documents({
        "$or": [
            {"file_name": {"$regex": query_regex, "$options": "i"}},
            {"caption": {"$regex": query_regex, "$options": "i"}}
        ]
    })
    
    # Pagination
    files = await cursor.skip(page * max_results).limit(max_results).to_list(length=max_results)
    
    return files, total_files

# Channel ki total files count karna (indexing ke liye)
async def total_files_in_channel(client, chat_id):
    # Yeh function Pyrogram client ka upyog karke message count karega
    # Example: count = await client.get_chat_history_count(chat_id)
    # Yahaan hum simplified rakhte hain
    pass 

# File ko uske ID se fetch karna (file bhejme ke liye)
async def get_file_by_id(file_id):
    return await collection.find_one({"file_id": file_id})
  
