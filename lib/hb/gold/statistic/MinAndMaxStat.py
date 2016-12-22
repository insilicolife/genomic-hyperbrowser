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
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from collections import OrderedDict

class MinAndMaxStat(MagicStatFactory):
    pass

class MinAndMaxStatSplittable(StatisticSplittable):    
    def _combineResults(self):
        #childResMin = [childResult['min'] for childResult in self._childResults if childResult['min']!=None]
        #childResMax = [childResult['max'] for childResult in self._childResults if childResult['max']!=None]
        childResMin = [childResult['min'] for childResult in self._childResults if childResult is not None]
        childResMax = [childResult['max'] for childResult in self._childResults if childResult is not None]
        self._result = OrderedDict([('min', min(childResMin)), ('max', max(childResMax))])

class MinAndMaxStatUnsplittable(Statistic):    
    def _compute(self):
        vec = self._children[0].getResult().valsAsNumpyArray()
        #if len(vec)>0:
        return OrderedDict([('min', vec.min()), ('max', vec.max())])
        #else:
        #    return OrderedDict([('min', None), ('max', None)])
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=True, interval=False)) )