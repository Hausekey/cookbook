from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.Qt import QSize
from PyQt5.QtCore import pyqtSlot, QAbstractItemModel, Qt
import sys
import os
from parse_pdf import TdfIdfAnalyzer
from os import listdir
from os.path import isfile, join
from shutil import copyfile

# todo: have tf idf data be saved for quick access when app closes & re-open
# todo: freeze the solution so that it can be a stand-alone app
# todo: have indicator when loading is done
# todo: url-ize the results so that document will open upon click
# todo: list out available documents

qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

contentspath = os.getcwd() + "/files"


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Leejung's Chinese Cookbook")

        self.contentsModel = ContentsModel()
        self.setFixedSize(1089, 611)
        self.load()
        self.contentsView.setModel(self.contentsModel)
        self.addButton.pressed.connect(self.add)
        self.removeButton.pressed.connect(self.delete)

    def load(self):
        if os.path.exists(contentspath):
            self.contentsModel.contents = [f for f in listdir(contentspath) if isfile(join(contentspath, f))]
        else:
            os.mkdir(contentspath)

    def add(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;.pdf (*.pdf);;.", options=options)
        if files:
            print(files)
            #self._analyzer.setupcorpus(files)
            for f in files:
                copyfile(f, contentspath + '/' + os.path.basename(f))
        self.contentsModel.contents = [f for f in listdir(contentspath) if isfile(join(contentspath, f))]
        self.contentsModel.layoutChanged.emit()
        #self._analyzer.Tfidf()

    def delete(self):
        indexes = self.contentsView.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            print(self.contentsModel.contents[row])
            os.remove(contentspath + self.contentsModel.contents[row])
            del self.contentsModel.contents[index.row()]
            self.model.layoutChanged.emit()
            self.contentsModel.clearSelection()



# Table of Contents
class ContentsModel(QtCore.QAbstractListModel):
    def __init__(self, *args, contents=None, **kwargs):
        super(ContentsModel, self).__init__(*args, **kwargs)
        self.contents = contents or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            title = self.contents[index.row()]
            return title

    def rowCount(self, index):
        return len(self.contents)

class ResultButtonModel(QtCore.QAbstractTableModel):
    def __init__(self, result):
        super(ResultTableModel, self).__init__()
        self._results = result


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(""
                      "QLabel { font-size:20px; }"
                      "QPushButton { font-size:20px;}"
                      "QWidget {font-size:20px; }"
                      "")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

