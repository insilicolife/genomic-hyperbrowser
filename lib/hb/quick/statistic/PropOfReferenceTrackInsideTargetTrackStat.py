from gold.statistic.RawOverlapStat import RawOverlapStat
'''
Created on Apr 27, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class PropOfReferenceTrackInsideTargetTrackStat(MagicStatFactory):
    '''
    STAT T1
    
    For tracks t1 (target track) and t2 (reference track) calculate
    bp(t1 intersection t2)/bp(t1) where bp is the number of basepairs covered. 
    '''
    pass

#class PropOfReferenceTrackInsideTargetTrackStatSplittable(StatisticSumResSplittable):
#    pass
            
class PropOfReferenceTrackInsideTargetTrackStatUnsplittable(Statistic):    
    def _compute(self):
        only1,both = [ self._children[0].getResult()[key] for key in ['Only1','Both'] ]
        if only1 + both == 0:
            return 0.0
        return float(both)/(only1 + both)
    
    def _createChildren(self):
        self._addChild(RawOverlapStat(self._region, self._track, self._track2))
