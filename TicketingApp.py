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

# Open the database and connect to it
conn = sqlite3.connect("D:\Temp\data.db")
c = conn.cursor()

class NewTicket(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("New Ticket")
        formLayout = qtw.QFormLayout()
        self.setLayout(formLayout)
        
        self.headLabel = qtw.QLabel("Enter the details of the new ticket below")
        self.headLabel.setFont(qtg.QFont("Arial", 18))
        formLayout.addRow(self.headLabel)
        
        self.ticketTitle = qtw.QLineEdit(self)
        self.ticketDesc = qtw.QTextEdit(self,
                                        lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                        lineWrapColumnOrWidth=75,
                                        placeholderText="Enter the description of the ticket")
        self.reportedDate = qtw.QDateTimeEdit()
        self.closedDate = qtw.QDateTimeEdit()
        self.ticketType = qtw.QComboBox()
        self.ticketType.addItems(['Bug', 'User Assistance'])
        self.ticketSeverity = qtw.QComboBox()
        self.ticketSeverity.addItems(['Minor', 'Major'])
        self.ticketStatus = qtw.QComboBox()
        self.ticketStatus.addItems(['Open', 'In Progress', 'Closed'])
        self.submitButton = qtw.QPushButton("Submit",
                                            clicked = lambda: self.addNewTicket())
        
        
        self.outputTable = qtw.QTableWidget(self) 
        self.outputTable.setRowCount(1)
        self.outputTable.setColumnCount(2)
        self.outputTable.setHorizontalHeaderLabels(['Title', 'Desc'])
        self.outputTable.setEditTriggers(qtw.QTableWidget.NoEditTriggers)
        
        
    
        formLayout.addRow("Title", self.ticketTitle)
        formLayout.addRow("Description", self.ticketDesc)
        formLayout.addRow("Reported Date", self.reportedDate)
        formLayout.addRow("Closed Date", self.closedDate)
        formLayout.addRow("Type", self.ticketType)
        formLayout.addRow("Severity", self.ticketSeverity)
        formLayout.addRow("Status", self.ticketStatus)
        formLayout.addRow(self.submitButton)
        formLayout.addRow(self.outputTable)
        # self.show()
    
    # Method to add a new ticket to the database    
    def addNewTicket(self):
        # sqlQuery = "INSERT INTO TICKETS (TITLE, DESCRIPTION) VALUES ("
        # sqlQuery += f"'{self.ticketTitle.text()}', '{self.ticketDesc.toPlainText()}')"
        # c.execute(sqlQuery)
        print("Row added")
        self.outputTable.setItem(0,0,qtw.QTableWidgetItem(self.ticketTitle.text()))
        self.outputTable.setItem(0,1,qtw.QTableWidgetItem(self.ticketDesc.toPlainText()))
        # self.outputTable.resizeColumnsToContents()
        # self.outputTable.resizeRowsToContents()
        self.outputTable.setWordWrap(True)
        

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
        
        # Create Tab 1 - New Ticket
        self.newTicket = NewTicket()
        self.tabWidget.addTab(self.newTicket, "New Ticket")
        # Create Tab 2 - All Tickets
        self.tabWidget.addTab(qtw.QLabel("All tickets go here"), "All Tickets")
        
        self.show()
        
if __name__== "__main__":
    # Start the app
    app = qtw.QApplication([])
    mainWindow = MainWindow()
    app.exec_()
    
# Commit and close the connection
    
conn.commit()
conn.close()
