import requests
from pymongo import MongoClient
from config import mongo

# Setup connection to mongodb collection
server = MongoClient(mongo)
db = server.tidewater_db


products = [
    "water_level",
    "water_temperature",
    "wind",
    # 'visibility',
    # 'humidity',
    # 'currents'
]

label = [
    "height",
    "temp",
]


def req(i):
    # list of items we want to request from NOAA CO-OP api
    payload = {
        # 'begin_date': f'{begin_date}',
        # 'end_date': f'{end_date}',
        "date": "recent",
        "station": "8570283",
        "product": products[i],
        "time_zone": "lst",
        "application": "kgl",
        "format": "json",
        "units": "english",
        "datum": "STND",
    }
    r = requests.get(
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter", params=payload
    ).json()
    mongoIns(r, i)


def mongoIns(r, i):
    if i < 2:
        for time in range(len(r["data"])):
            if db[products[i]].find_one({"time": r["data"][time]["t"]}):
                db[products[i]].update_one(
                    {"time": r["data"][time]["t"]},
                    {"$set": {f"{label[i]}": r["data"][time]["v"]}},
                )
            else:
                lst = {}
                lst["info"] = r["metadata"]
                lst["time"] = r["data"][time]["t"]
                lst[f"{label[i]}"] = r["data"][time]["v"]
                db[products[i]].insert_one(lst).inserted_id

    else:
        for time in range(len(r["data"])):
            if db[products[i]].find_one({"time": r["data"][time]["t"]}):
                db[products[i]].update_one(
                    {"time": r["data"][time]["t"]},
                    {
                        "$set": {
                            "Speed": r["data"][time]["s"],
                            "Direction": r["data"][time]["dr"],
                            "Gust": r["data"][time]["g"],
                        }
                    },
                )
            else:
                lst = {}
                lst["info"] = r["metadata"]
                lst["time"] = r["data"][time]["t"]
                lst["Speed"] = r["data"][time]["s"]
                lst["Direction"] = r["data"][time]["dr"]
                lst["Gust"] = r["data"][time]["g"]
                db[products[i]].insert_one(lst).inserted_id


if __name__ == "__main__":

    for i in range(3):
        req(i)

