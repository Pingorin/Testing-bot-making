# database.py

import motor.motor_asyncio
from info import DB_URI

class Database:
    def __init__(self, uri, database_name="telegram_bot"):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.files = self.db.files

    async def add_file(self, file_data):
        """
        फाइल को डेटाबेस में सेव करता है।
        Returns: (True, False) if saved, (False, True) if duplicate.
        """
        try:
            # file_id को _id के रूप में उपयोग करके डुप्लिकेट से बचें
            await self.files.insert_one(file_data)
            return True, False  # Saved, Not Duplicate
        except Exception: # DuplicateKeyError
            return False, True # Not Saved, Duplicate

    async def find_files(self, query, page=1, limit=10):
        """
        दिए गए क्वेरी के लिए फाइलों को खोजता है।
        """
        offset = (page - 1) * limit
        # टेक्स्ट सर्च के लिए regex का उपयोग करें (case-insensitive)
        cursor = self.files.find({'file_name': {'$regex': query, '$options': 'i'}})
        
        # कुल काउंट
        total = await self.files.count_documents({'file_name': {'$regex': query, '$options': 'i'}})
        
        # पेज के हिसाब से रिजल्ट्स
        cursor.skip(offset).limit(limit)
        
        results = await cursor.to_list(length=limit)
        return results, total

    async def get_file(self, file_id):
        """
        file_id का उपयोग करके एक फाइल प्राप्त करता है।
        """
        return await self.files.find_one({'_id': file_id})


db = Database(DB_URI)
