#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 14:50:14 2021

@author: k
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from os import path, makedirs
import sqlite3, re, shutil


class UpdateTicketWidget(qtw.QWidget):
    def __init__(self, ticketType, ticketSeverity, ticketStatus, conn, cur):
        super().__init__()
        self.setObjectName("New Ticket")
        formLayout = qtw.QFormLayout()
        self.setLayout(formLayout)
        
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
        self.attachedFilesListWidget = qtw.QListWidget()
        self.fileDialogBox = qtw.QFileDialog()
        self.submitButton = qtw.QPushButton("Submit",
                                            clicked = lambda: self.addUpdateTicket())
        self.resetButton = qtw.QPushButton("Reset",
                                            clicked = lambda: self.resetTicket())
        self.testButton = qtw.QPushButton("Test",
                                            clicked = lambda: self.testUpload())
        self.submitButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.resetButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        self.testButton.setSizePolicy(qtw.QSizePolicy(qtw.QSizePolicy.Fixed,
                                                       qtw.QSizePolicy.Fixed))
        
        
        self.outputTextEdit = qtw.QTextEdit(self,
                                            lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                            lineWrapColumnOrWidth = 75,
                                            placeholderText="Output",
                                            readOnly=True)
        
        
        # Add widgets to the form layout
        formLayout.addRow(self.headLabel)
        formLayout.addRow(self.ticketTitle)
        formLayout.addRow(self.ticketDesc)
        formLayout.addRow("Type", self.ticketType)
        formLayout.addRow("Severity", self.ticketSeverity)
        formLayout.addRow("Status", self.ticketStatus)
        formLayout.addRow("Reported Date", self.reportedDate)
        formLayout.addRow("Closed Date", self.closedDate)
        formLayout.addRow(self.attachFilesButton, self.attachedFilesListWidget)
        self.hBoxLayout2 = qtw.QHBoxLayout()
        self.hBoxLayout2.addWidget(self.submitButton)
        self.hBoxLayout2.addWidget(self.resetButton)
        self.hBoxLayout2.addWidget(self.testButton)
        self.hBoxLayout2.setAlignment(qtc.Qt.AlignCenter)
        formLayout.addRow(self.hBoxLayout2)
        formLayout.addRow(self.outputTextEdit)
    
    # Method to add a new ticket to the database    
    def addUpdateTicket(self):
        closedDate = ""
        if self.ticketStatus.currentData() == 'C':
            closedDate = self.closedDate.text()
        
        if self.ticketID == "":
            # Check if the title is empty
            if(re.search("^\s*$", self.ticketTitle.text())): 
                err = "Title is empty or contains only spaces. Please enter a valid Title."
                # print(err)
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
                    print(toPath)
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
                # print("Row added")
                
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
                
                
            # Clear the input values
            self.resetTicket()
    
    # Method to reset the content of the ticket    
    def resetTicket(self):
        # Clear the input values
        self.ticketTitle.clear()
        self.ticketDesc.clear()
        self.reportedDate.setDate(qtc.QDate.currentDate())
        self.closedDate.setDate(qtc.QDate.currentDate())
        self.ticketType.setCurrentIndex(-1)
        self.ticketSeverity.setCurrentIndex(-1)
        self.ticketStatus.setCurrentIndex(-1)
        
        for row in range(self.attachedFilesListWidget.count()):
            self.attachedFilesListWidget.takeItem(row)

    def attachFiles(self):
        self.fileDialogBox.open()
        fileName = self.fileDialogBox.getOpenFileName()
        self.attachedFilesListWidget.addItem(fileName[0])
        # print(fileName[0])
    
    def testUpload(self):
        # for row in range(self.attachedFilesListWidget.count()):
        #    fromPath = self.attachedFilesListWidget.item(row).text()
        #    fromPathSplit = self.attachedFilesListWidget.item(row).text().split("/")
        #    fileName = fromPathSplit[len(fromPathSplit) - 1]
        #    sqlQuery = "select max(ticket_id) from Tickets"
        #    self.cur.execute(sqlQuery)
        #    subFolderName = self.cur.fetchone()[0]
        #    toPath = f"./files/attachments/{subFolderName}"
        #    makedirs(toPath, exist_ok=True)
        #    toPath += f"/{fileName}"
        #    print(toPath)
        #    shutil.copy(fromPath,toPath)
        
        print(self.ticketStatus.currentData())
           
     
