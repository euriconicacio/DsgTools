# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgTools
                                 A QGIS plugin
 Brazilian Army Cartographic Production Tools
                             -------------------
        begin                : 2015-11-24
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Brazilian Army - Geographic Service Bureau
        email                : suporte.dsgtools@dsg.eb.mil.br
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

# Qt imports
from PyQt4 import QtGui, uic, QtCore
from PyQt4.QtCore import pyqtSlot, pyqtSignal
from PyQt4.Qt import QObject

# QGIS imports
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer,QgsDataSourceURI, QgsMessageLog
from qgis.utils import iface

#DsgTools imports
from DsgTools.Factories.LayerFactory.edgv_layer import EDGVLayer

class PostGISLayer(EDGVLayer):
    def __init__(self, abstractDb, codeList, table):
        """Constructor."""
        super(PostGISLayer, self).__init__(abstractDb, codeList)
        
        self.provider = 'postgres'
        
        self.schema, self.layer_name = abstractDb.getTableSchema(table)
        if table[-1] == 'c':
            layer = self.layer_name[:-1]+self.layer_name[-1].replace('c','a')
        else:
            layer = self.layer_name
        
        if table[-1] == 'c':
            sql = abstractDb.gen.loadLayerFromDatabase(table[:-1]+table[-1].replace('c','a'))
        else:
            sql = abstractDb.gen.loadLayerFromDatabase(table)

        self.qmlName = layer.replace('\r','')

        self.host = abstractDb.db.hostName()
        self.port = abstractDb.db.port()
        self.database = abstractDb.db.databaseName()
        self.user = abstractDb.db.userName()
        self.password = abstractDb.db.password()
        
        self.uri.setConnection(str(self.host),str(self.port), str(self.database), str(self.user), str(self.password))
        if self.layer_name[-1] == 'c':
            geomColumn = 'centroid'
        else:
            geomColumn = 'geom'
        self.uri.setDataSource(self.schema, layer, geomColumn, sql, 'id')
        self.uri.disableSelectAtId(True)

    def checkLoaded(self, name):
        '''
        Checks if the layer is already loaded
        '''
        loadedLayers = iface.legendInterface().layers()
        loaded = None
        for ll in loadedLayers:
            if ll.name() == name:
                candidateUri = QgsDataSourceURI(ll.dataProvider().dataSourceUri())
                if self.host == candidateUri.host() and self.database == candidateUri.database() and self.port == int(candidateUri.port()):
                    return ll
        return loaded

    def load(self, crs, idSubgrupo = None, uniqueLoad = False):
        '''
        Loads the layer into the TOC
        crs: EPSG
        idSubgrupo: group id
        uniqueLoad: unique load bool
        '''
        if uniqueLoad:
            lyr = self.checkLoaded(self.layer_name)
            if lyr:
                return lyr
        qmldir = ''
        try:
            qmldir = self.abstractDb.getQmlDir()
        except Exception as e:
            self.problemOccurred.emit(self.tr('A problem occurred! Check log for details.'))
            QgsMessageLog.logMessage(e.args[0], "DSG Tools Plugin", QgsMessageLog.CRITICAL)
            return None

        vlayerQml = os.path.join(qmldir, self.qmlName+'.qml')
        
        host = self.abstractDb.db.hostName()
        port = self.abstractDb.db.port()
        database = self.abstractDb.db.databaseName()
        user = self.abstractDb.db.userName()
        password = self.abstractDb.db.password()

        vlayer = iface.addVectorLayer(self.uri.uri(), self.layer_name, self.provider)
        if not vlayer:
            return None

        vlayer.setCrs(crs)
        if self.schema <> 'views':
            vlayer.loadNamedStyle(vlayerQml, False)
            attrList = vlayer.pendingFields()
            for field in attrList:
                i = vlayer.fieldNameIndex(field.name())
                if vlayer.editorWidgetV2(i) == 'ValueRelation':
                    groupList = iface.legendInterface().groups()
                    groupRelationshipList = iface.legendInterface().groupLayerRelationship()
                    if database not in groupList:
                        idx = iface.legendInterface().addGroup(database, True,-1)
                        domainIdGroup = iface.legendInterface().addGroup(self.tr("Dominios"), True, idx)
                    else:
                        idx = groupList.index(database)
                        if "Dominios" not in groupList[idx::]:
                            domainIdGroup = iface.legendInterface().addGroup(self.tr("Dominios"), True, idx)
                        else:
                            domainIdGroup = groupList[idx::].index("Dominios")
    
                    valueRelationDict = vlayer.editorWidgetV2Config(i)
                    domainTableName = valueRelationDict['Layer']
                    loadedLayers = iface.legendInterface().layers()
                    domainLoaded = False
                    for ll in loadedLayers:
                        if ll.name() == domainTableName:
                            candidateUri = QgsDataSourceURI(ll.dataProvider().dataSourceUri())
                            if host == candidateUri.host() and database == candidateUri.database() and port == int(candidateUri.port()):
                                domainLoaded = True
                                domLayer = ll
                    if not domainLoaded:
                        uri = "dbname='%s' host=%s port=%s user='%s' password='%s' key=code table=\"dominios\".\"%s\" sql=" % (database, host, port, user, password, domainTableName)
                        #TODO Load domain layer into a group
                        domLayer = iface.addVectorLayer(uri, domainTableName, self.provider)
                        iface.legendInterface().moveLayer(domLayer, domainIdGroup)
                    valueRelationDict['Layer'] = domLayer.id()
                    vlayer.setEditorWidgetV2Config(i,valueRelationDict)
    
            self.qmlLoaded.emit()

        iface.legendInterface().moveLayer(vlayer, idSubgrupo)
            
        if not vlayer.isValid():
            QgsMessageLog.logMessage(vlayer.error().summary(), "DSG Tools Plugin", QgsMessageLog.CRITICAL)

        return vlayer
    
    def loadDomainTable(self, name):
        pass
