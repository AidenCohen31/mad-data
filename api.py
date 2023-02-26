from flask import Flask, request
from flask_cors import CORS
import json
import boto3
from dotenv import load_dotenv
import os
import base64
import io
from datetime import datetime
import requests
from random import random
from sklearn.decomposition import PCA
load_dotenv()
i = 0

bucket = os.environ["BUCKETEER_BUCKET_NAME"]
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
client = boto3.client('s3',    aws_access_key_id=os.environ["BUCKETEER_AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["BUCKETEER_AWS_SECRET_ACCESS_KEY"])
@app.route("/submit", methods=["POST"])
def submit():
    return {"success" : True}

@app.route("/legibility", methods=["GET"])
def legi():
    # im = cv2.imread("img.jpg")
    # gray = cv2.cvtColor(im,  cv2.COLOR_BGR2GRAY)
    # th = cv2.threshold(gray,200,255,cv2.THRESH_BINARY)[1]

    # cny = cv2.Canny(th,100,200)

    # contours, hierarchy = cv2.findContours(cny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # for contour in contours:
    # x,y,w,h = cv2.boundingRect(contour)
    # if(w * h > 100):
    #     rects.append([x,y,w,h])
    
    return {"score" :0.0, "image" : "" }

def latex():
    arr = ["https://latex.codecogs.com/png.image?\dpi{200}\alpha&space;+&space;\frac{2\beta}{\gamma}","https://latex.codecogs.com/png.image?\dpi{200}\int \frac{1}{x} dx = \ln \left| x \right| + C", "https://latex.codecogs.com/png.image?\lim_{x%20\to%200}%20f(x)%20=%208"]
    r = requests.get(arr[i], stream = True)
    i+=1
    return {"image" : base64.b64encode(r.raw)}

@app.route("/files", methods=["GET"])
def files():
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket= bucket)
    ls = []
    for b in page_iterator:
        for file in b['Contents']:
            try:
                metadata = client.head_object(Bucket=bucket, Key=file['Key'])
                data = client.get_object(Bucket=bucket, Key=file["Key"])
                try:
                    ls.append({"metadata" : metadata["ResponseMetadata"] , "name" : file["Key"], "data" :   base64.b64encode(data["Body"].read()) })

                except Exception as e:
                    print(file)
            except Exception as e:
                print(e)
    return json.dumps({"files" : ls}, default=str)

@app.route("/download", methods=["GET"])
def download():
    return {"files" : "b64"}

def formatstr(cid, name=None):
    name = datetime.now().strftime("%m/%d/%Y%H:%M:%S") if name == None else name
    return cid + "/" + name

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"] if "name" in request.form else None
    cid = request.form["id"]
    client.upload_fileobj(io.BytesIO(base64.b64decode(latex()["image"])), bucket, formatstr(cid, name),   ExtraArgs={
        "Metadata": {
            "date": str(datetime.now().strftime("%m/%d/%Y%H:%M:%S"))
        }
    } )
    return {"success": True}
@app.route("/delete", methods=["POST"])
def delete():
    client.delete_object(Bucket=bucket, Key=formatstr(request.form["id"], request.form["name"]))
    return {"success" : True}
@app.route("/id", methods=["GET"])
def id():
    return {"id" : 1}
if __name__ == "__main__":
    app.run(port=5000)
