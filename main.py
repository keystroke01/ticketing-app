#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 14:50:14 2021

@author: k
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from os import path, makedirs, getcwd
from pandas import DataFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import sqlite3, re, shutil, sys


class UpdateTicketWidget(qtw.QWidget):
    def __init__(self, ticketType, ticketSeverity, ticketStatus, conn, cur):
        super().__init__()
        self.setObjectName("New Ticket")
        
        self.formLayout = qtw.QFormLayout()
        self.formLayoutWidget = qtw.QWidget()
        self.formLayoutWidget.setLayout(self.formLayout)
        
        self.conn = conn
        self.cur = cur
        
        # Initialize the widgets
        self.headLabel = qtw.QLabel("Enter the details of the ticket below")
        self.headLabel.setFont(qtg.QFont("Arial", 14))
        self.headLabel.setAlignment(qtc.Qt.AlignCenter)
        
        self.ticketID = ""
        self.ticketTitle = qtw.QLineEdit(self)
        self.ticketTitle.setPlaceholderText("Title")
        self.ticketDesc = qtw.QTextEdit(self,
                                        lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                        lineWrapColumnOrWidth=75,
                                        placeholderText="Description")
        self.reportedDate = qtw.QDateEdit()
        self.reportedDate.setCalendarPopup(True)
        self.reportedDate.setDate(qtc.QDate.currentDate())
        self.reportedDate.setDisplayFormat('dd/MMM/yyyy')
        self.closedDate = qtw.QDateEdit()
        self.closedDate.setCalendarPopup(True)
        self.closedDate.setDate(qtc.QDate.currentDate())
        self.closedDate.setDisplayFormat('dd/MMM/yyyy')
        
        # self.ticketStatus.changeEvent(qtc.QEvent.ActionChanged)
        
        # Adding items of TICKET_TYPE
        self.ticketType = qtw.QComboBox()
        
        for item in ticketType:
            # self.ticketType.addItem(text, data)
            self.ticketType.addItem(item[1], item[0])
        self.ticketType.setCurrentIndex(-1)
        
        # Adding items of TICKET_SEVERITY
        self.ticketSeverity = qtw.QComboBox()
        for item in ticketSeverity:
            # self.ticketType.addItem(text, data)
            self.ticketSeverity.addItem(item[1], item[0])
        self.ticketSeverity.setCurrentIndex(-1)
        
        # Adding items of STATUS
        self.ticketStatus = qtw.QComboBox()
        for item in ticketStatus:
            # self.ticketType.addItem(text, data)
            self.ticketStatus.addItem(item[1], item[0])
        self.ticketStatus.setCurrentIndex(-1)
        
        # if self.ticketStatus.currentData() == 
        
        self.attachFilesButton = qtw.QPushButton("Attach Files",
                                                 clicked = lambda: self.attachFiles())
        self.detachFilesButton = qtw.QPushButton("Remove Files",
                                                 clicked = lambda: self.detachFiles())
        self.attachedFilesListWidget = qtw.QListWidget()
        self.fileDialogBox = qtw.QFileDialog()
        self.submitButton = qtw.QPushButton("Submit",
                                            clicked = lambda: self.addTicket())
        self.resetButton = qtw.QPushButton("Reset",
                                            clicked = lambda: self.resetTicket())
        self.updateButton = qtw.QPushButton("Update",
                                            clicked = lambda: self.updateTicket())
        self.submitButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.resetButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.updateButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.submitButton.show()
        self.updateButton.hide()
        
        self.outputTextEdit = qtw.QTextEdit(self,
                                            lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                            lineWrapColumnOrWidth = 75,
                                            placeholderText="Output",
                                            readOnly=True)
        
        
        # Add widgets to the form layout
        self.formLayout.addRow(self.headLabel)
        self.formLayout.addRow(self.ticketTitle)
        self.formLayout.addRow(self.ticketDesc)
        self.formLayout.addRow("Type", self.ticketType)
        self.formLayout.addRow("Severity", self.ticketSeverity)
        self.formLayout.addRow("Status", self.ticketStatus)
        self.formLayout.addRow("Reported Date", self.reportedDate)
        self.formLayout.addRow("Closed Date", self.closedDate)
        
        self.vFilesButtonWidget = qtw.QWidget()
        self.vFileButtonsLayout = qtw.QVBoxLayout()
        self.vFileButtonsLayout.addWidget(self.attachFilesButton)
        self.vFileButtonsLayout.addWidget(self.detachFilesButton)
        self.vFilesButtonWidget.setLayout(self.vFileButtonsLayout)

        self.formLayout.addRow(self.vFilesButtonWidget, self.attachedFilesListWidget)
        self.hBoxLayout2 = qtw.QHBoxLayout()
        self.hBoxLayout2.addWidget(self.submitButton)
        self.hBoxLayout2.addWidget(self.updateButton)
        self.hBoxLayout2.addWidget(self.resetButton)
        self.hBoxLayout2.setAlignment(qtc.Qt.AlignCenter)
        self.formLayout.addRow(self.hBoxLayout2)
        # formLayout.addRow(self.outputTextEdit)
        self.vLayout = qtw.QVBoxLayout()
        self.vLayout.addWidget(self.formLayoutWidget)
        self.vLayout.addWidget(self.outputTextEdit)
        self.setLayout(self.vLayout)
    
    # Method to add a new ticket to the database    
    def addTicket(self):
        closedDate = ""
        if self.ticketStatus.currentData() == 'C':
            closedDate = self.closedDate.text()
        
        # Check if the title is empty
        if(re.search("^\s*$", self.ticketTitle.text())): 
            err = "Title is empty or contains only spaces. Please enter a valid Title."
            # # print(err)
            msg = qtw.QMessageBox()
            msg.setIcon(qtw.QMessageBox.Critical)
            msg.setText(err)
            msg.setWindowTitle("Error")
            msg.exec_()
        else: 
            # Add a new ticket
            sqlQuery = f"""
            INSERT 
            INTO 
            TICKETS (TITLE, 
                        DESCRIPTION, 
                        REPORTED_DATE, 
                        CLOSED_DATE, 
                        TICKET_TYPE_ID, 
                        TICKET_SEVERITY_ID, 
                        STATUS_ID) 
            VALUES ('{self.ticketTitle.text()}', 
                    '{self.ticketDesc.toPlainText()}',
                    '{self.reportedDate.text()}',
                    '{closedDate}',
                    (SELECT TICKET_TYPE_ID FROM TICKET_TYPE 
                        WHERE CODE = '{self.ticketType.currentData()}'),
                    (SELECT TICKET_SEVERITY_ID FROM TICKET_SEVERITY 
                        WHERE CODE = '{self.ticketSeverity.currentData()}'),
                    (SELECT STATUS_ID FROM STATUS
                        WHERE CODE = '{self.ticketStatus.currentData()}')
                    );"""
            self.cur.execute(sqlQuery)
            
            sqlQuery = "select max(ticket_id) from Tickets"
            self.cur.execute(sqlQuery)
            subFolderName = self.cur.fetchone()[0]
            
            for row in range(self.attachedFilesListWidget.count()):
                fromPath = self.attachedFilesListWidget.item(row).text()
                fromPathSplit = self.attachedFilesListWidget.item(row).text().split("/")
                fileName = fromPathSplit[len(fromPathSplit) - 1]
                toPath = f"./files/attachments/{subFolderName}"
                makedirs(toPath, exist_ok=True)
                toPath += f"/{fileName}"
                # print(toPath)
                shutil.copy(fromPath,toPath)
                sqlQuery = f"""
                INSERT 
                INTO 
                TICKET_ATTACHMENTS(ATTACHMENT_PATH,TICKET_ID)
                VALUES('{toPath}',
                        (SELECT MAX(TICKET_ID) FROM TICKETS)
                    );
                """ 
                self.cur.execute(sqlQuery)
            self.conn.commit()
            # # print("Row added")
            
            output = "A new ticket has been created with the following details:"
            output += "\n---------------------------------------------------------"
            output += f"\nTITLE: {self.ticketTitle.text()}"
            output += f"\nDESCRIPTION: {self.ticketDesc.toPlainText()}"
            output += f"\nREPORTED DATE: {self.reportedDate.text()}"
            output += f"\nCLOSED DATE: {closedDate}"
            output += f"\nTYPE: {self.ticketType.currentText()}"
            output += f"\nSEVERITY: {self.ticketSeverity.currentText()}"
            output += f"\nSTATUS: {self.ticketStatus.currentText()}"
            
            
            self.outputTextEdit.setText(output)  
            self.resetTicket()     
        

    def updateTicket(self):
        closedDate = ""
        if self.ticketStatus.currentData() == 'C':
            closedDate = self.closedDate.text()
        
        if(re.search("^\s*$", self.ticketTitle.text())): 
                err = "Title is empty or contains only spaces. Please enter a valid Title."
                # # print(err)
                msg = qtw.QMessageBox()
                msg.setIcon(qtw.QMessageBox.Critical)
                msg.setText(err)
                msg.setWindowTitle("Error")
                msg.exec_()
        else:
            # Update the selected Record
            sqlQuery = f"""
            UPDATE 
                TICKETS 
            SET
                TITLE = '{self.ticketTitle.text()}',
                DESCRIPTION = '{self.ticketDesc.toPlainText()}',
                TICKET_TYPE_ID = (SELECT TICKET_TYPE_ID FROM TICKET_TYPE
                                  WHERE 
                                  CODE = '{self.ticketType.currentData()}'),   
                TICKET_SEVERITY_ID = (SELECT TICKET_SEVERITY_ID FROM TICKET_SEVERITY 
                                      WHERE 
                                      CODE = '{self.ticketSeverity.currentData()}'),
                STATUS_ID = (SELECT STATUS_ID FROM STATUS
                             WHERE 
                             CODE = '{self.ticketStatus.currentData()}'),
                REPORTED_DATE = '{self.reportedDate.text()}',
                CLOSED_DATE = '{closedDate}'
            
            WHERE 
                TICKET_ID = {self.ticketID};
            """
            
            self.cur.execute(sqlQuery)
            self.conn.commit()

            # Update the attachments
            for row in range(self.attachedFilesListWidget.count()):
                fromPath = self.attachedFilesListWidget.item(row).text()
                if ("./files/attachments/" in fromPath) == False:
                    fromPathSplit = self.attachedFilesListWidget.item(row).text().split("/")
                    fileName = fromPathSplit[len(fromPathSplit) - 1]
                    toPath = f"./files/attachments/{self.ticketID}"
                    makedirs(toPath, exist_ok=True)
                    toPath += f"/{fileName}"
                    # print(toPath)
                    shutil.copy(fromPath,toPath)
                    sqlQuery = f"""
                    INSERT 
                    INTO 
                    TICKET_ATTACHMENTS(ATTACHMENT_PATH,TICKET_ID)
                    VALUES('{toPath}',
                            {self.ticketID}
                        );
                    """ 
                    # print(sqlQuery)
                self.cur.execute(sqlQuery)
            self.conn.commit()

            output = "The ticket has been updated with the following details:"
            output += "\n---------------------------------------------------------"
            output += f"\nTITLE: {self.ticketTitle.text()}"
            output += f"\nDESCRIPTION: {self.ticketDesc.toPlainText()}"
            output += f"\nREPORTED DATE: {self.reportedDate.text()}"
            output += f"\nCLOSED DATE: {closedDate}"
            output += f"\nTYPE: {self.ticketType.currentText()}"
            output += f"\nSEVERITY: {self.ticketSeverity.currentText()}"
            output += f"\nSTATUS: {self.ticketStatus.currentText()}"
            
            self.outputTextEdit.setText(output)       
            
            # Clear the input values
            self.resetTicket()
            self.formLayoutWidget.hide()

    # Method to reset the content of the ticket    
    
    def resetTicket(self):
        # Clear the input values
        self.ticketID = ""
        self.ticketTitle.clear()
        self.ticketDesc.clear()
        self.reportedDate.setDate(qtc.QDate.currentDate())
        self.closedDate.setDate(qtc.QDate.currentDate())
        self.ticketType.setCurrentIndex(-1)
        self.ticketSeverity.setCurrentIndex(-1)
        self.ticketStatus.setCurrentIndex(-1)
        self.attachedFilesListWidget.clear()

    def attachFiles(self):
        self.fileDialogBox.open()
        filePath = self.fileDialogBox.getOpenFileName()
        filePathSplit = filePath[0].split("/")
        fileName = filePathSplit[len(filePathSplit) - 1]
        # print(fileName, filePathSplit)

        if self.attachedFilesListWidget.count() == 0:
            self.attachedFilesListWidget.addItem(filePath[0])
            
        elif self.attachedFilesListWidget.count() > 0:
            nameMatchFoundItems = self.attachedFilesListWidget.findItems(
                "/"+fileName, qtc.Qt.MatchContains)
            # print(nameMatchFoundItems)
            if len(nameMatchFoundItems) == 0:
                self.attachedFilesListWidget.addItem(filePath[0])
            
                

    def detachFiles(self):
        if(len(self.attachedFilesListWidget.selectedItems()) > 0):
            if ("/files/attachments/" in self.attachedFilesListWidget.selectedItems()[0].text()) == False:
                i = self.attachedFilesListWidget.selectedIndexes()[0].row()
                self.attachedFilesListWidget.takeItem(i)
           
     
