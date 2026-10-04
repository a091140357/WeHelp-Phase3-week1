from fastapi import FastAPI, Form, File, UploadFile
import shutil, os, time
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
import boto3

app = FastAPI()

load_dotenv()
mysql_host = os.getenv("mysql_host")
mysql_user = os.getenv("mysql_user")
mysql_password = os.getenv("mysql_password")
mysql_database = os.getenv("mysql_database")

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY,
    region_name = REGION_NAME
)

try:
	db_pool = pooling.MySQLConnectionPool(
		pool_name = "myDBpool",
		pool_size = 5,
		pool_reset_session = True,
		host = mysql_host,
		user = mysql_user,
		password = mysql_password,
		database = mysql_database
	)
	print(f"{"-"*40}連線池建立成功{"-"*40}")
     
except Exception as e:
	print(f"{"-"*40}連線池建立失敗 {e}{"-"*40}")
	db_pool = None

@app.get("/")
def home_page():
    return FileResponse("static/index.html")

@app.get("/api/message")
def get_message():
    connection = None
    cursor = None
    try:
        connection = db_pool.get_connection()
        cursor = connection.cursor(dictionary = True)   

        cursor.execute("select * from message")
        data = cursor.fetchall()

        return {"data":data}
        
    except Exception as e:
        return JSONResponse(
			status_code = 500,
			content = {
				"error":True,
				"message":str(e)
			})
	
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

     

@app.post("/api/message")
def save_message(
    message:str = Form(""),
    image:UploadFile | None = File(None)
):
    image_url = ""
    if image:
        if not image.content_type.startswith("image/"):
             return JSONResponse(
                  status_code = 400,
                  content = {
                       "error":True,
                       "message":"上傳檔案格式錯誤"
                  }
             )

        timestamp = int(time.time())
        filename = f"{timestamp}_{image.filename}"

        try:
             s3_client.upload_fileobj(
                  image.file,
                  BUCKET_NAME,
                  filename,
                  ExtraArgs = {"ContentType":image.content_type}
             )
             image_url = f"https://d3jsg4z3dj7kth.cloudfront.net/{filename}"
             print("圖片上傳成功")

        except Exception as e:
             return JSONResponse(
                status_code = 500,
                content={
                    "error":True, 
                    "message":f"上傳失敗{e}"
                }
            )
        


    connection = None
    cursor = None

    try:
        connection = db_pool.get_connection()
        cursor = connection.cursor(dictionary = True)

        cursor.execute("insert into message(user_message, pic_url) values(%s, %s)",(message, image_url))
        connection.commit()

        return {
             "ok":True,
             "message":message,
             "pic":image_url
        }
    
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {
                "error":True,
                "message":str(e)
            })
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()



app.mount("/static", StaticFiles(directory="static"), name="static")