import constants
from tensorflow.python.client import device_lib 
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pymongo import MongoClient
import numpy as np
import time

print(device_lib.list_local_devices()) 

start_time = time.time()

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

avgSamplesCount = avgSamplescollection.count_documents({})
#limit = 200000
#avgSamplesCount = limit

npAvgSamples = np.zeros( shape = ( constants.TRAINING_DAYS + 1, avgSamplesCount ) )
idx = 0
totalPositiveSamples = 0
for avgSample in avgSamplescollection.find().batch_size( 500000 ):
    for j in range( constants.TRAINING_DAYS ):
        val = avgSample[ 'data' ][ j ][ 'Close' ]
        npAvgSamples[ j ][ idx ] = val
    npAvgSamples[ constants.TRAINING_DAYS ][ idx ] = avgSample[ 'tag']
    totalPositiveSamples += avgSample[ 'tag' ]
    idx += 1
    print( "loaded:" + str(idx) + " samples out of:" + str( avgSamplesCount ) + " percentage:" + str( idx /avgSamplesCount * 100 ) + "%" )

npAvgSamples = npAvgSamples.transpose()

totalNegativeSamples = avgSamplesCount - totalPositiveSamples
print("Total positive samples:" + str( totalPositiveSamples ) + " Total negative samples:" + str( totalNegativeSamples ) + " Total samples" +  str( avgSamplesCount ) )

inputX = npAvgSamples[ :, 0 : constants.TRAINING_DAYS ]
outputY = npAvgSamples[ :, constants.TRAINING_DAYS ]

scaler = StandardScaler()
scaler.fit_transform(inputX)

X_train, X_test, y_train, y_test = train_test_split( inputX, outputY, test_size = 0.25, random_state = 40 )

class_weight = { 0: totalNegativeSamples/avgSamplesCount, 1:totalPositiveSamples/avgSamplesCount }

model = Sequential()
model.add( Dense( constants.TRAINING_DAYS + constants.TRAINING_DAYS / 2, input_dim=constants.TRAINING_DAYS, activation='relu' ) )
model.add( Dense( constants.TRAINING_DAYS / 2, activation='relu' ) )
model.add( Dense( 1, activation = 'sigmoid' ) )

# Compile the model
model.compile( optimizer='adam', loss='categorical_crossentropy', metrics=[ 'accuracy' ] )

epochs_no = 100
batch_size = 2048
model.compile( loss='binary_crossentropy', optimizer = 'adam', metrics = [ 'accuracy' ])
model.fit( X_train, y_train, epochs = epochs_no, batch_size = batch_size, class_weight = class_weight )

# evaluate the keras model
_, accuracy = model.evaluate( X_test, y_test )
print( 'Accuracy: %.2f' % ( accuracy * 100 ) )

model.save( "./avg_keras_model" )

print( "Total execution time:%s seconds:" % ( time.time() - start_time ) )

