import os, mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
import time

load_dotenv()

mysql_host = os.getenv("mysql_host")
mysql_user = os.getenv("mysql_user")
mysql_password = os.getenv("mysql_password")
mysql_database = os.getenv("mysql_database")

db = None
cursor = None

retries = 10
while retries > 0:
    try:
        db = mysql.connector.connect(
            host = mysql_host,
            user = mysql_user,
            password = mysql_password,
        )

        if db.is_connected():
            print("mysql連線成功")
            break

    except Error as e:
        print(e)
        retries -= 1
        time.sleep(3)

if not db or not db.is_connected():
    print("連線不到mysql")
    exit(1)

try:
    cursor = db.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_database};")
    cursor.execute(f"use {mysql_database};")

    cursor.execute("""
    create table if not exists message(
                id int UNSIGNED not null auto_increment primary key,
                user_message varchar(1000),
                pic_url varchar(200),
                create_at datetime default current_timestamp)
                """)
    db.commit()
    print(f'{"-"*50}user資料庫建立完成{"-"*50}')

except Error as e:
    print(e)

finally:
    if cursor is not None:
        cursor.close()
    if db is not None and db.is_connected():
        db.close()
        print("資料庫關閉")