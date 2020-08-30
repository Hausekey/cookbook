from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.Qt import QSize
from PyQt5.QtCore import pyqtSlot, QAbstractItemModel, Qt
import sys
import os
from os import listdir
from os.path import isfile, join
from shutil import copyfile
import utils
import textract
from parse_pdf import TfIdfAnalyzer

# todo: have tf idf data be saved for quick access when app closes & re-open
# todo: freeze the solution so that it can be a stand-alone app
# todo: have indicator when loading is done
# todo: url-ize the results so that document will open upon click
# todo: list out available documents

qt_creator_file = "../ui/mainwindow.ui"
qt_recipeview = "../ui/recipepage.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
Ui_RecipeView, QtRecipeViewClass = uic.loadUiType(qt_recipeview)
contentspath = os.getcwd() + "/files/"

class RecipePage(QtWidgets.QMainWindow, Ui_RecipeView):
    def __init__(self, parent=None, content=""):
        super(RecipePage, self).__init__(parent)
        Ui_RecipeView.__init__(self)
        self.setupUi(self)
        self.textEdit.setText(utils.displayable_path(content))

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        Ui_MainWindow.__init__(self)
        self.setWindowIcon(QtGui.QIcon('../ui/images/logo.png'))
        self.setupUi(self)
        self.setWindowTitle("Leejung's Chinese Cookbook")

        self.contentsModel = ContentsModel()
        self.setFixedSize(1089, 611)
        self.load()
        self.contentsView.setModel(self.contentsModel)
        self.addButton.pressed.connect(self.add)
        self.removeButton.pressed.connect(self.delete)
        self.viewButton.pressed.connect(self.openDoc)
        self.dialog = RecipePage()
        self.searchengine = TfIdfAnalyzer()

    def load(self):
        if os.path.exists(utils.syspath(contentspath)):
            self.contentsModel.contents = [utils.bytestring_path(f) for f in listdir(contentspath) if isfile(join(contentspath, f))]
        else:
            os.mkdir(contentspath)

    def add(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;.pdf (*.pdf);;.", options=options)
        if files:
            print(files)
            for f in files:
                copyfile(utils.bytestring_path(f), utils.bytestring_path(contentspath + os.path.basename(f)))
                contentButton = QtWidgets.QPushButton("button")
                contentButton.pressed.connect(self.openDoc)
            #self.contentsModel.contents = [utils.bytestring_path(f) for f in listdir(contentspath) if isfile(join(contentspath, f))]
            self.searchengine.setupcorpus(files)
        self.searchengine.Tfidf()
        self.contentsModel.layoutChanged.emit()

    def delete(self):
        indexes = self.contentsView.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            print(self.contentsModel.contents[row])
            try:
                os.remove(utils.syspath(utils.bytestring_path(contentspath) + self.contentsModel.contents[row]))
                del self.contentsModel.contents[index.row()]
                self.contentsModel.layoutChanged.emit()
            except PermissionError:
                print("Permission denied")

    def openDoc(self):
        indexes = self.contentsView.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            text = textract.process(utils.displayable_path(utils.bytestring_path(contentspath) + utils.bytestring_path(self.contentsModel.contents[row])))
            self.dialog = RecipePage(self, text)
            print(text)
            self.dialog.show()


# Table of Contents
class ContentsModel(QtCore.QAbstractListModel):
    def __init__(self, *args, contents=None, **kwargs):
        super(ContentsModel, self).__init__(*args, **kwargs)
        self.contents = contents or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            title = self.contents[index.row()]
            return utils.displayable_path(title)

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

