from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QWidget, QVBoxLayout, QTabWidget, QPushButton, QFileDialog
from PyQt5.QtCore import pyqtSlot
import sys
from parse_pdf import TdfIdfAnalyzer

# todo: have tf idf data be saved for quick access when app closes & re-open
# todo: freeze the solution so that it can be a stand-alone app
# todo: have indicator when loading is done
# todo: url-ize the results so that document will open upon click
# todo: list out available documents

class RecipeFinder(QtWidgets.QMainWindow):
    def __init__(self):
        super(RecipeFinder, self).__init__()
        self.setGeometry(200, 200, 500, 500)
        self.setWindowTitle("Leejung's Chinese Cookbook")
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        self.show()

    def clicked(self):
        self.label.setText("you pressed the button")

class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self._analyzer = TdfIdfAnalyzer()
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.upload_tab = QWidget()
        self.search_tab = QWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.upload_tab, "Upload")
        self.tabs.addTab(self.search_tab, "Search")

        # Create first tab
        self.upload_tab.layout = QVBoxLayout(self)
        self.search_tab.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("Browse")
        self.pushButton1.clicked.connect(self.getfile)
        self.upload_tab.layout.addWidget(self.pushButton1)
        self.upload_tab.setLayout(self.upload_tab.layout)

        self.searchbar = QLineEdit(self)
        self.searchbutton = QPushButton("Search", self)
        self.searchbutton.clicked.connect(self.on_search_click)
        self.searchbutton.move(20, 80)
        self.resultbox = QLabel()
        self.resultbox.setText("testing")
        self.resultbox.setWordWrap(True)
        self.search_tab.layout.addWidget(self.searchbar)
        self.search_tab.layout.addWidget(self.searchbutton)
        self.search_tab.layout.addWidget(self.resultbox)
        self.search_tab.setLayout(self.search_tab.layout)
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def getfile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;.pdf (*.pdf);;.", options=options)
        if files:
            print(files)
            self._analyzer.setupcorpus(files)
        self._analyzer.Tfidf()

    @pyqtSlot()
    def on_search_click(self):
        textboxValue = self.searchbar.text()
        nosearch = 10
        docs = self._analyzer.find_relevant_documents(nosearch, textboxValue)
        self.resultbox.setText(', '.join(docs))


    # @pyqtSlot()
    # def on_click(self):
    #     print("\n")
    #     for currentQTableWidgetItem in self.tableWidget.selectedItems():
    #         print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(""
                      "QLabel { font-size:20px; }"
                      "QPushButton { font-size:20px;}"
                      "QWidget {font-size:20px; }"
                      "")
    ex = RecipeFinder()
    sys.exit(app.exec_())