class QueryTicketsWidget(qtw.QWidget):
    def __init__(self, ticketType, ticketSeverity, ticketStatus, conn, cur):
        super().__init__()
        
        self.conn = conn
        self.cur = cur
        self.setObjectName("Query Tickets")
        
        formLayout = qtw.QFormLayout()
        vLayout = qtw.QVBoxLayout()
        # self.setLayout(vLayout)
        
        self.query = ""
        
        # Initialize the widgets
        self.headLabel = qtw.QLabel("Select the below fields to query the tickets")
        self.headLabel.setFont(qtg.QFont("Arial", 14))
        self.headLabel.setAlignment(qtc.Qt.AlignCenter)
        
        # Adding items of TICKET_TYPE
        self.ticketType = qtw.QComboBox()
        for item in ticketType:
            # self.ticketType.addItem(text, data)
            self.ticketType.addItem(item[1], item[0])
        self.ticketType.setCurrentIndex(-1)
        
        # Adding items of TICKET_SEVERITY
        self.ticketSeverity = qtw.QComboBox()
        for item in ticketSeverity:
            # self.ticketType.addItem(text, data)
            self.ticketSeverity.addItem(item[1], item[0])
        self.ticketSeverity.setCurrentIndex(-1)
        
        # Adding items of STATUS
        self.ticketStatus = qtw.QComboBox()
        for item in ticketStatus:
            # self.ticketType.addItem(text, data)
            self.ticketStatus.addItem(item[1], item[0])
        self.ticketStatus.setCurrentIndex(-1)
        
        self.queryButton = qtw.QPushButton("Query",
                                            clicked = lambda: self.queryTickets())
        self.resetButton = qtw.QPushButton("Reset",
                                            clicked = lambda: self.resetQuery())
        self.updateButton = qtw.QPushButton("Update Selected Ticket",
                                            clicked = lambda: self.updateSelectedTicket())
        self.queryButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.resetButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.updateButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.updateTicketWidget = UpdateTicketWidget(ticketType,
                                                     ticketSeverity,
                                                     ticketStatus,
                                                     conn,
                                                     cur)
        
        self.gridLayout1 = qtw.QGridLayout()
        
        self.gridLayout1.setColumnCount = 3
        self.gridLayout1.setRowCount = 2
        # Add Grid Headers
        self.typeLabel = qtw.QLabel("Type")
        self.typeLabel.setAlignment(qtc.Qt.AlignCenter)
        self.gridLayout1.addWidget(self.typeLabel, 0, 0)
        self.severityLabel = qtw.QLabel("Severity")
        self.severityLabel.setAlignment(qtc.Qt.AlignCenter)
        self.gridLayout1.addWidget(self.severityLabel, 0, 1)
        self.statusLabel = qtw.QLabel("Status")
        self.statusLabel.setAlignment(qtc.Qt.AlignCenter)
        self.gridLayout1.addWidget(self.statusLabel, 0, 2)
        # Add Filters
        self.gridLayout1.addWidget(self.ticketType, 1, 0)
        self.gridLayout1.addWidget(self.ticketSeverity, 1, 1)
        self.gridLayout1.addWidget(self.ticketStatus, 1, 2)
        self.gridLayout1.setAlignment(qtc.Qt.AlignCenter)
        
        self.hBoxLayout1 = qtw.QHBoxLayout()
        self.hBoxLayout1.addWidget(self.queryButton)
        self.hBoxLayout1.addWidget(self.resetButton)
        # self.hBoxLayout1.addWidget(self.updateButton)
        self.hBoxLayout1.setAlignment(qtc.Qt.AlignCenter)
        
        self.outputTable = qtw.QTableWidget(self) 
        self.outputTable.setEditTriggers(qtw.QTableWidget.NoEditTriggers)
        
        self.outputTextEdit = qtw.QTextEdit(self,
                                            lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                            lineWrapColumnOrWidth = 75,
                                            placeholderText="Output",
                                            readOnly=True)
        
        formLayout.addRow(self.headLabel)
        formLayout.addRow(self.gridLayout1)
        formLayout.addRow(self.hBoxLayout1)
        vLayout.addLayout(formLayout)
        vLayout.addWidget(self.outputTable)
        vLayout.addWidget(self.outputTextEdit)
        vLayout.addWidget(self.updateButton)
        
        self.outputTextEdit.show()
        self.outputTable.hide()
        
        self.toolBox = qtw.QToolBox()
        self.mainQueryWidget = qtw.QWidget()
        self.mainQueryWidget.setLayout(vLayout)

        self.toolBox.addItem(self.mainQueryWidget, "Query Ticket")
        self.toolBox.addItem(self.updateTicketWidget, "Update Ticket")
        
        self.vLayout1 = qtw.QVBoxLayout()
        self.setLayout(self.vLayout1)
        self.vLayout1.addWidget(self.toolBox)
        
        self.cols = []
        
    def queryTickets(self):
        query = "SELECT * FROM V_TICKETS"
        
        queryFilter = " WHERE "
        
        if self.ticketType.currentIndex() != -1:
            queryFilter += f" TYPE = '{self.ticketType.currentText()}'"
            
        if self.ticketSeverity.currentIndex() != -1:
            if queryFilter == " WHERE ":
                queryFilter += f" SEVERITY = '{self.ticketSeverity.currentText()}'"
            else:
                queryFilter += f" AND SEVERITY = '{self.ticketSeverity.currentText()}'"
        if self.ticketStatus.currentIndex() != -1:
            if queryFilter == " WHERE ":
                queryFilter += f" STATUS = '{self.ticketStatus.currentText()}'"
            else:
                queryFilter += f" AND STATUS = '{self.ticketStatus.currentText()}'"        
        
        if queryFilter != " WHERE ":
            query += queryFilter
        # # print(query)
        queryResult = self.cur.execute(query)
        self.cols = []
        for desc in queryResult.description:
            self.cols.append(desc[0])
        # # print(self.cols)
        # # print(queryResult.fetchall())
        rows = queryResult.fetchall()
        # # print(rows)
        if len(rows) != 0:
            self.outputTextEdit.hide()
            self.outputTable.setRowCount(len(rows))
            self.outputTable.setColumnCount(len(self.cols))
            self.outputTable.setHorizontalHeaderLabels(self.cols)
            for i in range(0,len(rows)):
                for j in range(0,len(self.cols)):
                    self.outputTable.setItem(i, j, qtw.QTableWidgetItem(rows[i][j]))
                    # # print(len(qtw.QTableWidgetItem(rows[i][j]).text()))
            self.outputTable.setWordWrap(True)
            self.outputTable.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
            self.outputTable.setSelectionBehavior(qtw.QTableView.SelectRows)
            self.outputTable.show()
            self.updateTicketWidget.hide()
        else:
            self.outputTable.hide()
            self.updateTicketWidget.hide()
            self.outputTextEdit.setPlaceholderText("No records found")
            self.outputTextEdit.show()
     
    def resetQuery(self):
        self.ticketType.setCurrentIndex(-1)
        self.ticketSeverity.setCurrentIndex(-1)
        self.ticketStatus.setCurrentIndex(-1)
        self.outputTable.hide()
        self.updateTicketWidget.hide()
        self.outputTextEdit.setPlaceholderText("")
        self.outputTextEdit.show()

    def updateSelectedTicket(self):
        if len(self.outputTable.selectedItems()) > 0:
            self.updateTicketWidget.resetTicket()
            rowItems = self.outputTable.selectedItems()
            for i in range(len(self.cols)):
                rowItemStr = rowItems[i].text()
                # print(rowItemStr)
                if i == 0:
                    self.updateTicketWidget.ticketID = rowItemStr
                elif i == 1: # TITLE 
                    self.updateTicketWidget.ticketTitle.setText(rowItemStr) 
                elif i == 2: # DESCRIPTION
                    self.updateTicketWidget.ticketDesc.setText(rowItemStr)
                elif i == 3: # Ticket Type
                    for ticketTypeIndex in range(len(ticketType)):
                        if ticketType[ticketTypeIndex][1] == rowItemStr:
                            self.updateTicketWidget.ticketType.setCurrentIndex(ticketTypeIndex)  
                elif i == 4: # Ticket Severity
                    for ticketSeverityIndex in range(len(ticketSeverity)):
                        if ticketSeverity[ticketSeverityIndex][1] == rowItemStr:
                            self.updateTicketWidget.ticketSeverity.setCurrentIndex(ticketSeverityIndex)
                elif i == 5: # Ticket Status
                    for ticketStatusIndex in range(len(ticketStatus)):
                        if ticketStatus[ticketStatusIndex][1] == rowItemStr:
                            self.updateTicketWidget.ticketStatus.setCurrentIndex(ticketStatusIndex)  
                elif i == 6: # Reported Date
                    self.updateTicketWidget.reportedDate.setDate(qtc.QDate.fromString(rowItemStr, 'dd/MMM/yyyy'))
                elif i == 7: # Closed Date
                    self.updateTicketWidget.closedDate.setDate(qtc.QDate.fromString(rowItemStr, 'dd/MMM/yyyy'))
            
            # Attach the related files
            queryResult = self.cur.execute(f"""
            SELECT * FROM TICKET_ATTACHMENTS WHERE TICKET_ID = {self.updateTicketWidget.ticketID}""")
            queryCols = []
            for row in queryResult:
                # print(row[1])
                self.updateTicketWidget.attachedFilesListWidget.addItem(row[1])
            # # print(queryCols)

            self.updateTicketWidget.outputTextEdit.clear()
            self.updateTicketWidget.formLayoutWidget.show()
            self.updateTicketWidget.submitButton.hide()
            self.updateTicketWidget.updateButton.show()        
            self.updateTicketWidget.show()
            self.toolBox.setCurrentIndex(1)

