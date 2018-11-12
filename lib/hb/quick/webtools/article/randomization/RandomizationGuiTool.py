import os

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.track.trackstructure import TsRandAlgorithmRegistry
from gold.track.trackstructure.TsRandAlgorithmRegistry import getRequiredArgsForAlgorithm, getKwArgsForAlgorithm, \
    BIN_SOURCE_ARG, EXCLUDED_TS_ARG
from gold.track.trackstructure.TsUtils import getRandomizedVersionOfTs
from quick.gsuite.GuiBasedTsFactory import getFlatTracksTS, getSingleTrackTS
from quick.statistic.TsWriterStat import TsWriterStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from proto.HtmlCore import HtmlCore
from quick.webtools.mixin.RandAlgorithmMixin import RandAlgorithmMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class RandomizationGuiTool(GeneralGuiTool, RandAlgorithmMixin, UserBinMixin):
    @classmethod
    def getToolName(cls):
        return "Randomization GUI"

    #
    @classmethod
    def getInputBoxNames(cls):
        return [('Basic user mode', 'isBasic'),
                ("", 'toolDescTop'),
                ('Reference genome: ', 'genome'),
                ('Choose a file with chromosome lengths of a custom genome build : ', 'chooseChrnLenFile'),
                ('Number of tracks to shuffle: ', 'numberOfTracks'),
                ('Select the BED or Gsuite file to shuffle: ', 'chooseTrackFiles'),
                ('Restrict the shuffling to certain regions?', 'universeRegions'),
                ('Select the BED file containing universe of regions', 'universeRegionFileUpload'),
                ('Type of shuffling (horizontal or vertical): ', 'shufflingType'),
                ('Shuffling distribution: ', 'shufflingDistribution'),
                ('Preserve clumping of genomic regions? ', 'preserveClumping'),
                ('Allow overlap of shuffled locations? ', 'allowOverlaps'),
                ('Allow truncation of sizes in special cases? ', 'truncateSizes'),
                ('Should the shuffling be reproducible? ', 'reproduceShuffling'),
                ('Enter a seed value in the textbox: ', 'enterSeed')] \
               + cls.getInputBoxNamesForRandAlgSelection() \
                + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxIsBasic():
        return False

    @classmethod
    def getOptionsBoxToolDescTop(cls, prevChoices):
        core = HtmlCore()
        core.bigHeader('genomic-permutation-tools')
        core.smallHeader('a collection of permutation approaches to shuffle genomic regions')
        core.divider()
        return '__rawStr__', str(core)

    CUSTOM_REFERENCE_GENOME = 'Custom reference genome'


    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        return '__genome__'
        #return ['Human (hg19)', 'Human (hg38)', 'Mouse (mm9)', 'Mouse (mm10)',cls.CUSTOM_REFERENCE_GENOME]

    @classmethod
    def getOptionsBoxChooseChrnLenFile(cls, prevChoices):
        # if prevChoices.missingGenome:
        if prevChoices.genome == cls.CUSTOM_REFERENCE_GENOME:
            return ('__history__',)

    SINGLE_TRACK = 'Single genomic track'
    MULTIPLE_TRACKS = 'Multiple genomic tracks'

    @classmethod
    def getOptionsBoxNumberOfTracks(cls, prevChoices):  # Alt: getOptionsBox1()
        return [cls.SINGLE_TRACK, cls.MULTIPLE_TRACKS]

    HORIZONTAL = 'Shuffling should be within each genomic track'
    VERTICAL = 'Shuffling should be across all the multiple tracks'
    @classmethod
    def getOptionsBoxShufflingType(cls, prevChoices):
        if prevChoices.numberOfTracks in [cls.MULTIPLE_TRACKS]:
            return [cls.HORIZONTAL, cls.VERTICAL]

    WITHIN = 'shuffle within each chromosome'
    ACROSS = 'shuffle across chromosomes'
    @classmethod
    def getOptionsBoxShufflingDistribution(cls, prevChoices):
            return [cls.WITHIN, cls.ACROSS]

    PRESERVE = 'Preserve the distances between genomic regions'
    IGNORE = 'Ignore clumping of genomic regions when shuffling'

    @classmethod
    def getOptionsBoxPreserveClumping(cls, prevChoices):
        return [cls.PRESERVE, cls.IGNORE]

    ALLOW = 'Allow the shuffled regions to overlap'
    NO = 'Do not allow the shuffled regions to overlap'
    @classmethod
    def getOptionsBoxAllowOverlaps(cls, prevChoices):
        return [cls.ALLOW, cls.NO]

    TRUNCATE = 'Truncate the sizes of genomic regions in special cases'
    CANNOT = 'Do not truncate the sizes of genomic regions'

    @classmethod
    def getOptionsBoxTruncateSizes(cls, prevChoices):
        return [cls.TRUNCATE, cls.CANNOT]

    YES = 'Make the shuffling reproducible'
    UNNECESSARY= 'Not required'

    @classmethod
    def getOptionsBoxReproduceShuffling(cls, prevChoices):
        return [cls.UNNECESSARY,cls.YES]

    @classmethod
    def getOptionsBoxEnterSeed(cls, prevChoices):
        if prevChoices.reproduceShuffling in [cls.YES]:
            return ('textbox')

    @classmethod
    def getOptionsBoxChooseTrackFiles(cls, prevChoices):
        if prevChoices.numberOfTracks in [cls.SINGLE_TRACK,cls.MULTIPLE_TRACKS]:
            return ('__history__', 'bed','gsuite')

    WHOLE_GENOME = 'No, use the whole genome'
    EXPLICIT_UNIVERSE = 'Yes, perform the shuffling only in the explicit set of regions supplied'

    @classmethod
    def getOptionsBoxUniverseRegions(cls, prevChoices):  # Alt: getOptionsBox2()
            return [cls.WHOLE_GENOME, cls.EXPLICIT_UNIVERSE]

    @classmethod
    def getOptionsBoxUniverseRegionFileUpload(cls, prevChoices):
        if prevChoices.universeRegions in [cls.EXPLICIT_UNIVERSE]:
            return ('__history__', 'bed')

    @classmethod
    def getOptionsBoxFirstKey(cls):  # Alt: getOptionsBox1()
        """
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        Mandatory for the first key defined in getInputBoxNames(), if any.

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more
          advanced hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) |
                                ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting Galaxy dataset info, as
            described below.

        History check box list: ('__multihistory__', ) |
                                ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with Galaxy dataset ids as key (the number YYYY
            as described below), and the associated Galaxy dataset info as the
            values, given that the history element is ticked off by the user.
            If not, the value is set to None. The Galaxy dataset info structure
            is described below.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'],
                                 ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False),
                                             ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).


        ###
        Note about the "Galaxy dataset info" data structure:
        ###

        "Galaxy dataset info" is a list of strings coding information about a
        Galaxy history element and its associated dataset, typically used to
        provide info on the history element selected by the user as input to a
        ProTo tool.

        Structure:
            ['galaxy', fileFormat, path, name]

        Optionally encoded as a single string, delineated by colon:

            'galaxy:fileFormat:path:name'

        Where:
            'galaxy' used for assertions in the code
            fileFormat (or suffix) contains the file format of the dataset, as
                encoded in the 'format' field of a Galaxy history element.
            path (or file name/fn) is the disk path to the dataset file.
                Typically ends with 'XXX/dataset_YYYY.dat'. XXX and YYYY are
                numbers which are extracted and used as an unique id  of the
                dataset in the form [XXX, YYYY]
            name is the title of the history element

        The different parts can be extracted using the functions
        extractFileSuffixFromDatasetInfo(), extractFnFromDatasetInfo(), and
        extractNameFromDatasetInfo() from the module CommonFunctions.py.
        """
        return ['testChoice1', 'testChoice2', '...']

    @classmethod
    def getOptionsBoxSecondKey(cls, prevChoices):  # Alt: getOptionsBox2()
        """
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).

        Mandatory for the subsequent keys (after the first key) defined in
        getInputBoxNames(), if any.
        """
        return ''

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     """
    #     Defines a set of demo inputs to the option boxes in the
    #     order defined by getOptionBoxNames and getOptionsBoxOrder.
    #     If not None, a Demo button appears in the interface. Clicking the
    #     button fills the option boxed with the defined demo values.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     """
    #     Defines extra history elements to be created when clicking execute.
    #     This is defined by a list of HistElement objects, as in the
    #     following example:
    #
    #        from proto.GeneralGuiTool import HistElement
    #        return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]
    #
    #     It is good practice to use class constants for longer strings.
    #
    #     In the execute() method, one typically needs to fetch the path to
    #     the dataset referred to by the extra history element. To fetch the
    #     path, use the dict cls.extraGalaxyFn with the defined history title
    #     as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than
        'html', the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional
        files can be put (cls, e.g. generated image files). choices is a list
        of selections made by web-user in each options box.

        Mandatory unless isRedirectTool() returns True.
        """
        choices_gsuite = choices.chooseTrackFiles
        genome =  choices.genome
        analysisBins = UserBinMixin.getUserBinSource(choices)

        ts = getFlatTracksTS(genome, choices_gsuite)
        randTvProvider = cls._createTrackViewProvider(ts, analysisBins, choices.genome, choices.randType, choices.randAlg, False, None) #the last False and non are temporary..
        randomizedTs = getRandomizedVersionOfTs(ts, randTvProvider)

        #output files
        outputGSuite = GSuite()
        for singleTrackTs in randomizedTs.getLeafNodes():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName= os.path.sep.join(singleTrackTs.track.trackName) + '.randomized',
                                                suffix='bed')

            title = singleTrackTs.metadata.pop('title')
            gSuiteTrack = GSuiteTrack(uri, title=title + '.randomized', fileFormat='primary', trackType='segments', genome=genome, attributes=singleTrackTs.metadata)
            outputGSuite.addTrack(gSuiteTrack)
            singleTrackTs.metadata['trackFilePath'] = gSuiteTrack.path

        spec = AnalysisSpec(TsWriterStat)

        res = doAnalysis(spec, analysisBins, randomizedTs)

        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def _createTrackViewProvider(cls, origTs, binSource, genome, randType, randAlg, selectExcludedTrack, excludedTrack):
        reqArgs = getRequiredArgsForAlgorithm(randType, randAlg)
        kwArgs = getKwArgsForAlgorithm(randType, randAlg)

        args = []
        for arg in reqArgs:
            if arg == EXCLUDED_TS_ARG:
                if selectExcludedTrack == cls.YES:
                    raise NotImplementedError()
                    excludedTs = getSingleTrackTS(genome, excludedTrack)
                else:
                    excludedTs = None
                args.append(excludedTs)
            if arg == BIN_SOURCE_ARG:
                args.append(binSource)

        tvProvider = TsRandAlgorithmRegistry.createTrackViewProvider(
            randType, randAlg, *args, **kwArgs
        )

        tvProvider.setOrigTrackStructure(origTs)
        tvProvider.setBinSource(binSource)

        return tvProvider

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.

        Optional method. Default return value if method is not defined: None
        """
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     """
    #     Specifies whether the tool is accessible to all users. If False, the
    #     tool is only accessible to a restricted set of users as well as admin
    #     users, as defined in the galaxy.ini file.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #
    #     Mandatory method if isRedirectTool() returns True.
    #     """
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     """
    #     Specifies if this tool could be run from batch using the batch. The
    #     batch run line can be fetched from the info box at the bottom of the
    #     tool.
    #
    #     Optional method. Default return value if method is not defined:
    #         same as isHistoryTool()
    #     """
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     """
    #     Specifies whether changing the content of textboxes causes the page
    #     to reload. Returning False stops the need for reloading the tool
    #     after each input, resulting in less lags for the user.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     """
    #     Specifies a list of input boxes which resets the subsequent stored
    #     choices previously made. The input boxes are specified by index
    #     (starting with 1) or by key.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #
    #     Optional method. Default return value if method is not defined: ''
    #     """
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     """
    #     Specifies an id used by StaticFile.py to reference an illustration
    #     file on disk. The id is a list of optional directory names followed
    #     by a filename. The base directory is STATIC_PATH as defined by
    #     Config.py. The full path is created from the base directory
    #     followed by the id.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     """
    #     Specifies whether the debug mode is turned on. Debug mode is
    #     currently mostly used within the Genomic HyperBrowser and will make
    #     little difference in a plain Galaxy ProTo installation.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     """
    #     The format of the history element with the output of the tool. Note
    #     that if 'html' is returned, any print statements in the execute()
    #     method is printed to the output dataset. For text-based output
    #     (e.g. bed) the output dataset only contains text written to the
    #     galaxyFn file, while all print statements are redirected to the info
    #     field of the history item box.
    #
    #     Note that for 'html' output, standard HTML header and footer code is
    #     added to the output dataset. If one wants to write the complete HTML
    #     page, use the restricted output format 'customhtml' instead.
    #
    #     Optional method. Default return value if method is not defined:
    #     'html'
    #     """
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """
