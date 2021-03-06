from collections import OrderedDict

from gold.gsuite import GSuiteConstants
from quick.extra.clustering.ClusteringExecution import ClusteringExecution
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.
class ClusTrackTool(GeneralGuiTool, GenomeMixin, UserBinMixin, DebugMixin):
    #CONSTANTS
    ##GenomeMixin
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuite', 'gSuiteRef']
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    ALLOW_MULTIPLE_GENOMES = False
    WHAT_GENOME_IS_USED_FOR = 'the analysis'  # Other common possibility: 'the analysis'

    ##GSuite validation

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]


    ##Similarity techniques
    SIMILARITY_POSITIONAL = 'Use similarity of positional distribution along the genome'
    SIMILARITY_RELATIONS_TO_OTHER = 'Use similarity of relations to other sets of genomic features'
    SIMILARITY_DIRECT_SEQ_LVL = 'Use direct sequence-level similarity'
    REGIONS_CLUSTERING = 'Regions clustering'
    
    ##Options for pair distance
    PAIR_DIST_RATIO_INTERSECT_UNION_MINUS = 'Ratio of intersection vs union of segments (1 minus the ratio)'
    PAIR_DIST_RATIO_INTERSECT_UNION_OVER = 'Ratio of intersection vs union of segments (1 over the ratio)'
    PAIR_DIST_PAIRWISE_OVERLAP = 'Pairwise overlap enrichment between tracks (v2)'
    PAIR_DIST_RATIO_INTERSECT_UNION = 'Ratio of intersection vs union of segments'
    ONE_MINUS_RATIO = '1 minus the ratio'
    ONE_OVER_RATIO = '1 over the ratio'
    
    ##Clustering method
    CLUS_METHOD_HIERARCHICAL = 'Hierarchical clustering'
    CLUS_METHOD_K_MEANS = 'K-means clustering'
    
    ##Clustering algorithm
    CLUS_ALG_HIERAR_SINGLE = 'single'
    CLUS_ALG_HIERAR_AVG = 'average'
    CLUS_ALG_HIERAR_COMPLETE = 'complete'
    CLUS_ALG_HIERAR_WARD = 'ward'
    CLUS_ALG_HIERAR_MEDIAN = 'median'
    CLUS_ALG_HIERAR_CENTROID = 'centroid'
    
    CLUS_ALG_K_MEANS_HARTIGAN = 'Hartigan'
    CLUS_ALG_K_MEANS_LLOYD = 'Lloyd'
    CLUS_ALG_K_MEANS_MACQUEEN = 'MacQueen'
    CLUS_ALG_K_MEANS_FORGY = 'Forgy'
    
    ##Clustering option
    CLUS_OPT_DIST_EUCLIDEAN = 'euclidean'
    CLUS_OPT_DIST_MAX = 'maximum'
    CLUS_OPT_DIST_MANHATTAN = 'manhattan'
    CLUS_OPT_DIST_CANBERRA = 'canberra'
    CLUS_OPT_DIST_BINARY = 'binary'
    CLUS_OPT_DIST_MINKOWSKI = 'minkowski'
    

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "ClusTrack: Cluster tracks in GSuite based on genome level similarity"

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [
                ('Basic user mode', 'isBasic'),
                ('', 'basicQuestionId'),
                ('Select GSuite (tracks to cluster)','gSuite'),
                ('Select similarity technique', 'similarityTech'),
                ('Select GSuite (reference tracks)', 'gSuiteRef')
               ] + cls.getInputBoxNamesForGenomeSelection() + [
                ('Select feature for similarity calculation', 'featureSelection'),
                ('Select pair distance option', 'pairDistOption'),
                ('Select clustering method', 'clusteringMethod'),
                ('Select clustering algorithm', 'clusteringAlgorithm'),
                ('Select clustering option', 'clusteringOption')
               ] + cls.getInputBoxNamesForUserBinSelection() \
                 + cls.getInputBoxNamesForDebug()

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @staticmethod
    def getOptionsBoxBasicQuestionId(prevChoices):
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxGSuite(prevChoices): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxSimilarityTech(cls, prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        
        if prevChoices.isBasic:
            return ('__hidden__', cls.SIMILARITY_DIRECT_SEQ_LVL)
        
        return [cls.SIMILARITY_POSITIONAL, \
                cls.SIMILARITY_RELATIONS_TO_OTHER, \
                cls.SIMILARITY_DIRECT_SEQ_LVL
                ]

    @classmethod
    def getOptionsBoxFeatureSelection(cls, prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''

        if prevChoices.gSuite and prevChoices.genome:
            from quick.extra.clustering.FeatureCatalog import LocalResultsAsFeaturesCatalog, \
                ReferenceAnalsesAsFeaturesCatalog

            if prevChoices.similarityTech == cls.SIMILARITY_POSITIONAL:
                featureCatalog = LocalResultsAsFeaturesCatalog
            elif prevChoices.similarityTech == cls.SIMILARITY_RELATIONS_TO_OTHER:
                featureCatalog = ReferenceAnalsesAsFeaturesCatalog
            else:
                return None

            genome = prevChoices.genome
            for clustTrack in getGSuiteFromGalaxyTN(prevChoices.gSuite).allTracks():
                # Only first track in gSuite is currently used for generating feature list,
                # as in clusteringtool.make
                clustTN = clustTrack.trackName
                if prevChoices.gSuiteRef:
                    gSuiteRef = getGSuiteFromGalaxyTN(prevChoices.gSuiteRef)
                    refTrackNames = [track.trackName for track in gSuiteRef.allTracks()]
                else:
                    refTrackNames = [[]]
                featureSets = [set(featureCatalog.getValidAnalyses(genome, clustTN, refTN)) for
                               refTN in refTrackNames]
                return sorted(set.intersection(*featureSets))

    @classmethod
    def getOptionsBoxPairDistOption(cls, prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        
        if prevChoices.similarityTech == cls.SIMILARITY_DIRECT_SEQ_LVL:
            if prevChoices.isBasic:
                return ('__hidden__', cls.PAIR_DIST_RATIO_INTERSECT_UNION_MINUS)
            return [
                cls.PAIR_DIST_RATIO_INTERSECT_UNION_MINUS, \
                cls.PAIR_DIST_RATIO_INTERSECT_UNION_OVER, \
                cls.PAIR_DIST_PAIRWISE_OVERLAP]
        else:
            return None

    @classmethod
    def getOptionsBoxGSuiteRef(cls, prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        #TODO: boris 20141102, return reference track gsuite element if 
        #appropriate feature extraction strategy is selected
        if prevChoices.similarityTech == cls.SIMILARITY_RELATIONS_TO_OTHER \
        or prevChoices.similarityTech == cls.REGIONS_CLUSTERING:
            return GeneralGuiTool.getHistorySelectionElement('gsuite')
        else:
            return None

    @classmethod
    def getOptionsBoxClusteringMethod(cls, prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices.isBasic:
            return ('__hidden__', cls.CLUS_METHOD_HIERARCHICAL)

        return [cls.CLUS_METHOD_HIERARCHICAL
#                 ,\
#                 cls.CLUS_METHOD_K_MEANS
                ]
        
    @classmethod
    def getOptionsBoxClusteringAlgorithm(cls, prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        
        if prevChoices.clusteringMethod == cls.CLUS_METHOD_HIERARCHICAL:
            if prevChoices.isBasic:
                return ('__hidden__', cls.CLUS_ALG_HIERAR_SINGLE)
            
            return [
                cls.CLUS_ALG_HIERAR_SINGLE, \
                cls.CLUS_ALG_HIERAR_AVG, \
                cls.CLUS_ALG_HIERAR_COMPLETE, \
                cls.CLUS_ALG_HIERAR_WARD, \
                cls.CLUS_ALG_HIERAR_MEDIAN, \
                cls.CLUS_ALG_HIERAR_CENTROID]
        elif prevChoices.clusteringMethod == cls.CLUS_METHOD_K_MEANS:
            return [
                cls.CLUS_ALG_K_MEANS_HARTIGAN, \
                cls.CLUS_ALG_K_MEANS_LLOYD, \
                cls.CLUS_ALG_K_MEANS_MACQUEEN, \
                cls.CLUS_ALG_K_MEANS_FORGY]
        else:
            return None

    @classmethod
    def getOptionsBoxClusteringOption(cls, prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        
        if prevChoices.clusteringMethod == cls.CLUS_METHOD_HIERARCHICAL \
        and prevChoices.similarityTech != cls.SIMILARITY_DIRECT_SEQ_LVL:
            return [
                cls.CLUS_OPT_DIST_EUCLIDEAN, \
                cls.CLUS_OPT_DIST_MAX, \
                cls.CLUS_OPT_DIST_MANHATTAN, \
                cls.CLUS_OPT_DIST_CANBERRA, \
                cls.CLUS_OPT_DIST_BINARY, \
                cls.CLUS_OPT_DIST_MINKOWSKI]
        elif prevChoices.clusteringMethod == cls.CLUS_METHOD_K_MEANS:
            return ['2', '3', '4', '5']
        else:
            return None

    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        cls._setDebugModeIfSelected(choices)

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
          
        genome = gSuite.genome
        trackTitles = list(gSuite.allTrackTitles())
        tracks = [track.trackName for track in gSuite.allTracks()]
        
        refTracks = []
        if choices.gSuiteRef:
            gSuiteRef = getGSuiteFromGalaxyTN(choices.gSuiteRef)
            refTracks = [track.trackName for track in gSuiteRef.allTracks()]
            refTracksReady = [':'.join(refTrack) for refTrack in refTracks]

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        clusterMethod = choices.clusteringMethod
        extra_option = choices.clusteringAlgorithm
        distanceType = None
        if clusterMethod == cls.CLUS_METHOD_HIERARCHICAL:
            distanceType = choices.clusteringOption
        kmeans_alg = None
        if clusterMethod == cls.CLUS_METHOD_K_MEANS:
            kmeans_alg = choices.clusteringAlgorithm
            extra_option = choices.clusteringOption
        
        numreferencetracks = len(refTracks)
        
#         if self.params.get('clusterCase') == 'use pair distance':
        if choices.similarityTech == cls.SIMILARITY_DIRECT_SEQ_LVL:
            feature = None
            extra_feature = None
            if choices.pairDistOption == cls.PAIR_DIST_RATIO_INTERSECT_UNION_MINUS:
                feature = cls.PAIR_DIST_RATIO_INTERSECT_UNION
                extra_feature = cls.ONE_MINUS_RATIO
            elif choices.pairDistOption == cls.PAIR_DIST_RATIO_INTERSECT_UNION_OVER:
                feature = cls.PAIR_DIST_RATIO_INTERSECT_UNION
                extra_feature = cls.ONE_OVER_RATIO
            elif choices.pairDistOption == cls.PAIR_DIST_PAIRWISE_OVERLAP:
                feature = cls.PAIR_DIST_PAIRWISE_OVERLAP

            ClusteringExecution.executePairDistance(genome, tracks, trackTitles, clusterMethod, extra_option, feature, extra_feature, galaxyFn, regSpec, binSpec);
#         elif self.params.get('clusterCase') == 'use refTracks':
        elif choices.similarityTech == cls.SIMILARITY_RELATIONS_TO_OTHER:
            refTrackFeatures = [choices.featureSelection] * numreferencetracks
            ClusteringExecution.executeReferenceTrack(genome, tracks, trackTitles, clusterMethod, extra_option, 
                                                      distanceType, kmeans_alg, galaxyFn, regSpec, binSpec, 
                                                      numreferencetracks, refTracksReady, refTrackFeatures)
#         elif self.params.get('clusterCase') == 'self feature': #self feature case.
        elif choices.similarityTech == cls.SIMILARITY_POSITIONAL: #self feature case.
            feature = choices.featureSelection
            ClusteringExecution.executeSelfFeature(genome, tracks, trackTitles, clusterMethod, extra_option, feature, distanceType, kmeans_alg, galaxyFn, regSpec, binSpec);
        else : # regions clustering case
#             self.handleRegionClustering(genome, tracks, clusterMethod, extra_option)
            #TODO: handle region clustering
            pass

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if not choices.gSuite:
            from quick.toolguide.controller.ToolGuide import ToolGuideController
            from quick.toolguide import ToolGuideConfig
            return ToolGuideController.getHtml(cls.toolId,
                                               [ToolGuideConfig.GSUITE_INPUT],
                                               choices.isBasic)

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gSuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)
        if errorString:
            return errorString

        if choices.similarityTech == cls.SIMILARITY_RELATIONS_TO_OTHER \
                or choices.similarityTech == cls.REGIONS_CLUSTERING:
            if not choices.gSuiteRef:
                from quick.toolguide.controller.ToolGuide import ToolGuideController
                from quick.toolguide import ToolGuideConfig
                return ToolGuideController.getHtml(cls.toolId,
                                                   [ToolGuideConfig.GSUITE_INPUT],
                                                   choices.isBasic)

            errorString = GeneralGuiTool._checkGSuiteFile(choices.gSuiteRef)
            if errorString:
                return errorString

            gSuiteRef = getGSuiteFromGalaxyTN(choices.gSuiteRef)
            errorString = GeneralGuiTool._checkGSuiteRequirements \
                (gSuiteRef,
                 cls.GSUITE_ALLOWED_FILE_FORMATS,
                 cls.GSUITE_ALLOWED_LOCATIONS,
                 cls.GSUITE_ALLOWED_TRACK_TYPES,
                 cls.GSUITE_DISALLOWED_GENOMES)
            if errorString:
                return errorString

        if choices.similarityTech in [cls.SIMILARITY_POSITIONAL,
                                      cls.SIMILARITY_RELATIONS_TO_OTHER]:
            if not choices.featureSelection:
                return 'Feature for similarity calculation has not been selected. ' \
                       'If no features are available for selection, the track types ' \
                       'if the clustering and reference tracks are too inconsistent. ' \
                       'Please remove the inconsistent tracks from the GSuite.'

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString
        
        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether the debug mode is turned on.
        '''
        return False
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #
    #@staticmethod
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
