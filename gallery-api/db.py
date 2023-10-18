import os
import json
from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("../.env.local")


def get_date(formats: str):
    return datetime.strptime(datetime.now().strftime(formats), formats)


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

    def upd_last_used(self, tid):
        self.conn.update_one({"tid": tid}, {"$set": {"last_used": get_date("%Y-%m-%d %H:%M:%S")}})

    def upd_img_count(self, tid):
        self.upd_last_used(tid)
        return self.conn.update_one({"tid": tid}, {"$inc": {"imgCount": 1}})


class IMGRequest:
    def __init__(self):
        self.conn = connect().img_ai

    def get_public_images(self, limit, skip):
        return self.conn.find({
            "public": True
        }, {
            "_id": 1,
            "img_name": 1,
            "prompt": 1,
            "style": 1}).sort("created_at", -1).limit(limit).skip(skip)
