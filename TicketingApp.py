#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 14:50:14 2021

@author: k
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import sqlite3
import re

# Open the database and connect to it
conn = sqlite3.connect("D:\Temp\data.db")
c = conn.cursor()

c.execute("SELECT CODE, DESCRIPTION FROM STATUS")
status = c.fetchall()

c.execute("SELECT CODE, DESCRIPTION FROM TICKET_SEVERITY")
ticketSeverity = c.fetchall()

# c.execute("SELECT * FROM TICKET_TYPE")
c.execute("SELECT CODE, DESCRIPTION FROM TICKET_TYPE")
ticketType = c.fetchall()



class NewTicket(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("New Ticket")
        formLayout = qtw.QFormLayout()
        self.setLayout(formLayout)
        
        # Initialize the widgets
        self.headLabel = qtw.QLabel("Enter the details of the new ticket below")
        self.headLabel.setFont(qtg.QFont("Arial", 18))
        self.headLabel.setAlignment(qtc.Qt.AlignCenter)
        
        
        self.ticketTitle = qtw.QLineEdit(self)
        self.ticketTitle.setPlaceholderText("Title")
        self.ticketDesc = qtw.QTextEdit(self,
                                        lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                        lineWrapColumnOrWidth=75,
                                        placeholderText="Description")
        self.reportedDate = qtw.QDateEdit()
        self.reportedDate.setCalendarPopup(True)
        self.closedDate = qtw.QDateEdit()
        self.closedDate.setCalendarPopup(True)
        
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
        for item in status:
            # self.ticketType.addItem(text, data)
            self.ticketStatus.addItem(item[1], item[0])
        self.ticketStatus.setCurrentIndex(-1)
        
        self.submitButton = qtw.QPushButton("Submit",
                                            clicked = lambda: self.addNewTicket())
        self.resetButton = qtw.QPushButton("Reset",
                                            clicked = lambda: self.resetNewTicket())
        
        
        self.outputTextEdit = qtw.QTextEdit(self,
                                            lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                            lineWrapColumnOrWidth = 75,
                                            placeholderText="Output",
                                            readOnly=True)
        
        
        # Add widgets to the form layout
        formLayout.addRow(self.headLabel)
        formLayout.addRow(self.ticketTitle)
        formLayout.addRow(self.ticketDesc)
        formLayout.addRow("Reported Date", self.reportedDate)
        formLayout.addRow("Closed Date", self.closedDate)
        formLayout.addRow("Type", self.ticketType)
        formLayout.addRow("Severity", self.ticketSeverity)
        formLayout.addRow("Status", self.ticketStatus)
        self.hBoxLayout1 = qtw.QHBoxLayout()
        self.hBoxLayout1.addWidget(self.submitButton)
        self.hBoxLayout1.addWidget(self.resetButton)
        formLayout.addRow(self.hBoxLayout1)
        formLayout.addRow(self.outputTextEdit)
    
    
    
    # Method to add a new ticket to the database    
    def addNewTicket(self):
        
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
                    '{self.closedDate.text()}',
                    (SELECT TICKET_TYPE_ID FROM TICKET_TYPE 
                     WHERE CODE = '{self.ticketType.currentData()}'),
                    (SELECT TICKET_SEVERITY_ID FROM TICKET_SEVERITY 
                     WHERE CODE = '{self.ticketSeverity.currentData()}'),
                    (SELECT STATUS_ID FROM STATUS
                     WHERE CODE = '{self.ticketStatus.currentData()}')
                    );"""
            c.execute(sqlQuery)
            conn.commit()
            # print("Row added")
            # self.outputTable.setItem(0,0,qtw.QTableWidgetItem(self.ticketTitle.text()))
            # self.outputTable.setItem(0,1,qtw.QTableWidgetItem(self.ticketDesc.toPlainText()))
            # self.outputTable.resizeColumnsToContents()
            # self.outputTable.resizeRowsToContents()
            # self.outputTable.setWordWrap(True)
            
            output = "A new ticket has been created with the following details:"
            output += "\n---------------------------------------------------------"
            output += f"\nTITLE: {self.ticketTitle.text()}"
            output += f"\nDESCRIPTION: {self.ticketDesc.toPlainText()}"
            output += f"\nREPORTED DATE: {self.reportedDate.text()}"
            output += f"\nCLOSED DATE: {self.closedDate.text()}"
            output += f"\nTYPE: {self.ticketType.currentText()}"
            output += f"\nSEVERITY: {self.ticketSeverity.currentText()}"
            output += f"\nSTATUS: {self.ticketStatus.currentText()}"
            
            self.outputTextEdit.setText(output)       
            
            # Clear the input values
            self.resetNewTicket()
    
    # Method to reset the content of the ticket    
    def resetNewTicket(self):
        # Clear the input values
        self.ticketTitle.clear()
        self.ticketDesc.clear()
        self.reportedDate.clear()
        self.closedDate.clear()
        self.ticketType.setCurrentIndex(-1)
        self.ticketSeverity.setCurrentIndex(-1)
        self.ticketStatus.setCurrentIndex(-1)

class QueryTickets(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Query Tickets")
        
        formLayout = qtw.QFormLayout()
        vLayout = qtw.QVBoxLayout()
        self.setLayout(vLayout)
        
        self.query = ""
        
        # Initialize the widgets
        self.headLabel = qtw.QLabel("Select the below fields to query old tickets")
        self.headLabel.setFont(qtg.QFont("Arial", 18))
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
        for item in status:
            # self.ticketType.addItem(text, data)
            self.ticketStatus.addItem(item[1], item[0])
        self.ticketStatus.setCurrentIndex(-1)
        
        self.queryButton = qtw.QPushButton("Query",
                                            clicked = lambda: self.queryTickets())
        self.resetButton = qtw.QPushButton("Reset",
                                            clicked = lambda: self.resetQuery())
       
        
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
        
        self.outputTable = qtw.QTableWidget(self) 
        self.outputTable.setRowCount(0)
        self.outputTable.setColumnCount(0)
        self.outputTable.setHorizontalHeaderLabels(['Title', 
                                                    'Desc', 
                                                    'Reported Date', 
                                                    'Closed Date'])
        self.outputTable.setEditTriggers(qtw.QTableWidget.NoEditTriggers)
        
        formLayout.addRow(self.headLabel)
        formLayout.addRow(self.gridLayout1)
        formLayout.addRow(self.hBoxLayout1)
        # formLayout.addRow(self.outputTable)
        vLayout.addLayout(formLayout)
        vLayout.addWidget(self.outputTable)
        
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
        queryResult = c.execute(query)
        cols = []
        for desc in queryResult.description:
            cols.append(desc[0])
        # print(cols)
        # print(queryResult.fetchall())
        rows = queryResult.fetchall()
        
        if len(rows) != 0:
            self.outputTable.setRowCount(len(rows))
            self.outputTable.setColumnCount(len(cols))
            self.outputTable.setHorizontalHeaderLabels(cols)
            for i in range(0,len(rows)):
                for j in range(0,len(cols)):
                    self.outputTable.setItem(i, j, qtw.QTableWidgetItem(rows[i][j]))
            self.outputTable.setWordWrap(True)
            self.outputTable.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)

    
    def resetQuery(self):
        self.ticketType.setCurrentIndex(-1)
        self.ticketSeverity.setCurrentIndex(-1)
        self.ticketStatus.setCurrentIndex(-1)
        
        

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ticketing App")
        self.setBaseSize(qtc.QSize(1000,500))
        self.setMinimumSize(qtc.QSize(1000,500))
        #Tab Widget is the central widget
        self.tabWidget = qtw.QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.setCentralWidget(self.tabWidget)
        
        # Create Tab 1 - All Tickets
        self.queryTickets = QueryTickets()
        self.tabWidget.addTab(self.queryTickets, "Query Tickets")
        # Create Tab 2 - New Ticket
        self.newTicket = NewTicket()
        self.tabWidget.addTab(self.newTicket, "New Ticket")
        
        
        self.show()
        
if __name__== "__main__":
    # Start the app
    app = qtw.QApplication([])
    mainWindow = MainWindow()
    app.exec_()
    
# Commit and close the connection
    
conn.commit()
conn.close()
#TEST TEST TEST
