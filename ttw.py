import sys
import os
import json
import ctypes
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWinExtras import QtWin

if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

myappid='deflop.telltheworld.0.1'
QtWin.setCurrentProcessExplicitAppUserModelID(myappid)

from pypresence import Presence

app = QtWidgets.QApplication(sys.argv)
app.rpc = None
app.clientid = None

with open('ttw.db', 'a+') as f:
    f.seek(0)
    print(bool(f.read(0)))
    if bool(f.read(0)):
        sjson = {'clientid': 0, 'details': '', 'state': '', 'imagekey': ''}
        json.dump(sjson, f)


try:
    with open('ttw.db', 'r+') as f:
        data = json.load(f)
        app.clientid = data['clientid']
except Exception as e:
    print(e)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        uic.loadUi("window.ui", self)
        mega = QIcon('mega.png')
        self.setWindowTitle('Tell The World RPC 1.0.0')
        self.setWindowIcon(mega)
        self.stopbutton.setEnabled(False)
        self.startbutton.setEnabled(False)
        self.state.setEnabled(False)
        self.details.setEnabled(False)
        self.imagekey.setEnabled(False)
        self.refreshbutton.setEnabled(False)
        self.connect.clicked.connect(self.do_connect)
        self.startbutton.clicked.connect(self.start_rpc)
        self.stopbutton.clicked.connect(self.stop_rpc)
        self.refreshbutton.clicked.connect(self.refresh)
        if app.clientid:
            self.clientid.setText(str(app.clientid))
            self.do_connect(app.clientid)
            self.details.setText(data['details'])
            self.state.setText(data['state'])
            self.imagekey.setText(data['imagekey'])
            self.start_rpc()

    def do_connect(self, client_id = None):
        app.rpc = Presence(client_id or self.clientid.text())
        app.rpc.connect()
        self.connect.setEnabled(False)
        self.startbutton.setEnabled(True)
        self.clientid.setEnabled(False)
        self.state.setEnabled(True)
        self.imagekey.setEnabled(True)
        self.details.setEnabled(True)

    def start_rpc(self):
        with open('ttw.db', 'w+') as f:
            data['clientid'] = app.clientid or self.clientid.text()
            data['details'] = self.details.text()
            data['state'] = self.state.text()
            data['imagekey'] = self.imagekey.text()
            json.dump(data, f)
        app.rpc.update(state=self.state.text(), details=self.details.text(), large_image=self.imagekey.text())
        self.stopbutton.setEnabled(True)
        self.startbutton.setEnabled(False)
        self.refreshbutton.setEnabled(True)

    def stop_rpc(self):
        app.rpc.clear()
        self.stopbutton.setEnabled(False)
        self.startbutton.setEnabled(True)
        self.state.setEnabled(True)
        self.details.setEnabled(True)
        self.refreshbutton.setEnabled(False)


    def refresh(self):
        app.rpc.update(state=self.state.text(), details=self.details.text(), large_image=self.imagekey.text())

window = MainWindow()
window.show()

app.setQuitOnLastWindowClosed(False)

# Create the icon
icon = QIcon("mega.png")

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Create the menu
menu = QMenu()
action = QAction("Open")
action.triggered.connect(window.show)
menu.addAction(action)

# Add a Quit option to the menu.
quit = QAction("Quit")
quit.triggered.connect(app.quit)
menu.addAction(quit)

# Add the menu to the tray
tray.setContextMenu(menu)

app.exec_()