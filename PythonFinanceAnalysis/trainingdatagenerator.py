import pymongo
from pymongo import MongoClient
import csv
import constants
import trainingutils

#Making a Connection with MongoClient
try:
    conn = MongoClient()
    print("Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")

# database
db = conn["stocks_database"]
# collection
collection = db["stock_history"]

tickers = []
with open('./data/nasdaq_screener_1644443600221.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tickers.append( row['Symbol'] )

for ticker in tickers:    
    queue = []
    for doc in collection.find( {"ticker":ticker}, {"ticker":1, "Close": 1, "timestamp" : 1} ).sort( "timestamp", pymongo.ASCENDING ):        
        queue.append(doc)
        if len(queue) > constants.DAYS_OF_INTEREST:
            queue.pop(0)
            sample = trainingutils.TrainingSample(queue)
            maxTag = sample.tagBasedOnMax()
            avgTag = sample.tagBasedOnAverage()
            print( maxTag + " " + avgTag )
    break

