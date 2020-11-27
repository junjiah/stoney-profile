import hashlib
import os
import sqlite3
import sys
import time

import requests
import tweepy

STONEY_ID = 292830390
DB_PATH = "profiles.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = on;")

# Create DB
if not os.path.exists(DB_PATH):
    print("creating DB")
    sql = """
    create table if not exists PROFILES(
        PIC_ID BINARY PRIMAY KEY UNIQUE,
        DATA BLOB);"""
    conn.execute(sql)
    sql = """
    create table if not exists PROFILE_HISTORY(
        UPDATED_AT INTEGER PRIMARY KEY,
        PIC_ID BINARY,
        foreign key (PIC_ID) references PROFILES(PIC_ID));"""
    conn.execute(sql)

# Connect to twitter and fetch profile pictures
with open("twitter-credentials", "r") as f:
    lines = f.readlines()
    key, secret = lines[0].strip(), lines[1].strip()

auth = tweepy.OAuthHandler(key, secret)
api = tweepy.API(auth)
stoney = api.get_user(STONEY_ID)
profile_img_url = stoney.profile_image_url.replace("_normal.", "_400x400.")
# print(profile_img_url)
req = requests.get(profile_img_url, stream=True)
if req.status_code != 200:
    print("failed to download profile image", req.status_code, req.reason)
    sys.exit(1)

req.raw.decode_content = True
pic_blob = req.raw.read()
pic_id = hashlib.md5(pic_blob).digest()

# Fetch latest one to see if there is any change
cursor = conn.cursor()
sql = "select PIC_ID from PROFILE_HISTORY order by UPDATED_AT desc limit 1;"
cursor.execute(sql)
last_pic_id = cursor.fetchone()[0]
if last_pic_id == pic_id:
    print("no change")
    sys.exit(0)

sql = "insert or ignore into PROFILES(PIC_ID, DATA) values(?, ?);"
conn.execute(sql, [sqlite3.Binary(pic_id), sqlite3.Binary(pic_blob)])
conn.commit()

sql = "insert into PROFILE_HISTORY(UPDATED_AT, PIC_ID) values(?, ?);"
conn.execute(sql, [int(time.time()), sqlite3.Binary(pic_id)])
conn.commit()

conn.close()
