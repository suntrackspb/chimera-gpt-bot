import os
import json
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class MEncode:
    def __init__(self, data):
        self.data = MongoJSONEncoder().encode(data)

    def encode(self):
        return json.loads(self.data)


def connect():
    conn = MongoClient(host=os.getenv("DB_HOST"),
                       port=int(os.getenv("DB_PORT")),
                       username=os.getenv("DB_USER"),
                       password=os.getenv("DB_PASS"),
                       authSource='admin', )
    db = conn.gptBot
    return db


class Users:
    def __init__(self):
        self.conn = connect().users

    def add_user(self, message):
        tid = message.chat.id
        first_name = message.chat.first_name
        last_name = message.chat.last_name
        username = message.chat.username
        data = {
            "tid": tid,
            "firstname": first_name,
            "lastname": last_name,
            "username": username,
            "total_per_day": 10000,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "imgCount": 0,
            "isAdmin": False,
            "isBlocked": False,
            "last_used": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        }
        return self.conn.insert_one(data).inserted_id

    def check_user(self, message):
        tid = message.chat.id
        user = self.conn.find_one({"tid": tid})
        self.upd_last_used(tid)
        if user is None:
            _id = self.add_user(message)
            print(f"User {tid} added to base, id: {_id}")

    def get_users(self):
        return self.conn.find({},
                              {
                                  "_id": 0,
                                  "tid": 1,
                                  "username": 1,
                                  "firstname": 1,
                                  "lastname": 1,
                                  "total_tokens": 1,
                                  "imgCount": 1,
                                  "isBlocked": 1,
                              }
                              ).sort("total_tokens", 1)

    def get_user(self, tid):
        data = self.conn.find_one({"tid": tid})
        return data

    def check_admin(self, tid):
        user = self.conn.find_one({"tid": tid})
        return user['isAdmin']

    def set_admin(self, tid):
        self.conn.update_one({"tid": tid}, [{'$set': {'isAdmin': {'$not': '$isAdmin'}}}])

    def check_block(self, tid):
        user = self.conn.find_one({"tid": tid})
        return user['isBlocked']

    def set_block(self, tid):
        self.conn.update_one({"tid": tid}, [{'$set': {'isBlocked': {'$not': '$isBlocked'}}}])

    def get_limit(self, tid):
        limit = self.conn.find_one({"tid": tid})
        return limit['total_per_day']

    def set_limit(self, tid, limit):
        self.conn.update_one({"tid": tid}, {"$set": {"total_per_day": limit}})

    def check_limit(self, tid):
        user = self.conn.find_one({"tid": tid})
        count = DayCounter().get_count(tid)
        if count >= user['total_per_day']:
            return True
        return False

    def upd_last_used(self, tid):
        self.conn.update_one({"tid": tid}, {"$set": {"last_used": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})

    def upd_gpt_count(self, tid, usage):
        self.upd_last_used(tid)
        return self.conn.update_one(
            {"tid": tid},
            {
                "$inc":
                    {
                        "prompt_tokens": usage['prompt_tokens'],
                        "completion_tokens": usage['completion_tokens'],
                        "total_tokens": usage['total_tokens'],
                    }
            }
        )

    def upd_img_count(self, tid):
        self.upd_last_used(tid)
        return self.conn.update_one({"tid": tid}, {"$inc": {"imgCount": 1}})


class GPTRequest:
    def __init__(self):
        self.conn = connect().gpt_ai

    def add_request(self, tid, text):
        data = {
            "tid": tid,
            "type": "user",
            "text": text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.conn.insert_one(data)

    def add_answer(self, tid, text):
        data = {
            "tid": tid,
            "type": "gpt",
            "text": text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.conn.insert_one(data)


class IMGRequest:
    def __init__(self):
        self.conn = connect().img_ai

    def add_row(self, tid, filename, prompt, style):
        data = {
            "tid": tid,
            "type": "ans",
            "img_name": filename,
            "prompt": prompt,
            "style": style,
            "public": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        Users().upd_img_count(tid)
        self.conn.insert_one(data)

    def update_public(self, filename):
        return self.conn.update_one({"img_name": filename}, {"$set": {"public": True}})

    def get_public_images(self, limit, skip):
        return self.conn.find({
            "public": True
        }, {
            "_id": 1,
            "img_name": 1,
            "prompt": 1,
            "style": 1}).sort("created_at", -1).limit(limit).skip(skip)


class DayCounter:
    def __init__(self):
        self.conn = connect().day_counter

    def add_day_limit(self, tid, total_count):
        data = {
            "tid": tid,
            "count": total_count,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        self.conn.insert_one(data)

    def update_day_limit(self, tid, total_count):
        return self.conn.update_one(
            {"tid": tid, "date": datetime.now().strftime("%Y-%m-%d")},
            {
                "$inc": {"count": total_count}
            }
        )

    def execute_counter(self, tid, total_count):
        doc = self.conn.find_one({"tid": tid, "date": datetime.now().strftime("%Y-%m-%d")})
        if doc is None:
            self.add_day_limit(tid, total_count)
        else:
            self.update_day_limit(tid, total_count)

    def get_count(self, tid):
        count = self.conn.find_one({"tid": tid, "date": datetime.now().strftime("%Y-%m-%d")})
        if count is None:
            return 0
        return count['count']

    def drop_limit(self, tid):
        self.conn.update_one({"tid": tid, "date": datetime.now().strftime("%Y-%m-%d")}, {"$set": {"count": 0}})