class QueryTicketsWidget(qtw.QWidget):
    def __init__(self, ticketType, ticketSeverity, ticketStatus, conn, cur):
        super().__init__()
        
        self.conn = conn
        self.cur = cur
        self.setObjectName("Query Tickets")
        
        formLayout = qtw.QFormLayout()
        vLayout = qtw.QVBoxLayout()
        self.setLayout(vLayout)
        
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
        self.hBoxLayout1.addWidget(self.updateButton)
        self.hBoxLayout1.setAlignment(qtc.Qt.AlignCenter)
        
        self.outputTable = qtw.QTableWidget(self) 
        self.outputTable.setEditTriggers(qtw.QTableWidget.NoEditTriggers)
        # self.outputTable.adjustSize()
        
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
        # vLayout.addWidget(self.updateButton)
        vLayout.addWidget(self.outputTextEdit)
        vLayout.addWidget(self.updateTicketWidget)
        self.outputTextEdit.show()
        self.outputTable.hide()
        self.updateTicketWidget.hide()
        
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
        # print(query)
        queryResult = self.cur.execute(query)
        self.cols = []
        for desc in queryResult.description:
            self.cols.append(desc[0])
        # print(self.cols)
        # print(queryResult.fetchall())
        rows = queryResult.fetchall()
        # print(rows)
        if len(rows) != 0:
            self.outputTextEdit.hide()
            self.outputTable.setRowCount(len(rows))
            self.outputTable.setColumnCount(len(self.cols))
            self.outputTable.setHorizontalHeaderLabels(self.cols)
            for i in range(0,len(rows)):
                for j in range(0,len(self.cols)):
                    self.outputTable.setItem(i, j, qtw.QTableWidgetItem(rows[i][j]))
                    # print(len(qtw.QTableWidgetItem(rows[i][j]).text()))
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
            self.updateTicketWidget.submitButton.setText("Update")
            rowItems = self.outputTable.selectedItems()
            for i in range(len(self.cols)):
                rowItemStr = rowItems[i].text()
                print(rowItemStr)
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
                    
            self.updateTicketWidget.show()
            
            
            
    
    
class MainWindow(qtw.QMainWindow):
    def __init__(self, ticketType, ticketSeverity, ticketStatus, conn, cur):
        super().__init__()
        self.conn = conn
        self.c = cur
        self.setWindowTitle("Ticketing App")
        self.setBaseSize(qtc.QSize(1366,768))
        self.setMinimumSize(qtc.QSize(1366,768))
        
        #Tab Widget is the central widget
        self.tabWidget = qtw.QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        
        # Create Tab 1 - All Tickets
        self.queryTickets = QueryTicketsWidget(ticketType, ticketSeverity, ticketStatus, conn, cur)
        self.tabWidget.addTab(self.queryTickets, "Query Tickets")
        # Create Tab 3 - New Ticket
        self.updateTicket = UpdateTicketWidget(ticketType, ticketSeverity, ticketStatus, conn, cur)
        self.tabWidget.addTab(self.updateTicket, "Create a new Ticket")
        self.setCentralWidget(self.tabWidget)
        
        self.show()
    
    
        
if __name__== "__main__":
    filePath = ("./files/data.db")
    if path.exists(filePath):
        # Start the app
        app = qtw.QApplication([])
        # Open the database and connect to it
        conn = sqlite3.connect(filePath)
        cur = conn.cursor()
        cur.execute("SELECT CODE, DESCRIPTION FROM STATUS")
        ticketStatus = cur.fetchall()
        cur.execute("SELECT CODE, DESCRIPTION FROM TICKET_SEVERITY")
        ticketSeverity = cur.fetchall()
        cur.execute("SELECT CODE, DESCRIPTION FROM TICKET_TYPE")
        ticketType = cur.fetchall()
        mainWindow = MainWindow(ticketType, ticketSeverity, ticketStatus, conn, cur)
        
        # if mainWindow.queryTickets.upateButton.clicked():
        #     mainWindow.tabWidget.setCurrentIndex(1)
        
        app.exec_()
        conn.commit()
        conn.close()
    else:
        # print("False")
        err = "Database file does not exist"
        msg = qtw.QMessageBox()
        msg.setIcon(qtw.QMessageBox.Critical)
        msg.setText(err)
        msg.setWindowTitle("Error !")
        msg.exec_()

    
    
    
# Commit and close the connection
    

#TEST TEST TEST
