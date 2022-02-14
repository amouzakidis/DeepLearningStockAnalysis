import constants
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from pymongo import MongoClient

# Making a Connection with MongoClient
try:

    conn = MongoClient()
    print("Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")

# database
db = conn["stocks_database"]
# collection
avgSamplescollection = db["stock_samples_avg"]

avgSamples = avgSamplescollection.find()
avcSamplesCount = avgSamplescollection.count_documents({})

print(avcSamplesCount)

model = Sequential()  
model.add( Dense( constants.EVALUATION_DAYS, activation = 'relu', input_shape = ( constants.EVALUATION_DAYS, ) ) )
model.add( Dropout( 0.2 ) ) 
model.add( Dense( constants.EVALUATION_DAYS / 2, activation = 'relu' ) )
model.add( Dropout( 0.2 ) ) 
model.add( Dense( 2, activation = 'softmax'))

#model.save("./avg_keras_model.krs")



