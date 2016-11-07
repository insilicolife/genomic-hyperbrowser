# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
'''
Created on Jan 21, 2016

@author: boris
'''

from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.SingleValExtractorStat import SingleValExtractorStat


class SingleValueOverlapStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class SingleValueOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class SingleValueOverlapStatUnsplittable(Statistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild(SingleValExtractorStat(self._region, self._track, self._track2, childClass=RawOverlapStat, resultKey='Both', **self._kwArgs))