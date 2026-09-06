from pymongo import MongoClient
import base64
import pprint
import os

client = MongoClient()
db = client["helmet_surv"]
surv_data = db.surv_data

print("\t\tCASE FINDER\n\n")

accn_number = input("Enter Accusation Number : ") #ACN15012322413578

print("\nCase folder {} created\n\nDetails :-\n-------------\n".format(accn_number))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.environ.get("HELMET_CASES_DIR", os.path.join(BASE_DIR, "Cases"))
new_dir = accn_number

data_r = surv_data.find_one({"accusation number": accn_number})

print("ACCUSATION NUMBER :", accn_number)
print("LOCATION          :", data_r["location"])
print("DATE              :", data_r["date"])
print("TIME              :", data_r["time"])
print("BIKE              : Refer in Case folder - 'Bike.jpg'")
print("NUMBER PLATE      : Refer in Case folder - 'Number_Plate.jpg'")
print("RIDER             : Refer in Case folder - 'Rider.jpg'")
print("RIDER_HEAD        : Refer in Case folder - 'Rider_Head.jpg'")
print("FINE STATUS       :", data_r["fine"])

path = os.path.join(parent_dir, new_dir)
try:
    os.mkdir(path)
except:
    pass

decodeit = open(path+'/Bike.jpg', 'wb')
decodeit.write(base64.b64decode((data_r["bike"])))
decodeit.close()
decodeit = open(path+'/Number_Plate.jpg', 'wb')
decodeit.write(base64.b64decode((data_r["number plate"])))
decodeit.close()
decodeit = open(path+'/Rider.jpg', 'wb')
decodeit.write(base64.b64decode((data_r["rider"])))
decodeit.close()
decodeit = open(path+'/Rider_Head.jpg', 'wb')
decodeit.write(base64.b64decode((data_r["rider_head"])))
decodeit.close()

print("\nAll relevant details displayed successfully\n")

client.close()

