import yfinance as yf
import pandas as pd
import datetime as dt
import csv
import sys
from dateutil.relativedelta import relativedelta
import pymongo
from pymongo import MongoClient

print( sys.argv )

if( len(sys.argv) > 1 ):
    start_date = sys.argv[1]
else:
    start_date = three_yrs_ago = dt.datetime.now() - relativedelta(years=5)

if( len(sys.argv) > 2 ):
    end_date = sys.argv[2]
else:
    end_date = dt.datetime.now()

tickers = []
with open('./data/nasdaq_screener_1644443600221.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tickers.append( row['Symbol'] )
        
# Making a Connection with MongoClient
try:
    conn = MongoClient()
    print("Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")

# database
db = conn["stocks_database"]
# collection
collection = db["stock_history"]

idx = 0
total = len(tickers);
for ticker in tickers:
    idx += 1
    print( "idx: " + str( idx ) + " of total:" + str( total ) + " ticker:" + str(ticker) )
    df = yf.download( ticker, start_date, end_date )
    for index, row in df.iterrows():
        row_dict = row.to_dict() 
        row_dict['ticker'] = ticker
        row_dict['timestamp'] = index
        collection.insert_one( row_dict )

    


