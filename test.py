import sys
from PyQt5. QtWidgets import (QApplication, QWidget, QPushButton)
#from PyQt5.Qt import Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        button = QPushButton('test',self)

    def keyPressEvent(self, event):
        print('Key Press Event fired')



if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = MainWindow()
    demo.show()

    sys.exit(app.exec_())

