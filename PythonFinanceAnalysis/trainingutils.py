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
        return self.tag

    def tagBasedOnAverage( self ):
        avgValue =sum( [ item['Close'] for item in self.evaluationData ] ) / len( self.evaluationData )
        if avgValue > self.data[ len( self.data ) -1 ][ "Close" ]  * constants.WANTED_AVERAGE_INCREASED_FACTOR:
            self.tag = constants.DATASET_INTERESTING
        else:
            self.tag = constants.DATASET_NOT_INTERESTING
        return self.tag

    def tagBasedOnGeneralIncrease( self ):
        avgValue = sum( [ item['Close'] for item in self.evaluationData ] ) / len( self.evaluationData )
        avgPrevValue = sum( [ item['Close'] for item in self.data ] ) / len( self.data )
        if avgValue > self.data[ len( self.data ) -1 ][ "Close" ] and avgValue > avgPrevValue:
            self.tag = constants.DATASET_INTERESTING
        else:
            self.tag = constants.DATASET_NOT_INTERESTING
        return self.tag