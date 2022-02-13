import constants

class TrainingSample:
    def __init__( self, data ):
        self.tag = constants.DATASET_UNTESTED
        self.data = []   
        self.evaluationData = []
        for idx in range(constants.TRAINING_DAYS):
            self.data.append( data[ idx ] )
        
        for idx in range(constants.EVALUATION_DAYS):
            self.evaluationData.append( data[ idx + constants.TRAINING_DAYS ] )
           
    def tagBasedOnMax( self ):
        maxValue = max( self.evaluationData, key = lambda x:x[ 'Close' ] )[ 'Close' ]        
        if maxValue > self.data[len( self.data) -1][ "Close" ] * constants.WANTED_INCREASED_FACTOR:
            self.tag = constants.DATASET_INTERESTING
        else:
            self.tag = constants.DATASET_NOT_INTERESTING

    def tagBasedOnAverage( self ):
        avgValue =sum( self.evaluationData, key=lambda x:x[ 'Close' ]) / len( self.evaluationData )
        if avgValue > self.data[ len( self.data ) -1 ][ "Close" ]  * constants.WANTED_INCREASED_FACTOR:
            self.tag = constants.DATASET_INTERESTING
        else:
            self.tag = constants.DATASET_NOT_INTERESTING