class AnalyzeTicketsWidget(qtw.QWidget):
    def __init__(self, conn, cur):
        super().__init__()
        self.conn = conn
        self.cur = cur
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.refreshButton = qtw.QPushButton("Refresh",
                                             clicked = lambda: self.plotData())
        vLayout = qtw.QVBoxLayout()
        
        vLayout.addWidget(self.canvas)
        vLayout.addWidget(self.refreshButton)
        
        self.setLayout(vLayout)
    
    def plotData(self):
        self.figure.clear()
       
        sqlQuery = "SELECT * FROM V_TICKETS"
        queryResult = self.cur.execute(sqlQuery)
        cols = []
        for desc in queryResult.description:
            cols.append(desc[0])
        df = DataFrame(data=queryResult,columns=cols)
        df = df.replace(np.nan, "NA")
        # print(df.replace(np.nan, "NA"))
        dfGBType = df.groupby("TYPE")["ID"].count().reset_index()
        dfGBSeverity = df.groupby("SEVERITY")["ID"].count().reset_index()

        def addlabels(x,y):
            for i in range(len(x)):
                plt.text(i, y[i], y[i], ha = 'center')
        
        axes = self.figure.add_subplot(221)
        axes.bar(dfGBType['TYPE'], dfGBType['ID'])
        addlabels(dfGBType['TYPE'], dfGBType['ID'])
        plt.xlabel("Ticket Type")
        plt.ylabel("No of Tickets")
        plt.title("No of Tickets per Type")

        axes2 = self.figure.add_subplot(222)
        axes2.bar(dfGBSeverity['SEVERITY'], dfGBSeverity['ID'])
        addlabels(dfGBSeverity['SEVERITY'], dfGBSeverity['ID'])
        plt.xlabel("Severity")
        plt.ylabel("No of Tickets")
        plt.title("No of Tickets per Severity")
        
        axes3 = self.figure.add_subplot(223)
        axes3.pie(
            dfGBType['ID'], 
            labels = dfGBType['TYPE'],
            autopct='%1.2f%%')

        axes4 = self.figure.add_subplot(224)
        axes4.pie(
            dfGBSeverity['ID'], 
            labels = dfGBSeverity['SEVERITY'],
            autopct='%1.2f%%'
            )

        self.canvas.draw()

        # print(dfGBType)
        # print(dfGBSeverity)
        
        
