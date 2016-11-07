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

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.Statistic import StatisticSumResSplittable

#Similar to CountPointStat, except it doesn't require interval=False
class OverlapAgnosticCountElementStat(MagicStatFactory):
    pass

class OverlapAgnosticCountElementStatSplittable(StatisticSumResSplittable):
    pass
            
class OverlapAgnosticCountElementStatUnsplittable(Statistic):
    ALLOW_OVERLAPS = None
    
    def _compute(self):
        rawData = self._children[0].getResult()
        if rawData.trackFormat.reprIsDense():
            return len(rawData.valsAsNumpyArray())
        else:
            return len( rawData.startsAsNumpyArray() )
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=self.ALLOW_OVERLAPS) ) )