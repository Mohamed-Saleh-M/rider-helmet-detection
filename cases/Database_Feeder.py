from pymongo import MongoClient
import base64
import pprint
import os
from datetime import datetime
client = MongoClient()
db = client["helmet_surv"]
surv_data = db.surv_data

print("\t\tDATABASE FEEDER\n")

print('DATA FEEDING STARTED AT',(datetime.now()).strftime("%H:%M:%S"),"\n\n")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.environ.get("HELMET_CASES_DIR", os.path.join(BASE_DIR, "Cases"))

list_loc = [f.name for f in os.scandir(path) if f.is_dir()]
for i in list_loc:
    path_i = path + "/" + i
    list_loc_i = [f.name for f in os.scandir(path_i) if f.is_dir()]
    c = 0
    for j in list_loc_i:
        path_j = path_i + "/" + j
        date = j[3:5] + "/" + j[5:7] + "/" + j[7:9]
        time = j[9:11] + ":" + j[11:13] + ":" + j[13:15]
        with open(path_j + "/bike.jpg", "rb") as image2string:
                bike = base64.b64encode(image2string.read())
        with open(path_j + "/numberplate.jpg", "rb") as image2string:
                np = base64.b64encode(image2string.read())
        with open(path_j + "/rider.jpg", "rb") as image2string:
                r = base64.b64encode(image2string.read())
        with open(path_j + "/rider_head.jpg", "rb") as image2string:
                rh = base64.b64encode(image2string.read())
        data = {
             "accusation number": j,
             "location": i,
             "date" : date,
             "time" : time,
             "bike" : bike,
             "number plate" : np,
             "rider" : r,
             "rider_head" : rh,
             "fine" : "Not Paid"
             }
        result = surv_data.insert_one(data)
        print("|",end="")
        c = c+1
        os.remove(path_j + "/bike.jpg")
        os.remove(path_j + "/numberplate.jpg")
        os.remove(path_j + "/rider.jpg")
        os.remove(path_j + "/rider_head.jpg")
        os.rmdir(path_j)
    os.rmdir(path_i)    
    print(" 100%")
    print(i,"-",c,"cases stored in the database\n")
print("Cases stored in the database successfully\n")
print('DATA FEEDING ENDED AT',(datetime.now()).strftime("%H:%M:%S"),"\n\n")
client.close()

