import sys
import os

from collections import OrderedDict, namedtuple
from conglomerate.methods.interface import ColocMeasureOverlap
from conglomerate.methods.method import ManyVsManyMethod
from conglomerate.tools.SingleResultValue import SingleResultValue
from conglomerate.tools.job import Job
from gold.application.HBAPI import doAnalysis
from gold.track.Track import Track
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import GlobalBinSource
from quick.statistic.StatFacades import TpRawOverlapStat


AnalysisObject = namedtuple('AnalysisObject', ['analysisSpec', 'binSource', 'tracks', 'genome'])

class HyperBrowser(ManyVsManyMethod):

    def __init__(self):
        self._parsedResults = None
        self._genome = None
        self._queryTracks = None
        self._refTracks = None
        self._allowOverlaps = False
        self._colocStatistic = "TpRawOverlapStat"
        # self._randomizationAssumption = 'PermutedSegsAndIntersegsTrack_'
        self.preserveClumping(True)
        self._analyses = OrderedDict()
        self._results = None
        self._params = "Conglo Params not supported in HyperBrowser"
        self._trackTitleMappings = {}


    def _getToolName(self):
        return 'hb_conglo'

    def _getTool(self):
        raise NotImplementedError('Not supported by HB')

    def checkForAbsentMandatoryParameters(self):
        pass

    def createJobs(self):
        for queryTrack in self._queryTracks:
            qTrack = self._processTrack(queryTrack)
            for refTrack in self._refTracks:
                rTrack = self._processTrack(refTrack)
                self._analyses[(queryTrack, refTrack)] = AnalysisObject(self._getAnalysisSpec(),
                                                                        self._binSource,
                                                                        [qTrack, rTrack],
                                                                        self._genome)
        return [HBJob(self._analyses)]


    def setResultFilesDict(self, resultFilesDict):
        self._results = resultFilesDict
        self._ranSuccessfully = True

    def getResultFilesDict(self):
        return self._results
	
    def _setDefaultParamValues(self):
        pass

    def setGenomeName(self, genomeName):
        self._genome = genomeName.split('(')[-1].split(')')[0]
        self._binSource = GlobalBinSource(self._genome)

    def setChromLenFileName(self, chromLenFileName):
        pass

    def _setQueryTrackFileNames(self, trackFileList):
        # self._queryTracks = [self._getTrackFromFilename(trackFn) for trackFn in trackFnList]
        # self._queryTracks = [ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome, ['galaxy', 'bed', trackFn, 'dummy']) for trackFn in trackFnList]
        trackFnList = []
        for trackFile in trackFileList:
            self._addTrackTitleMapping(trackFile.path, trackFile.title)
            trackFnList.append(trackFile.path)
        self._queryTracks = trackFnList

    def _setReferenceTrackFileNames(self, trackFileList):
        trackFnList = []
        for trackFile in trackFileList:
            self._addTrackTitleMapping(trackFile.path, trackFile.title)
            trackFnList.append(trackFile.path)

        self._refTracks = trackFnList
        # self._refTracks = [ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome, ['galaxy', 'bed', trackFn, 'dummy']) for trackFn in trackFnList]
        # self._refTracks = [self._getTrackFromFilename(trackFn) for trackFn in trackFnList]
        # self._refTracks = [Track(ExternalTrackManager.constructGalaxyTnFromSuitedFn(trackFn),
        #                          splitext(basename(trackFn))) for trackFn in trackFnList]

    def setAllowOverlaps(self, allowOverlaps):
        self._allowOverlaps = allowOverlaps

    def _parseResultFiles(self):
        pass

    def getPValue(self):
        pvals = OrderedDict()
        for trackTuple, result in self._results.iteritems():
            pval = result.getGlobalResult()['P-value']
            pvals[trackTuple] = SingleResultValue(self._getNumericFromStr(pval), '<%.4f' % pval)
        return self.getRemappedResultDict(pvals)


    def getTestStatistic(self):
        testStats = OrderedDict()
        for trackTuple, result in self._results.iteritems():
            testStat = float(result.getGlobalResult()['TSMC_' + self._colocStatistic]) / result.getGlobalResult()['MeanOfNullDistr']
            svr = SingleResultValue(testStat, '<span title="' + \
                                    self.getTestStatDescr() \
                                    + '">' + ('%.2f' % testStat) + '</span>')
            testStats[trackTuple] = svr
        return self.getRemappedResultDict(testStats)

    @classmethod
    def getTestStatDescr(cls):
        return 'ratio of observed/expected'

    def getFullResults(self, galaxyFn=None):
        from os import linesep
        fullResult = OrderedDict()

        if galaxyFn:
            resultPage = self._generateResultPage(galaxyFn)
            for trackTuple, result in self._results.iteritems():
                fullResult[trackTuple] = resultPage
        else:
            for trackTuple, result in self._results.iteritems():
                fullResult[trackTuple] = str(result.getGlobalResult()['TSMC_' + self._colocStatistic]) + \
                             "\t" + str(result.getGlobalResult()['P-value']) + " <br>" + linesep
        return self.getRemappedResultDict(fullResult)

    def _generateResultPage(self, galaxyFn):
        from gold.result.ResultsViewer import ResultsViewerCollection

        resColl = ResultsViewerCollection(self._results.values(), galaxyFn)
        resultPage = GalaxyInterface.getHtmlBeginForRuns(galaxyFn)
        resultPage += GalaxyInterface.getHtmlForToggles(withRunDescription=True)
        resultPage += str(resColl)
        resultPage += GalaxyInterface.getHtmlEndForRuns()

        return resultPage

    def preserveClumping(self, preserve):
        if preserve:
            self._randomizationAssumption = \
                'PermutedSegsAndIntersegsTrack_:' \
                'Preserve segments (T2), segment lengths and inter-segment gaps (T1); ' \
                'randomize positions (T1) (MC)'
        else:
            self._randomizationAssumption = \
                'PermutedSegsAndSampledIntersegsTrack_:' \
                'Preserve segments (T2) and segment lengths (T1); randomize positions (T1) (MC)'

    def setRestrictedAnalysisUniverse(self, restrictedAnalysisUniverse):
        assert restrictedAnalysisUniverse is None, restrictedAnalysisUniverse


    def setColocMeasure(self, colocMeasure):

        if isinstance(colocMeasure, ColocMeasureOverlap):
            self._colocStatistic = "TpRawOverlapStat"
        else:
            raise AssertionError('Overlap is the only supported measure')

    def setHeterogeneityPreservation(self, preservationScheme, fn=None):
        pass

    def setRuntimeMode(self, mode):
        if mode =='quick':
            self._runtimeMode = 'Quick and rough indication'
        elif mode == 'medium':
            self._runtimeMode = 'Moderate resolution of global p-value'
        elif mode == 'accurate':
            self._runtimeMode = 'Fixed 10 000 samples (slow)'
        else:
            raise Exception("Invalid mode")

    def _getAnalysisSpec(self):

        from gold.description.AnalysisList import REPLACE_TEMPLATES
        from gold.description.AnalysisDefHandler import AnalysisDefHandler

        analysisDefString = REPLACE_TEMPLATES[
                                '$MCFDR$'] + ' -> RandomizationManagerStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', self._runtimeMode)
        analysisSpec.addParameter('assumptions', self._randomizationAssumption)
        analysisSpec.addParameter('rawStatistic', self._colocStatistic)
        analysisSpec.addParameter('tail', 'more')
        analysisSpec.addParameter('H0:_', 'The segments of track 1 are located independently '
                                          'of the segments of track 2 with respect to overlap')
        analysisSpec.addParameter('H1_more:_', 'The segments of track 1 tend to overlap the '
                                               'segments of track 2')
        analysisSpec.addParameter('H1_less:_', 'The segments of track 1 tend to avoid overlapping '
                                               'the segments of track 2')
        analysisSpec.addParameter('H1_different:_', 'The locations of the segments of track 1 '
                                                    'are dependent on the locations of the '
                                                    'segments of track 2 with respect to overlap')
        return analysisSpec

    # def _getTrackFromFilename(self, filePath):
    #     import os
    #     import shutil
    #     from gold.util.CommonFunctions import convertTNstrToTNListFormat
    #     relFilePath = os.path.relpath(filePath)
    #     trackName = ':'.join(os.path.normpath(relFilePath).split(os.sep))
    #     # trackName = _convertTrackName(trackName)
    #     convertedTrackName = convertTNstrToTNListFormat(trackName, doUnquoting=True)
    #
    #     from gold.util.CommonFunctions import createOrigPath, ensurePathExists
    #     origFn = createOrigPath(self._genome, convertedTrackName, os.path.basename(filePath))
    #     if os.path.exists(origFn):
    #         shutil.rmtree(os.path.dirname(origFn))
    #     ensurePathExists(origFn)
    #     shutil.copy(filePath, origFn)
    #     os.chmod(origFn, 0664)
    #
    #     from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
    #     PreProcessAllTracksJob(self._genome, convertedTrackName).process()
    #     return Track(convertedTrackName, trackTitle=trackName.split(":")[-1])

    def _processTrack(self, trackFn):
        from os.path import splitext, basename
        storedStdOut = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        track = Track(ExternalTrackManager.getPreProcessedTrackFromGalaxyTN
                      (self._genome, ['galaxy', 'bed', trackFn, basename(trackFn)],
                       printErrors=False, printProgress=False),
                      splitext(basename(trackFn)))
        sys.stdout = storedStdOut
        return track

    @staticmethod
    def addRunDescriptionToResult(analysisObj, result):
        runDescription = GalaxyInterface.getRunDescription(
            analysisObj.tracks[0].trackName, analysisObj.tracks[1].trackName,
            analysisObj.analysisSpec.getDef(),
            analysisObj.genome + ':*', '*', analysisObj.genome,
            showBatchLine=False)
        runDescBox = GalaxyInterface.getRunDescriptionBox(runDescription)
        result.setRunDescription(runDescBox)


class HBJob(Job):
    def __init__(self, analyses):
        self._analyses = analyses

    def run(self):
        results = OrderedDict()
        for key, analysisObj in self._analyses.iteritems():
            result = doAnalysis(analysisObj.analysisSpec, analysisObj.binSource, analysisObj.tracks)
            HyperBrowser.addRunDescriptionToResult(analysisObj, result)
            results[key] = result
        return results
