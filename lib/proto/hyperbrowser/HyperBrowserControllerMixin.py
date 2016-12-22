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
#

from gold.application.GalaxyInterface import GalaxyInterface
from proto.hyperbrowser.hyper_gui import TrackWrapper


class HyperBrowserControllerMixin(object):
    def _init(self):
        super(HyperBrowserControllerMixin, self)._init()

        self.trackElements = {}
        self.batchline = ''

    def getInputValueForTrack(self, id, name):
        try:
            # assert False
            cachedTracks = self.getCacheData(id)
            track = self.getTrackElement(id, name, tracks=cachedTracks)
        except:
            print 'track cache is empty'
            track = self.getTrackElement(id, name)
            self.putCacheData(id, track.tracks)

        self.trackElements[id] = track
        tn = track.definition(False)
        GalaxyInterface.cleanUpTrackName(tn)
        val = ':'.join(tn)
        # val = track.asString()
        return val

    def decodeChoice(self, opts, id, choice):
        if opts == '__track__':
            tn = str(choice).split(':')
            GalaxyInterface.cleanUpTrackName(tn)
            choice = ':'.join(tn)
        else:
            choice = super(HyperBrowserControllerMixin, self).decodeChoice(opts, id, choice)
        return choice

    def getBatchLine(self):
        if len(self.subClasses) == 0 and self.prototype.isBatchTool():
            self.batchline = '$Tool[%s](%s)' % (self.toolId, '|'.join([repr(c) for c in self.choices]))
            return self.batchline
        return None

    def _getAllGenomes(self):
        return [('----- Select -----', '', False)] + GalaxyInterface.getAllGenomes(self.galaxy.getUserName())
        
    def getTrackElement(self, id, label, history=False, ucsc=False, tracks=None):
        datasets = []
        if history:
            try:
                datasets = self.galaxy.getHistory(GalaxyInterface.getSupportedGalaxyFileFormats())
            except Exception, e:
                print e
        element = TrackWrapper(id, GalaxyInterface, [], self.galaxy, datasets, self.getGenome(), ucscTracks=ucsc)
        if tracks is not None:
            element.tracks = tracks
        else:
            element.fetchTracks()
        element.legend = label
        return element

    @staticmethod
    def _getStdOutToHistoryDatatypes():
        return ['html', 'customhtml', 'hbfunction']
