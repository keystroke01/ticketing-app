#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 14:50:14 2021

@author: k
"""

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg

class NewTicket(qtw.QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Ticketing App")
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
        self.submitButton = qtw.QPushButton("Submit")
        
        formLayout.addRow("Title", self.ticketTitle)
        formLayout.addRow("Description", self.ticketDesc)
        formLayout.addRow("Reported Date", self.reportedDate)
        formLayout.addRow("Closed Date", self.closedDate)
        formLayout.addRow("Type", self.ticketType)
        formLayout.addRow("Severity", self.ticketSeverity)
        formLayout.addRow("Status", self.ticketStatus)
        formLayout.addRow(self.submitButton)
        # self.show()
        

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ticketing App")
        
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
        
app = qtw.QApplication([])
mainWindow = MainWindow()
# mainWindow.show()
app.exec_()

#TESTING