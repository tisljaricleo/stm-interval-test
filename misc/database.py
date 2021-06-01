from pymongo import MongoClient


def init(db_name):
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    return db, client


def closeConnection(client):
    client.close()


def insertMany(db, collection, data):
    db[collection].insert_many(data)


def insertOne(db, collection, data):
    db[collection].insert_one(data)


def selectAll(db, collection, ret="list"):
    if ret == "list":
        return list(db[collection].find())
    else:
        return db[collection].find()


def selectSome(db, collection, query, ret="list"):
    if ret == "list":
        return list(db[collection].find(query))
    else:
        return db[collection].find(query)


def selectDistinct(db, collection, attribute, ret="list"):
    if ret == "list":
        return list(db[collection].find().distinct(attribute))
    else:
        return db[collection].find().distinct(attribute)


def selectSkipLimit(db, collection, skip, limit):
    return list(db[collection].find().skip(skip).limit(limit))


def count(db, collection):
    return int(db[collection].find().count())


def groupBy(db, collection, query):
    return db[collection].aggregate([{'$group': query}])
