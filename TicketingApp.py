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

c.execute("SELECT * FROM STATUS")
status = c.fetchall()

c.execute("SELECT * FROM TICKET_SEVERITY")
ticketSeverity = c.fetchall()

# c.execute("SELECT CODE, DESCRIPTION FROM TICKET_TYPE")
c.execute("SELECT * FROM TICKET_TYPE")
ticketType = c.fetchall()

print(status)


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
        formLayout.addRow(self.headLabel)
        
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
        ticketTypeList = []
        for item in ticketType:
            ticketTypeList.append(item[2])
        self.ticketType.addItems(ticketTypeList)
        
        # Adding items of TICKET_SEVERITY
        self.ticketSeverity = qtw.QComboBox()
        ticketSeverityList = []
        for item in ticketSeverity:
            ticketSeverityList.append(item[2])
        self.ticketSeverity.addItems(ticketSeverityList)
        
        # Adding items of STATUS
        self.ticketStatus = qtw.QComboBox()
        statusList = []
        for item in status:
            statusList.append(item[2])
        self.ticketStatus.addItems(statusList)
        
        
        self.submitButton = qtw.QPushButton("Submit",
                                            clicked = lambda: self.addNewTicket())
        self.resetButton = qtw.QPushButton("Reset",
                                            clicked = lambda: self.resetNewTicket())
        
        # self.outputTable = qtw.QTableWidget(self) 
        # self.outputTable.setRowCount(1)
        # self.outputTable.setColumnCount(2)
        # self.outputTable.setHorizontalHeaderLabels(['Title', 
        #                                             'Desc', 
        #                                             'Reported Date', 
        #                                             'Closed Date'])
        # self.outputTable.setEditTriggers(qtw.QTableWidget.NoEditTriggers)
        
        self.outputTextEdit = qtw.QTextEdit(self,
                                            lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                            lineWrapColumnOrWidth = 75,
                                            placeholderText="Output",
                                            readOnly=True)
        
        
        # Add widgets to the form layout
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
            print(err)
            msg = qtw.QMessageBox()
            msg.setIcon(qtw.QMessageBox.Critical)
            msg.setText(err)
            msg.setWindowTitle("Error")
            msg.exec_()
           
            
                
        else: 
            print("no")
            # sqlQuery = """
            # INSERT INTO TICKETS (TITLE, 
            #                      DESCRIPTION, 
            #                      REPORTED_DATE, 
            #                      CLOSED_DATE, 
            #                      TICKET_TYPE_ID, 
            #                      TICKET_SEVERITY_ID, 
            #                      STATUS_ID) VALUES ("""
            # sqlQuery += f"'{self.ticketTitle.text()}', '{self.ticketDesc.toPlainText()}')"
            # c.execute(sqlQuery)
            
            print("Row added")
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
        self.ticketType.clear()
        self.ticketSeverity.clear()
        self.ticketStatus.clear()



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
