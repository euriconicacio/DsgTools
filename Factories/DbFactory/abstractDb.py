# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgTools
                                 A QGIS plugin
 Brazilian Army Cartographic Production Tools
                              -------------------
        begin                : 2015-10-21
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Philipe Borba - Cartographic Engineer @ Brazilian Army
        email                : borba@dsg.eb.mil.br
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
import os
from uuid import uuid4

from osgeo import ogr, osr

# DsgTools imports
from DsgTools.Factories.SqlFactory.sqlGeneratorFactory import SqlGeneratorFactory
from DsgTools.Utils.utils import Utils

#PyQt imports
from PyQt4.QtSql import QSqlQuery, QSqlDatabase
from PyQt4.QtCore import QSettings, SIGNAL, pyqtSignal, QObject

#Qgis imports
import qgis.core 

class DbSignals(QObject):
        updateLog = pyqtSignal(str)
        clearLog = pyqtSignal()

class AbstractDb(QObject):
    def __init__(self):
        '''
        Constructor
        '''
        super(AbstractDb,self).__init__()
        self.conversionTypeDict = dict({'QPSQL':'postgis','QSQLITE':'spatialite'})
        self.utils = Utils()
        self.signals = DbSignals()
        self.slotConnected = False
        pass
    
    def __del__(self):
        '''
        Destructor
        '''
        if self.db.isOpen():
            self.db.close()
            self.db = None
            
    def checkAndOpenDb(self):
        '''
        Check and open the database
        '''
        if not self.db.isOpen():
            if not self.db.open():
                raise Exception(self.tr('Error opening database: ')+self.db.lastError().text())

    def getType(self):
        '''
        Gets the driver name
        '''
        return self.db.driverName()

    def countElements(self, layers):
        '''
        Counts the number of elements in each layer present in layers
        '''
        self.checkAndOpenDb()
        listaQuantidades = []
        for layer in layers:
            (table,schema)=self.getTableSchema(layer)
            if layer.split('_')[-1] in ['p','l','a'] or schema == 'complexos':
                sql = self.gen.getElementCountFromLayer(layer)
                query = QSqlQuery(sql,self.db)
                query.next()
                number = query.value(0)
                if not query.exec_(sql):
                    raise Exception(self.tr("Problem counting elements: ")+query.lastError().text())
                listaQuantidades.append([layer, number])
        return listaQuantidades     

    def findEPSG(self):
        '''
        Finds the database EPSG
        '''
        self.checkAndOpenDb()
        sql = self.gen.getSrid()
        query = QSqlQuery(sql, self.db)
        if not query.isActive():
            raise Exception(self.tr("Problem finding EPSG: ")+query.lastError().text())
        srid = -1
        while query.next():
            srid = query.value(0)
        return srid

    def listWithElementsFromDatabase(self, classList):
        '''
        List classes with elements
        classList: class list
        '''
        self.checkAndOpenDb()
        classListWithNumber = self.countElements(classList)
        classesWithElements = dict()
        for cl in classListWithNumber:
            if cl[1]>0:
                classesWithElements[cl[0]]=cl[1]   
        return classesWithElements

    def listClassesWithElementsFromDatabase(self):
        '''
        List classes with elements. Uses all classes (complex included)
        '''
        geomClassList = self.listGeomClassesFromDatabase()
        complexClassList = self.listComplexClassesFromDatabase()
        classList = []
        for g in geomClassList:
            classList.append(g)
        for c in complexClassList:
            classList.append(c)
        classList.sort()
        return self.listWithElementsFromDatabase(classList)

    def getAggregationAttributes(self):
        '''
        Gets complex link columns
        '''
        self.checkAndOpenDb()
        columns = []
        sql = self.gen.getAggregationColumn()
        query = QSqlQuery(sql, self.db)
        if not query.isActive():
            raise Exception(self.tr("Problem getting aggregation attributes: ")+query.lastError().text())
        while query.next():
            value = query.value(0)
            columns.append(value)
        return columns

    def getOgrDatabase(self):
        '''
        Builds a OGR database
        '''
        if self.ogrDb != None:
            self.buildOgrDatabase()
            return self.ogrDb

    def buildFieldMap(self):
        '''
        Gets database structure according to the edgv version
        '''
        self.checkAndOpenDb()
        fieldMap = self.getStructureDict()
        return fieldMap

    def validateWithOutputDatabaseSchema(self, outputAbstractDb):
        return None
    
    def convertDatabase(self, outputAbstractDb, type):
        '''
        Converts database
        '''
        self.signals.clearLog.emit()
        if outputAbstractDb.db.driverName() == 'QPSQL':
            return self.convertToPostgis(outputAbstractDb,type)
        if outputAbstractDb.db.driverName() == 'QSQLITE':
            return self.convertToSpatialite(outputAbstractDb,type)
        return None
    
    def makeValidationSummary(self, invalidatedDataDict):
        '''
        Makes the database conversion validation summary
        '''
        hasErrors = False
        for key in invalidatedDataDict.keys():
            if len(invalidatedDataDict[key]) > 0:
                hasErrors = True
        if hasErrors:
            self.signals.updateLog.emit('\n'+'{:-^60}'.format(self.tr('Validation Problems Summary')))
            for key in invalidatedDataDict.keys():
                
                if key == 'nullLine' and len(invalidatedDataDict[key])>0:
                    self.signals.updateLog.emit('\n\n'+self.tr('Classes with null lines:')+'\n')
                    self.signals.updateLog.emit('\n\n'+'{:<50}'.format(self.tr('Class'))+self.tr('Elements')+'\n\n')
                    for cl in invalidatedDataDict[key].keys():
                        self.signals.updateLog.emit('{:<50}'.format(cl)+str(invalidatedDataDict[key][cl])+'\n')

                if key == 'nullPk' and len(invalidatedDataDict[key])>0:
                    self.signals.updateLog.emit('\n\n'+self.tr('Classes with null primary keys:')+'\n')
                    self.signals.updateLog.emit('\n\n'+'{:<50}'.format(self.tr('Class'))+self.tr('Elements')+'\n\n')
                    for cl in invalidatedDataDict[key].keys():
                        self.signals.updateLog.emit('{:<50}'.format(cl)+str(invalidatedDataDict[key][cl])+'\n')

                if key == 'notInDomain' and len(invalidatedDataDict[key])>0:
                    self.signals.updateLog.emit('\n\n'+self.tr('Features with attributes not in domain:')+'\n\n')
                    for cl in invalidatedDataDict[key].keys():
                        self.signals.updateLog.emit('\n'+self.tr('Class: ')+cl+'\n')
                        for id in invalidatedDataDict[key][cl].keys():
                            attrCommaList = '(id,'+','.join(invalidatedDataDict[key][cl][id].keys())+') = '
                            at = invalidatedDataDict[key][cl][id].keys()
                            valueList = '('+str(id)
                            for i in range(len(at)):
                                valueList += ','+str(invalidatedDataDict[key][cl][id][at[i]])
                            valueList += ')\n'
                            self.signals.updateLog.emit(attrCommaList+valueList)

                if key == 'nullAttribute' and len(invalidatedDataDict[key])>0:
                    self.signals.updateLog.emit('\n\n'+self.tr('Features with null attributes in a not null field:')+'\n\n')
                    for cl in invalidatedDataDict[key].keys():
                        self.signals.updateLog.emit(self.tr('Class: ')+cl+'\n')
                        for id in invalidatedDataDict[key][cl].keys():
                            attrCommaList = '(id,'+','.join(invalidatedDataDict[key][cl][id].keys())+') = '
                            valueList = '('+str(id)
                            for attr in invalidatedDataDict[key][cl][id].keys():
                                valueList += ','+str(invalidatedDataDict[key][cl][id][attr])
                            valueList += ')\n'
                            self.signals.updateLog.emit(attrCommaList+valueList)
                            
                if key == 'classNotFoundInOutput' and len(invalidatedDataDict[key])>0:
                    self.signals.updateLog.emit('\n\n'+self.tr('Classes with classes that have elements but do not have output equivalent:')+'\n\n')
                    for cl in invalidatedDataDict[key]:
                            self.signals.updateLog.emit(self.tr('Class: ')+cl+'\n')
                
                if key == 'attributeNotFoundInOutput' and len(invalidatedDataDict[key])>0:
                    self.signals.updateLog.emit('\n\n'+self.tr('Classes with attributes that have no output attribute equivalent:')+'\n\n')
                    for cl in invalidatedDataDict[key].keys():
                        self.signals.updateLog.emit(self.tr('Class: ')+cl+'\n')
                        valueList = '('+','.join(invalidatedDataDict[key][cl])+')\n'
                        self.signals.updateLog.emit(valueList)
                
        return hasErrors
            
    def buildReadSummary(self,inputOgrDb,outputAbstractDb,classList):
        '''
        Builds the conversion read summary
        '''
        self.signals.clearLog.emit() #Clears log
        inputType = self.conversionTypeDict[self.db.driverName()]
        outputType = self.conversionTypeDict[outputAbstractDb.db.driverName()]
        self.signals.updateLog.emit(self.tr('Conversion type: ')+inputType+'2'+outputType+'\n')
        self.signals.updateLog.emit('\n'+self.tr('Input database: ')+self.db.databaseName()+'\n')
        self.signals.updateLog.emit('\n'+self.tr('Output database: ')+outputAbstractDb.db.databaseName()+'\n')
        self.signals.updateLog.emit('\n'+'{:-^60}'.format(self.tr('Read Summary')))
        self.signals.updateLog.emit('\n\n'+'{:<50}'.format(self.tr('Class'))+self.tr('Elements')+'\n\n')
        for cl in classList:
            self.signals.updateLog.emit('{:<50}'.format(cl)+str(inputOgrDb.GetLayerByName(str(cl)).GetFeatureCount())+'\n')
        return None
    
    def makeTranslationMap(self, layerName, layer, outLayer, fieldMapper):
        '''
        Makes the translation map
        '''
        layerFieldMapper=fieldMapper[layerName]
        layerDef = layer.GetLayerDefn()
        outLayerDef = outLayer.GetLayerDefn()
        panMap = []        
        for i in range(layerDef.GetFieldCount()):
            featureDef = layerDef.GetFieldDefn(i)
            fieldName = featureDef.GetName()
            if fieldName in layerFieldMapper.keys():
                name = layerFieldMapper[fieldName]
                fieldId = outLayerDef.GetFieldIndex(name)
                panMap.append(fieldId) 
            else:
                panMap.append(-1)
        return panMap
    
    def translateLayer(self, inputLayer, inputLayerName, outputLayer, outputFileName, layerPanMap, errorDict, defaults={}, translateValues={}):
        '''
        Makes the layer conversion
        '''
        inputLayer.ResetReading()
        inSpatialRef = inputLayer.GetSpatialRef()
        outSpatialRef = outputLayer.GetSpatialRef()
        coordTrans = None
        if inSpatialRef <> outSpatialRef:
            coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        initialCount = outputLayer.GetFeatureCount()
        count = 0
        feat=inputLayer.GetNextFeature()
        #for feat in inputLayer:
        while feat:
            inputId = feat.GetFID()
            if feat.geometry().GetGeometryCount() > 1:
                #Deaggregator
                for geom in feat.geometry():
                    newFeat=ogr.Feature(outputLayer.GetLayerDefn())
                    newFeat.SetFromWithMap(feat,True,layerPanMap)
                    auxGeom = ogr.Geometry(newFeat.geometry().GetGeometryType())
                    auxGeom.AssignSpatialReference(newFeat.geometry().GetSpatialReference())
                    auxGeom.AddGeometry(geom)
                    if coordTrans <> None:
                        auxGeom.Transform(coordTrans)
                    newFeat.SetGeometry(auxGeom)
                    out=outputLayer.CreateFeature(newFeat)
                    if out <> 0:
                        self.utils.buildNestedDict(errorDict, [inputLayerName], [inputId])
                    else:
                        count += 1
            else:
                newFeat=ogr.Feature(outputLayer.GetLayerDefn())
                newFeat.SetFromWithMap(feat,True,layerPanMap)
                if coordTrans <> None:
                    geom = feat.GetGeometryRef()
                    geom.Transform(coordTrans)
                    newFeat.SetGeometry(geom)
                out=outputLayer.CreateFeature(newFeat)
                if out <> 0:
                    self.utils.buildNestedDict(errorDict, [inputLayerName], [inputId])
                else:
                    count += 1
            feat=inputLayer.GetNextFeature()
            
        return count
    
    def translateDS(self, inputDS, outputDS, fieldMap, inputLayerList, errorDict,invalidated=None):
        '''
        Translates the data source
        '''
        self.signals.updateLog.emit('\n'+'{:-^60}'.format(self.tr('Write Summary')))
        self.signals.updateLog.emit('\n\n'+'{:<50}'.format(self.tr('Class'))+self.tr('Elements')+'\n\n')
        status = False
        for inputLyr in inputLayerList.keys():
            schema = self.getTableSchema(inputLyr)
            attrList = fieldMap[inputLyr].keys()
            
            #sql = self.gen.getFeaturesWithSQL(inputLyr,attrList) #order elements here
            #inputOgrLayer = inputDS.ExecuteSQL(sql.encode('utf-8'))
            #Here I had to change the way of loading because of features ids. I need to use inputDs.GetLayerByName
            
            inputOgrLayer = inputDS.GetLayerByName(str(inputLyr)) #new way of loading layer. The old way was an attempt to make a general rule for conversion between edgv versions
            outputFileName = self.translateOGRLayerNameToOutputFormat(inputLyr,outputDS)
            outputLayer=outputDS.GetLayerByName(outputFileName)
            #order conversion here
            layerPanMap=self.makeTranslationMap(inputLyr, inputOgrLayer,outputLayer, fieldMap)
            ini = outputLayer.GetFeatureCount()
            if invalidated == None:
                iter=self.translateLayer(inputOgrLayer, inputLyr, outputLayer, outputFileName, layerPanMap, errorDict)
            else:
                needsFix = False
                for keyDict in invalidated.values():
                    if len(keyDict) > 0:
                        if type(keyDict) == list:
                            if inputLyr in keyDict:
                                needsFix = True
                        if type(keyDict) == dict:
                            if inputLyr in keyDict.keys():
                                needsFix = True
                                break
                if needsFix:
                    iter = self.translateLayerWithDataFix(inputOgrLayer, inputLyr, outputLayer, outputFileName, layerPanMap, invalidated, errorDict)
                else:
                    iter=self.translateLayer(inputOgrLayer, inputLyr, outputLayer, outputFileName, layerPanMap, errorDict)
            if iter == -1:
                status = False
                self.signals.updateLog.emit('{:<50}'.format(self.tr('Error on layer ')+inputLyr+self.tr('. Conversion not performed.')+'\n'))
                return status
            diff = outputLayer.GetFeatureCount()-ini
            if iter == diff:
                status = True
            else:
                status = False
            self.signals.updateLog.emit('{:<50}'.format(str(outputFileName))+str(diff)+'\n')
        self.writeErrorLog(errorDict)
        outputDS.Destroy()
        return status
    
    def buildInvalidatedDict(self):
        '''
        Builds the initial state of the conversion invalidated dictionary
        '''
        invalidated = dict()
        invalidated['nullLine'] = dict()       
        invalidated['nullPk'] = dict()
        invalidated['notInDomain'] = dict()
        invalidated['nullAttribute'] = dict()
        invalidated['classNotFoundInOutput'] = []
        invalidated['attributeNotFoundInOutput'] = dict()
        return invalidated
    
    def prepareForConversion(self,outputAbstractDb):
        '''
        Executes preconditions for the conversion
        '''
        self.checkAndOpenDb()
        outputAbstractDb.checkAndOpenDb()
        fieldMap = self.buildFieldMap()
        inputOgrDb = self.buildOgrDatabase()
        outputOgrDb = outputAbstractDb.buildOgrDatabase()
        inputLayerList = self.listClassesWithElementsFromDatabase()
        errorDict = dict()
        self.buildReadSummary(inputOgrDb,outputAbstractDb,inputLayerList)
        return (inputOgrDb, outputOgrDb, fieldMap, inputLayerList, errorDict)

    def translateLayerWithDataFix(self, inputLayer, inputLayerName, outputLayer, outputFileName, layerPanMap, invalidated, errorDict, defaults={}, translateValues={}):
        '''
        casos e tratamentos:
        1. nullLine: os atributos devem ser varridos e, caso seja linha nula, ignorar o envio
        2. nullPk: caso seja complexo, gerar uma chave
        3. notInDomain: excluir do mapeamento aquele atributo caso ele seja mapeado
        4. nullAttribute: excluir do mapeamento aquele atributo caso ele seja não nulo
        5. classNotFoundInOutput: pular classe na conversão e mostrar no warning
        6. attributeNotFoundInOutput: pular atributo e mostrar no warning para todas as feicoes
        '''
        inputLayer.ResetReading()
        fieldCount = inputLayer.GetLayerDefn().GetFieldCount()
        initialCount = outputLayer.GetFeatureCount()
        inSpatialRef = inputLayer.GetSpatialRef()
        outSpatialRef = outputLayer.GetSpatialRef()
        coordTrans = None
        if inSpatialRef <> outSpatialRef:
            coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        count = 0
        feat=inputLayer.GetNextFeature()
        (schema,className) = self.getTableSchema(inputLayerName)
        outputOgrLyrDict = self.getOgrLayerIndexDict(outputLayer)
        if inputLayerName not in invalidated['classNotFoundInOutput']:
            while feat:
                nullLine = True
                #Case 1: nullLine
                for i in range(fieldCount):
                    if feat.GetField(i) <> None:
                        nullLine = False
                        break
                if feat.GetFID() <> -1 or feat.geometry() <> None:
                    nullLine = False
                if not nullLine:
                    if inputLayerName not in invalidated['classNotFoundInOutput']:
                        newFeat=ogr.Feature(outputLayer.GetLayerDefn())
                        inputId = feat.GetFID()
                        #Case 2: nullPk in complex:
                        newFeat.SetFromWithMap(feat,True,layerPanMap)
                        if schema == 'complexos' and feat.GetFID() == -1:
                            newFeat.SetFID(uuid4())
                        #Case 3
                        for j in range(inputLayer.GetLayerDefn().GetFieldCount()):
                            if layerPanMap[j] <> -1:
                                if inputLayerName in invalidated['notInDomain'].keys():
                                    if inputId in invalidated['notInDomain'][inputLayerName].keys():
                                        if outputLayer.GetLayerDefn().GetFieldDefn(layerPanMap[j]).GetName() in invalidated['notInDomain'][inputLayerName][inputId].keys():
                                            newFeat.UnsetField(layerPanMap[j])
                                if inputLayerName in invalidated['nullAttribute'].keys():
                                    if inputId in invalidated['nullAttribute'][inputLayerName].keys():
                                        if outputLayer.GetLayerDefn().GetFieldDefn(layerPanMap[j]).GetName() in invalidated['nullAttribute'][inputLayerName][inputId].keys():
                                            if outputLayer.GetLayerDefn().GetFieldDefn(layerPanMap[j]).GetTypeName() == 'String':
                                                newFeat.SetField(layerPanMap[j],'-9999')
                                            if outputLayer.GetLayerDefn().GetFieldDefn(layerPanMap[j]).GetTypeName() == 'Integer':
                                                newFeat.SetField(layerPanMap[j],-9999)
                        if newFeat.geometry().GetGeometryCount() > 1:
                            #Deaggregator
                            for geom in newFeat.geometry():
                                auxGeom = ogr.Geometry(newFeat.geometry().GetGeometryType())
                                auxGeom.AssignSpatialReference(newFeat.geometry().GetSpatialReference())
                                auxGeom.AddGeometry(geom)
                                if coordTrans <> None:
                                    auxGeom.Transform(coordTrans)
                                newFeat.SetGeometry(auxGeom)
                                out=outputLayer.CreateFeature(newFeat)
                                if out <> 0:
                                    self.utils.buildNestedDict(errorDict, [inputLayerName], [inputId])
                                else:
                                    count += 1
                        else:
                            if coordTrans <> None:
                                geom = feat.GetGeometryRef()
                                geom.Transform(coordTrans)
                                newFeat.SetGeometry(geom)
                            out=outputLayer.CreateFeature(newFeat)
                            if out <> 0:
                                self.utils.buildNestedDict(errorDict, [inputLayerName], [inputId])
                            else:
                                count += 1
                feat=inputLayer.GetNextFeature()
            return count
        else:
            return -1
    
    def buildOgrDatabase(self):
        '''
        Build a OGR database
        '''
        con = self.makeOgrConn()
        ogrDb = ogr.Open(con,update=1)
        return ogrDb
    
    def reorderTupleList(self, ls):
        '''
        Reorders a tuple list
        ls: list to be reordered
        '''
        if 'OGC_FID' in ls:
            idField = 'OGC_FID'
        else:
            idField = 'id'
        index = ls.index(idField)
        reordered = [ls[index]]
        reordered.extend(ls[0:index])
        reordered.extend(ls[index+1::])
        return reordered
    
    def getOgrLayerIndexDict(self, lyr):
        '''
        Gets ogr field definitions
        '''
        ogrDict = dict()
        layerDef = lyr.GetLayerDefn()
        for i in range(layerDef.GetFieldCount()):
            ogrDict[i] = layerDef.GetFieldDefn(i).GetName() 
        return ogrDict
    
    def writeErrorLog(self,errorDict):
        '''
        Writes conversion error log
        '''
        errorClasses = errorDict.keys()
        if len(errorClasses)>0:
            self.signals.updateLog.emit('\n'+'{:-^60}'.format(self.tr('Features not converted')))
            self.signals.updateLog.emit('\n\n'+'{:<50}'.format(self.tr('Class'))+self.tr('Feature id')+'\n\n')
            for cl in errorClasses:
                for id in errorDict[cl]:
                    self.signals.updateLog.emit('\n\n'+'{:<50}'.format(cl+str(id)))
    
    def getQmlDir(self):
        '''
        Gets the QML directory
        '''
        self.checkAndOpenDb()
        currentPath = os.path.dirname(__file__)
        if qgis.core.QGis.QGIS_VERSION_INT >= 20600:
            qmlVersionPath = os.path.join(currentPath, '..', '..', 'Qmls', 'qgis_26')
        else:
            qmlVersionPath = os.path.join(currentPath, '..', '..', 'Qmls', 'qgis_22')

        version = self.getDatabaseVersion()
        if version == '3.0':
            qmlPath = os.path.join(qmlVersionPath, 'edgv_30')
        elif version == '2.1.3':
            qmlPath = os.path.join(qmlVersionPath, 'edgv_213')
        elif version == 'FTer_2a_Ed':
            qmlPath = os.path.join(qmlVersionPath, 'FTer_2a_Ed')
        else:
            qmlPath = ''
        return qmlPath
    
    def makeValueRelationDict(self, table, codes):
        '''
        Makes the value relation dictionary (multi valued attributes)
        '''
        self.checkAndOpenDb()
        ret = dict()
        in_clause = '(%s)' % ",".join(map(str, codes))
        sql = self.gen.makeRelationDict(table, in_clause)
        query = QSqlQuery(sql, self.db)
        while query.next():
            code = str(query.value(0))
            code_name = query.value(1)
            ret[code_name] = code
        return ret