
import datetime
import pymongo
import numpy as np
import misc.config as config

config.initialize_stm_setup()
client = pymongo.MongoClient()
db = client["SUMOSpeedTransitionDB"]
SumoRoutesCol = db["SUMORoutes"]
SumoRoutesSortedCol = db["SUMORoutesSorted"]

intervali= list([])
for br in range(1, 25):
    intervali.append(dict({"data": [], "interval": br}))

innerdata= list([])
for br in range(1, 25):
    innerdata.append(dict({"data": [], "interval": br}))


sat = 3600
x = 1
vrijeme = list([])
for i in range(1, 24, x):
    vr = sat * i
    vrijeme.append(dict({"data": [vr], "vremena":i}))

data = list(SumoRoutesCol.find({}, {"_id": 0}))
DoljnjeVrijeme= 0
brojac = 0

for a in vrijeme:
    for b in a["data"]:
        GornjeVrijeme = b

        for x in data:

            VrijemeZaUsporediti = x["points"][0]["timestep"]

            if DoljnjeVrijeme < VrijemeZaUsporediti <= GornjeVrijeme:
                innerdata[brojac]["data"].append(x["route_id"])

        DoljnjeVrijeme = GornjeVrijeme
        brojac = brojac + 1

try:
    SumoRoutesSortedCol.insert_many(innerdata)
except:
    print("GRESKA!")
