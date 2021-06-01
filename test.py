from misc import database

db, client = database.init("SUMOSpeedTransitionDB")

data = db["SUMORoutes"].find().limit(1)

print(list(data))