class MainWindow(qtw.QMainWindow):
    def __init__(self, ticketType, ticketSeverity, ticketStatus, conn, cur):
        super().__init__()
        self.conn = conn
        self.c = cur
        self.setWindowTitle("Ticketing App")
        self.setBaseSize(qtc.QSize(1366,768))
        self.setMinimumSize(qtc.QSize(1366,768))
        
        self.menuBar = qtw.QMenuBar()
        self.setMenuBar(self.menuBar)
        
        self.menuFile = qtw.QMenu()
        self.menuFile.setTitle("File")
        self.mfNewTicketAction = qtw.QAction()
        self.mfNewTicketAction.setText("New Ticket")
        self.mfQueryTicketAction = qtw.QAction()
        self.mfQueryTicketAction.setText("Query Ticket")
        self.mfAnalyzeAction = qtw.QAction()
        self.mfAnalyzeAction.setText("Analyze")
        self.mfExitAction = qtw.QAction()
        self.mfExitAction.setText("Exit")
        self.menuFile.addActions([
            self.mfNewTicketAction,
            self.mfQueryTicketAction,
            self.mfAnalyzeAction, 
            self.mfExitAction])

        self.menuHelp = qtw.QMenu()
        self.menuHelp.setTitle("Help")
        self.mhAboutAction = qtw.QAction()
        self.mhAboutAction.setText("About")
        self.menuHelp.addActions([self.mhAboutAction])

        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuHelp)

        self.menuFile.triggered[qtw.QAction].connect(self.processTrigger)
        self.menuHelp.triggered[qtw.QAction].connect(self.processTrigger)
        
        self.centralWidget = qtw.QWidget()
        
        self.queryTickets = QueryTicketsWidget(ticketType, ticketSeverity, ticketStatus, conn, cur)
        self.updateTicket = UpdateTicketWidget(ticketType, ticketSeverity, ticketStatus, conn, cur)
        self.analyzeTickets = AnalyzeTicketsWidget(conn, cur)

        self.queryTickets.hide()
        self.updateTicket.show()
        self.analyzeTickets.hide()

        self.vBoxLayout = qtw.QVBoxLayout()
        self.vBoxLayout.addWidget(self.queryTickets)
        self.vBoxLayout.addWidget(self.updateTicket)
        self.vBoxLayout.addWidget(self.analyzeTickets)
        self.centralWidget.setLayout(self.vBoxLayout)
        self.setCentralWidget(self.centralWidget)

        self.show()
    
    def processTrigger(self, q):
        # # print(q.text())
        if q.text() == "New Ticket":
            self.queryTickets.hide()
            self.updateTicket.show()
            self.analyzeTickets.hide()
        elif q.text() == "Query Ticket":
            self.queryTickets.show()
            self.updateTicket.hide()
            self.analyzeTickets.hide()
        elif q.text() == "Analyze":
            self.queryTickets.hide()
            self.updateTicket.hide()
            self.analyzeTickets.plotData()
            self.analyzeTickets.show()
        elif q.text() == "Exit":
            self.conn.commit()
            self.conn.close()
            sys.exit()
        else: # About
            msg = qtw.QMessageBox()
            msg.setIcon(qtw.QMessageBox.Information)
            aboutText = """Ticketing App\nCreated using PyQt5\nAuthor: SK"""
            msg.setText(aboutText)
            msg.setWindowTitle("About")
            msg.exec_()
      
