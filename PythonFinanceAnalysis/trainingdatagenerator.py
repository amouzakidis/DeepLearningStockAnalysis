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
collectionMax = db["stock_samples_max"]
collectionAvg = db["stock_samples_avg"]
collectionGAI = db["stock_samples_gai"]

tickers = []
with open('./data/nasdaq_screener_1644443600221.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tickers.append( row['Symbol'] )

totalMax = 0
totalAvg = 0
totalGAI = 0
idx = 0
jdx = 0
totalSamples = 0
for ticker in tickers:
    jdx += 1
    print( ticker +" stock number " + str( jdx ) + " of " + str( len(tickers) ) )
    queue = []
    for doc in collection.find( {"ticker":ticker}, {"ticker":1, "Close": 1, "timestamp" : 1} ).sort( "timestamp", pymongo.ASCENDING ):        
        idx += 1
        queue.append(doc)
        if len(queue) > constants.DAYS_OF_INTEREST:
            queue.pop(0)
            totalSamples += 1
            sample = trainingutils.TrainingSample(queue)
            maxTag = sample.tagBasedOnMax()
            avgTag = sample.tagBasedOnAverage()
            generalIncreaseTag = sample.tagBasedOnGeneralIncrease()
            totalMax += maxTag
            totalAvg += avgTag            
            totalGAI += generalIncreaseTag
            #collectionMax.insert_one( { "ticker": ticker, "data": sample.data, "tag": maxTag })
            #collectionAvg.insert_one( { "ticker": ticker, "data": sample.data, "tag": avgTag })
            collectionGAI.insert_one( { "ticker": ticker, "data": sample.data, "tag": generalIncreaseTag })

print( "Total Max:" + str( totalMax ) + "(" + str( totalMax/totalSamples ) + ")" )
print( "Total Average:" + str( totalAvg )  + "(" + str( totalAvg/totalSamples ) + ")")
print( "Total Overall Average:" + str( totalGAI )  + "(" + str( totalGAI/totalSamples ) + ")")
print( "Total Samples:" + str( totalSamples ) )