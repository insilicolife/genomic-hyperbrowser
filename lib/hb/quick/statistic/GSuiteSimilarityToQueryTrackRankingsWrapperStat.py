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
from gold.track.TrackStructure import TrackStructure
from quick.statistic.GSuiteSimilarityToQueryTrackRankingsV2Stat import GSuiteSimilarityToQueryTrackRankingsV2Stat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class GSuiteSimilarityToQueryTrackRankingsWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass


#class GSuiteSimilarityToQueryTrackRankingsWrapperStatSplittable(StatisticSumResSplittable):
#    pass


class GSuiteSimilarityToQueryTrackRankingsWrapperStatUnsplittable(MultipleTrackStatistic):
        
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
    
        ts = TrackStructure()
        ts[TrackStructure.QUERY_KEY] = [self._tracks[0]]
        ts[TrackStructure.REF_KEY] = self._tracks[1:]
        self._addChild(GSuiteSimilarityToQueryTrackRankingsV2Stat(self._region, ts, **self._kwArgs))