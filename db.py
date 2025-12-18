import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import firestore_async
import asyncio

class DataBase:
    _initialized = False
    ref_name = "" 

    @classmethod
    def connect(cls, path: str):
        if not cls._initialized:
            cred = credentials.Certificate(path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://softc-7cb3c-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
            cls._initialized = True
        else:
            print("Firebase already initialized.")

    @classmethod
    async def load_all(cls):
        try:
            datas = db.reference(cls.ref_name).get()
        
            if datas:
                return datas
                
        except Exception as e:
            print(f"Error loading all data from {cls.ref_name}: {e}")
            return False

    @classmethod
    async def load(cls, key: str):
        try:
            data = db.reference(f'{cls.ref_name}/{key}').get()

            if data:
                return data

        except Exception as e:
            print(f"Error loading data from {cls.ref_name} with key {key}: {e}")
            return False

class UserDB(DataBase):
    ref_name = "Users" 

    @classmethod
    async def upload(cls, user: dict):
        try:
            db.reference(f'{cls.ref_name}/{user["id"]}').set(user)

        except Exception as e:
            print(f"Error uploading user: {e}")

    @classmethod
    async def update(cls, user_id: str, updates: dict):
        try:
            await db.reference(f'{cls.ref_name}/{user_id}').update(updates)

        except Exception as e:
            print(f"Error updating user {user_id}: {e}")

    @classmethod
    async def delete(cls, user_id: str):
        try:
            await db.reference(f'{cls.ref_name}/{user_id}').delete()

        except Exception as e:
            print(f"Error deleting user {user_id}: {e}")