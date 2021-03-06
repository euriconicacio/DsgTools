# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgTools
                                 A QGIS plugin
 Brazilian Army Cartographic Production Tools
                              -------------------
        begin                : 2014-11-08
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Luiz Andrade - Cartographic Engineer @ Brazilian Army
        email                : luiz.claudio@dsg.eb.mil.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import json
class Utils:
    def mergeDict(self, dictionary1, dictionary2):
        '''
        Merges two dictionaries
        '''
        output = dict()
        if type(dictionary1) <> dict or type(dictionary2) <> dict:
            return dictionary2
        for item, value in dictionary1.iteritems():
            if dictionary2.has_key(item):
                if isinstance(dictionary2[item], dict):
                    output[item] = self.mergeDict(value, dictionary2.pop(item))
                else:
                    if type(value) == list:
                        if item not in output.keys():
                            output[item] = []
                        for i in value:
                            if i not in output[item]:
                                output[item].append(i)
                        output[item].extend(self.mergeDict(value, dictionary2.pop(item)))
                    else:
                        output[item] = self.mergeDict(value, dictionary2.pop(item))
            else:
                if type(value) == list:
                    if item not in output.keys():
                        output[item]=[]
                    for i in value:
                        if i not in output[item]:
                            output[item].append(i)
                else:
                    output[item] = value
        for item, value in dictionary2.iteritems():
            if type(value) == list:
                if item not in output.keys():
                    output[item]=[]
                for i in value:
                    if i not in output[item]:
                        output[item].append(i)
            else:
                output[item] = value
        return output
    
    def buildOneNestedDict(self, inputDict, keyList, value):
        '''
        Builds a nested dictionary for a specific key
        '''
        if len(keyList) == 1:
            if keyList[0] not in inputDict.keys():
                inputDict[keyList[0]] = dict()
            if type(value) == list:
                inputDict[keyList[0]]=[]
                for i in value:
                    if i not in inputDict[keyList[0]]:
                        inputDict[keyList[0]].append(i)
            else:
                inputDict[keyList[0]]=value
            return inputDict
        else:
            if keyList[0] not in inputDict.keys():
                if len(inputDict.values()) == 0:
                    inputDict[keyList[0]] = dict()
            inputDict[keyList[0]] = self.buildOneNestedDict(inputDict[keyList[0]], keyList[1::], value)
            return inputDict
    
    def buildNestedDict(self, inputDict, keyList, value):
        '''
        Builds a nested dict
        '''
        if len(inputDict.keys())>0:
            tempDict = self.buildOneNestedDict(dict(), keyList, value)
            return self.mergeDict(inputDict, tempDict)
        else:
            return self.buildOneNestedDict(inputDict, keyList, value)
    
    def readJsonFile(self, filename):
        '''
        Reads a json file and makes a dictionary
        '''
        try:
            file = open(filename, 'r')
            data = file.read()
            fileDict = json.loads(data)
            file.close()
            return fileDict
        except:
            return dict()