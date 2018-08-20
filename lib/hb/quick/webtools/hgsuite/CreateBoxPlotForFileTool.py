from collections import OrderedDict
import numpy

from proto.StaticFile import StaticImage
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from quick.util.CommonFunctions import extractFileSuffixFromDatasetInfo
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


class CreateBoxPlotForFileTool(GeneralGuiTool):

    TITLE = 'title'

    @classmethod
    def getToolName(cls):
        return "Create box plot for tabular file or hGSuite"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select file', 'selFile'),
                ('Do you want to have box plot separately for category', 'response'),
                ('Select category', 'responseValue'),
                ('Select column', 'selCol'),
                ('Include 0 values to count results', 'resValue')
                ]

    @staticmethod
    def getOptionsBoxSelFile():
        return GeneralGuiTool.getHistorySelectionElement('tabular', 'gsuite')

    @classmethod
    def getOptionsBoxResponse(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def getOptionsBoxResponseValue(cls, prevChoices):
        if prevChoices.response == 'yes':
            if prevChoices.selFile:
                suffixForFile = extractFileSuffixFromDatasetInfo(prevChoices.selFile)
                if suffixForFile == 'tabular':
                    return cls.returnColFile(prevChoices.selFile, asListResponse=True)
                if suffixForFile == 'gsuite':
                    gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile)
                    return cls.returnColFile(prevChoices.selFile, asListResponse=True, gSuiteAttributes=gSuite.attributes+[cls.TITLE])


    @classmethod
    def getOptionsBoxSelCol(cls, prevChoices):
        if prevChoices.selFile:
            suffixForFile = extractFileSuffixFromDatasetInfo(prevChoices.selFile)
            if prevChoices.response == 'yes':
                if suffixForFile == 'tabular':
                    return cls.returnColFile(prevChoices.selFile)
                if suffixForFile == 'gsuite':
                    gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile)
                    return cls.returnColFile(prevChoices.selFile,
                                      gSuiteAttributes=gSuite.attributes + [cls.TITLE])
            else:
                if suffixForFile == 'tabular':
                    return cls.returnColFile(prevChoices.selFile)
                if suffixForFile == 'gsuite':
                    gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile)
                    return cls.returnColFile(prevChoices.selFile,
                                      gSuiteAttributes=gSuite.attributes + [cls.TITLE])



    @classmethod
    def getOptionsBoxResValue(cls, prevChoices):
        return ['yes', 'no']



    @classmethod
    def returnColFile(cls, selFile2, asListResponse=False, gSuiteAttributes=None):
        if gSuiteAttributes != None:
            header = gSuiteAttributes
        else:
            with open(ExternalTrackManager.extractFnFromGalaxyTN(selFile2.split(':')),
                      'r') as f:
                header = f.readline()
                header = header.strip('\n').split('\t')

        if asListResponse == False:
            hDict = OrderedDict()
            for h in header:
                hDict[h] = False
        if asListResponse == True:
            hDict = []
            for h in header:
                hDict.append(h)



        return hDict

    @classmethod
    def openGSuiteFileWithCategories(cls, fileName, selCol, colNameAttributes):

        gSuite = getGSuiteFromGalaxyTN(fileName)
        attributeList = gSuite.attributes

        dataAll = OrderedDict()

        categories = list(set(gSuite.getAttributeValueList(colNameAttributes)))
        for i, iTrack in enumerate(gSuite.allTracks()):

            attr = iTrack.getAttribute(colNameAttributes)
            if not attr in dataAll.keys():
                dataAll[attr] = []
            val = iTrack.getAttribute(selCol)
            try:
                if val == 'nan' or val == None:
                    dataAll[attr].append(0)
                else:
                    dataAll[attr].append(float(val))
            except:
                pass

        return dataAll, categories

    @classmethod
    def openFileWithCategories(cls, fileName, colName, colNameAttributes):
        allData = OrderedDict()
        categories = []
        fN = fileName.split(':')
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fN), 'r') as f:
            i = 0
            cna = 0

            for line in f:
                l = line.strip('\n').split('\t')
                if i == 0:
                    # inxColName = l.index(k.encode('utf-8'))
                    # allData[inxColName] = {}
                    #categories.append(k.encode('utf-8'))
                    cna = l.index(colNameAttributes)
                    k = l.index(colName)

                else:
                    if l != ['']:

                        try:
                            attr = l[cna]
                            if not attr in allData.keys():
                                allData[attr]=[]
                                categories.append(attr.encode('utf-8'))
                            if l[k] == 'nan':
                                allData[attr].append(0)
                            else:
                                allData[attr].append(float(l[k]))

                        except:
                            pass
                i += 1
        return allData, categories

    @classmethod
    def openFile(cls, fileName, colName):
        allData = OrderedDict()
        categories = []
        fN = fileName.split(':')
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fN), 'r') as f:
            i = 0
            for line in f:
                l = line.strip('\n').split('\t')
                if i == 0:
                    for k, it in colName.iteritems():
                        if it != False:
                            inxColName = l.index(k.encode('utf-8'))
                            allData[inxColName] = []
                            categories.append(k.encode('utf-8'))
                else:
                    if l != ['']:
                        for k in allData.keys():
                            try:
                                if l[k] == 'nan' or l[k] == None:
                                    allData[k].append(0)
                                else:
                                    allData[k].append(float(l[k]))
                            except:
                                pass
                i += 1
        return allData, categories

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selFile = choices.selFile
        selCol = choices.selCol
        resValue = choices.resValue
        response = choices.response

        suffixForFile = extractFileSuffixFromDatasetInfo(choices.selFile)

        if response == "yes":
            res = ""
            for k, it in selCol.iteritems():
                if it != False:
                    sc = k
                    responseValue = choices.responseValue
                    if suffixForFile == 'tabular':
                        dataAll, categories = cls.openFileWithCategories(selFile, sc, responseValue)

                    if suffixForFile == 'gsuite':
                        dataAll, categories = cls.openGSuiteFileWithCategories(selFile, sc, responseValue)

                    #outputFile = open(cls.makeHistElement(galaxyExt='customhtml', title=sc), 'w')
                    res += str(cls.printResultsForBoxPlot(sc, categories, choices, dataAll, galaxyFn, resValue))
                    #outputFile.write(str(res))
                    #outputFile.close()
            print res
        else:
            if suffixForFile == 'tabular':
                dataAll, categories = cls.openFile(selFile, selCol)
            if suffixForFile == 'gsuite':
                dataAll, categories = cls.openGSuiteFile(selFile, selCol)


            print cls.printResultsForBoxPlot(selCol, categories, choices, dataAll, galaxyFn, resValue)


    @classmethod
    def printResultsForBoxPlot(cls, selCol, categories, choices, dataAll, galaxyFn, resValue):
        dataForBoxPlot = []
        prettyResults = {}
        i = 0
        for data in dataAll.itervalues():

            if resValue == 'no':
                data = [d for d in data if d > 0]
            countedData = [min(data), numpy.percentile(data, 25), numpy.percentile(data, 50),
                           numpy.percentile(data, 75), max(data)]
            dataForBoxPlot.append(countedData)
            s = 0
            if len(data) > 0:
                s = float(sum(data)) / float(len(data))
            prettyResults[categories[i]] = countedData + [s, float(sum(data)), float(len(data))]
            i += 1
        vg = visualizationGraphs()
        categoriesSorted, dataForBoxPlotSorted = (list(t) for t in
                                                  zip(*sorted(zip(categories, dataForBoxPlot))))
        plot = vg.drawBoxPlotChart(dataForBoxPlotSorted,
                                   categories=categoriesSorted,
                                   seriesName='values',
                                   xAxisRotation=90,
                                   titleText=selCol)
        core = HtmlCore()
        core.begin()
        shortQuestion = 'results'
        addTableWithTabularAndGsuiteImportButtons(
            core,
            choices,
            galaxyFn,
            shortQuestion,
            tableDict=prettyResults,
            columnNames=['Column'] + ['Minimum', 'Lower quantile', 'Median', 'Upper quantile',
                                      'Maximum', 'Average', 'Sum', 'Elements number']
        )
        core.line(plot)
        core.end()
        return core

    @classmethod
    def openGSuiteFile(cls, selFile, selCol):
        gSuite = getGSuiteFromGalaxyTN(selFile)
        attributeList = gSuite.attributes

        dataAll = OrderedDict()
        categories = []
        for k, it in selCol.iteritems():
            if it != False:
                inxColName = attributeList.index(k.encode('utf-8'))
                if k == cls.TITLE:
                    dataAll[inxColName] = gSuite.allTrackTitles()
                else:
                    if not inxColName in dataAll.keys():
                        dataAll[inxColName] = []
                    for val in gSuite.getAttributeValueList(k):
                        try:
                            if val == 'nan' or val == None:
                                dataAll[inxColName].append(0)
                            else:
                                dataAll[inxColName].append(float(val))
                        except:
                            pass

                categories.append(k.encode('utf-8'))

        return dataAll, categories

    @classmethod
    def _checkType(cls, l):
        if len(l) == 0:
            return 0
        for x in l:
            try:
                float(x)
            except:
                return 0
        return 1

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices.selFile:
            suffixForFile = extractFileSuffixFromDatasetInfo(choices.selFile)
            if choices.responseValue == "yes":
                for k, it in choices.selCol.iteritems():
                    if it != False:
                        sc = k
                        responseValue = choices.responseValue
                        if suffixForFile == 'tabular':
                            dataAll, categories = cls.openFileWithCategories(choices.selFile, sc,
                                                                             responseValue)

                        if suffixForFile == 'gsuite':
                            dataAll, categories = cls.openGSuiteFileWithCategories(choices.selFile, sc,
                                                                                   responseValue)
            else:
                if suffixForFile == 'tabular':
                    dataAll, categories = cls.openFile(choices.selFile, choices.selCol)
                if suffixForFile == 'gsuite':
                    dataAll, categories = cls.openGSuiteFile(choices.selFile, choices.selCol)

            howManycY = 0
            cY = 0
            for keyD, itD in dataAll.iteritems():
                cY += cls._checkType(dataAll[keyD])
                howManycY += 1

            if cY != howManycY:
                return 'All the values need to be number type.'

    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'

    @staticmethod
    def isPublic():
        return True

    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to present metadata columns from gSuite or results from tabular file in the box chart.'

        stepsToRunTool = ['Select file',
                          'Do you want to have box plot separately for category',
                          'Select category',
                          'Select column',
                          'Include 0 values to count results'
                          ]
        urlexample1Output = StaticImage(['hgsuite', 'img',
                                         'CreateBoxPlotForFileTool-img1.png']).getURL()



        example = {'Example 1 (Series: Single; chart type: heatmap; file: tabular)': ['', ["""
        attribute0	attribute1	attribute2	attribute3
        track6.bed-CG	track6.bed	CG	1
        track6.bed-CA	track6.bed	CA	0
        track3.bed-CG	track3.bed	CG	0
        track3.bed-CA	track3.bed	CA	1
        track1.bed-CG	track1.bed	CG	0
        track1.bed-CA	track1.bed	CA	2
        track2.bed-CG	track2.bed	CG	0
        track2.bed-CA	track2.bed	CA	5
        track4.bed-CG	track4.bed	CG	0
        track4.bed-CA	track4.bed	CA	1
        track5.bed-CG	track5.bed	CG	1
        track5.bed-CA	track5.bed	CA	0


                    """],
          [
              ['Select file','tabular'],
              ['Do you want to have box plot separately for category','yes'],
              ['Select category','attribute2'],
              ['Select column','attribute3'],
              ['Include 0 values to count results', 'no']
        ],
          [
              '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample1Output + '" /></div>'
          ]
          ]
        }

        toolResult = 'The results are presented in an interactive box chart.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example
                                          )