if __name__== "__main__":
    dbPath = getcwd() + "/files/data.db"
    # print(getcwd())
    if path.exists(dbPath):
        # Start the app
        app = qtw.QApplication(sys.argv) 
        # Open the database and connect to it
        conn = sqlite3.connect(dbPath)
        cur = conn.cursor()
        cur.execute("SELECT CODE, DESCRIPTION FROM STATUS")
        ticketStatus = cur.fetchall()
        cur.execute("SELECT CODE, DESCRIPTION FROM TICKET_SEVERITY")
        ticketSeverity = cur.fetchall()
        cur.execute("SELECT CODE, DESCRIPTION FROM TICKET_TYPE")
        ticketType = cur.fetchall()
        mainWindow = MainWindow(ticketType, ticketSeverity, ticketStatus, conn, cur)
        
        icon = qtg.QIcon()
        icon.addFile("./resources/icon.png")
        app.setWindowIcon(icon)
        app.exec_()
        conn.commit()
        conn.close()
    else:
        # # print("False")
        app = qtw.QApplication(sys.argv)
        # mainWindow = qtw.QMainWindow()  
        err = "Database file does not exist\nPlease check ./files/ for data.db"
        msg = qtw.QMessageBox()
        msg.setIcon(qtw.QMessageBox.Critical)
        msg.setText(err)
        msg.setWindowTitle("Error !")
        sys.exit(msg.exec_())
        app.exec_()
        # sys.exit()

