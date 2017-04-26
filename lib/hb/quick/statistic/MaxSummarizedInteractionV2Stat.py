'''
Created on Nov 10, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.MultitrackSummarizedInteractionV2Stat import MultitrackSummarizedInteractionV2Stat
from quick.statistic.StatisticV2 import StatisticV2


class MaxSummarizedInteractionV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class MaxSummarizedInteractionV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class MaxSummarizedInteractionV2StatUnsplittable(StatisticV2):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild(
            MultitrackSummarizedInteractionV2Stat(self._region, 
                                                 self._trackStructure,
                                                 multitrackSummaryFunc = 'max',
                                                 **self._kwArgs))
