import constants
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.client import device_lib 
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from pymongo import MongoClient
import numpy as np
import time
import sys
import precisionArgmax as parg
from numpy import save, load

#np.set_printoptions(threshold = sys.maxsize)

start_time = time.time()

loadFile = 1

if loadFile == 1:
    npAvgSamples = load('data.npy')
    totalPositiveSamples = 107742 
    totalNegativeSamples = 492258
    avgSamplesCount = 6000000
else :
    # Making a Connection with MongoClient
    try:
        conn = MongoClient()
        print("Connected successfully!!!")
    except:  
        print("Could not connect to MongoDB")

    # database
    db = conn["stocks_database"]
    # collection
    #avgSamplescollection = db["stock_samples_gai"]
    avgSamplescollection = db[ constants.TARGET_COLLECTION ]

    query = {}
    avgSamplesCount = avgSamplescollection.count_documents( query )
    limit = 600000
    avgSamplesCount = min( limit, avgSamplesCount )

    npAvgSamples = np.zeros( shape = ( constants.TRAINING_DAYS + 1, avgSamplesCount ) )
    idx = 0
    totalPositiveSamples = 0
    for avgSample in avgSamplescollection.find( query ).batch_size( 500000 ).limit(limit):
        for j in range( constants.TRAINING_DAYS ):
            val = avgSample[ 'data' ][ j ][ 'Close' ]
            npAvgSamples[ j ][ idx ] = val
        npAvgSamples[ constants.TRAINING_DAYS ][ idx ] = avgSample[ 'tag']
        totalPositiveSamples += avgSample[ 'tag' ]
        idx += 1
        print( "loaded:" + str(idx) + " samples out of:" + str( avgSamplesCount ) + " percentage:" + str( idx /avgSamplesCount * 100 ) + "%" )
    save('data.npy', npAvgSamples)

scaler = MinMaxScaler()
npAvgSamples = scaler.fit_transform(npAvgSamples)
npAvgSamples = npAvgSamples.transpose()

totalNegativeSamples = avgSamplesCount - totalPositiveSamples
print("Total positive samples:" + str( totalPositiveSamples ) + " Total negative samples:" + str( totalNegativeSamples ) + " Total samples" +  str( avgSamplesCount ) )

inputX = npAvgSamples[ :, 0 : constants.TRAINING_DAYS ]
outputY = npAvgSamples[ :, constants.TRAINING_DAYS ]

X_train, X_test, y_train, y_test = train_test_split( inputX, outputY, test_size = 0.3, random_state = 30 )

class_weight = { 0: totalNegativeSamples/avgSamplesCount, 1:totalPositiveSamples/avgSamplesCount }

model = Sequential()
model.add( Dense( units = constants.TRAINING_DAYS, 
                input_shape=(constants.TRAINING_DAYS,), 
                kernel_initializer='uniform', 
                activation ='relu') )
model.add( Dropout(0.5) )
model.add( BatchNormalization() )
model.add( Dense( units = constants.TRAINING_DAYS / 2,  
                kernel_initializer='uniform', 
                activation ='relu') )
model.add( Dropout( 0.5 ))
model.add( BatchNormalization() )
model.add( Dense( units = constants.TRAINING_DAYS / 4,  
                kernel_initializer='uniform', 
                activation ='relu') )
model.add( Dropout( 0.5 ))
model.add( BatchNormalization() )
model.add( Dense( units = 1,
                kernel_initializer='uniform',
                activation ='sigmoid') )

METRICS = [
      keras.metrics.TruePositives( name='TruePositive' ),
      keras.metrics.FalsePositives( name='FalsePositive' ),
      keras.metrics.TrueNegatives( name='TrueNegative' ),
      keras.metrics.FalseNegatives( name='FalseNegative' ), 
      keras.metrics.BinaryAccuracy( name='Accuracy' ),
      keras.metrics.Precision( name='Precision' ),
      keras.metrics.Recall( name='Recall' ),
      keras.metrics.AUC( name='auc' ),
      keras.metrics.AUC( name='prc', curve='PR' ),
]

# Compile the model
model.compile( optimizer=keras.optimizers.Adam( learning_rate = 5e-03 ), loss = keras.losses.BinaryCrossentropy(), metrics=METRICS )

train_data = tf.data.Dataset.from_tensor_slices((X_train, y_train))
valid_data = tf.data.Dataset.from_tensor_slices((X_test, y_test))

epochs_no = 100
batch_size = avgSamplesCount
model.fit( X_train, y_train, epochs = epochs_no, batch_size = batch_size, class_weight = class_weight )
#model.fit( train_data, validation_data=valid_data, epochs = epochs_no, batch_size = batch_size, class_weight = class_weight )

print("Now Evaluate")
results = model.evaluate( X_test, y_test, batch_size = batch_size, )
print("Loss: {:0.4f}".format(results[0]))
print("Results")
print( results )

model.save( "./avg_keras_model" )

print( "Total execution time:%s seconds:" % ( time.time() - start_time ) )

