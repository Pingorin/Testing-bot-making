# database.py

import motor.motor_asyncio
from info import DB_URI

class Database:
    def __init__(self, uri, database_name="telegram_bot"):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.files = self.db.files

    async def add_file(self, file_data):
        try:
            await self.files.insert_one(file_data)
            return True, False  # Saved, Not Duplicate
        except Exception: # DuplicateKeyError
            return False, True # Not Saved, Duplicate

    async def find_files(self, query, page=1, limit=10):
        offset = (page - 1) * limit
        # टेक्स्ट सर्च के लिए regex का उपयोग करें (case-insensitive)
        cursor = self.files.find({'file_name': {'$regex': query, '$options': 'i'}})
        total = await self.files.count_documents({'file_name': {'$regex': query, '$options': 'i'}})
        cursor.skip(offset).limit(limit)
        results = await cursor.to_list(length=limit)
        return results, total

    async def get_file(self, file_id):
        return await self.files.find_one({'_id': file_id})

db = Database(DB_URI)
