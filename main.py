import sys
import io

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from ui import Ui_MainWindow
from PyQt5.QtGui import QIcon
from about_ui import Ui_Form

from coupon_generator import *
from reimbursement_table_generateor import *


app = QtWidgets.QApplication(sys.argv)
app.setWindowIcon(QIcon("./assets/ui_images_element/icon.png"))
MainWindow = QtWidgets.QMainWindow()
gui = Ui_MainWindow()
gui.setupUi(MainWindow)
MainWindow.show()

def popup_error_window():
    dialog = QMessageBox()
    dialog.setWindowTitle('Something went wrong')
    dialog.setIcon(QMessageBox.Icon.Warning)
    dialog.setText('Please configure both the image path and the output directory.')

    dialog.exec()

def popup_complete():

    dialog = QMessageBox ()
    dialog.setText ("Complete Generation!!")
    dialog.setWindowTitle("What's going on")
    dialog.setIcon(QMessageBox.Icon.Information)
    dialog.exec()

def get_parameters():
    amount = gui.generateAmount_spinBox.value()
    serial_start_number = gui.serialNumberStart_spinBox.value()
    serial_prefix = gui.serialNumberPrefix_lineEdit.text()
    back_image_path = gui.pictureDir_lineEdit_2.text()
    output_path = gui.targetDir_lineEdit.text()

    return amount, serial_start_number, serial_prefix, back_image_path, output_path


info_text = get_info_text()
gui.precaution_plainTextEdit.setPlainText(info_text)

_, serial_start_number, serial_prefix, _, _ = get_parameters()
image = generate_preview_coupon( default_back_image_path , serial_prefix, serial_start_number)
image_bytes = io.BytesIO()
image.save(image_bytes, format='PNG')
qt = QtGui.QPixmap()
qt.loadFromData(image_bytes.getvalue())
gui.previewPicture_label.setPixmap(qt)



def open_file_picker():
    filePath , filterType   =  QFileDialog.getOpenFileName(None ,'open_file',None ,"JPEG (*.jpg *.jpeg);;PNG (*.png)" )
    if filePath == '':
        filePath = '底圖檔案路徑'
    print(filePath , filterType)
    gui.pictureDir_lineEdit_2.setText(filePath)


def open_target_folder():
    filePath =  QFileDialog.getExistingDirectory(None ,'open_folder' )
    if filePath == '':
        filePath = '輸出儲存目錄'
    print(filePath)
    filePath = f'{filePath}/output'
    gui.targetDir_lineEdit.setText(filePath)





def generatePreview_button():
    try:
        _, serial_start_number, serial_prefix, back_image_path, _ = get_parameters()
        info_text = gui.precaution_plainTextEdit.toPlainText()
        write_info_text(info_text)
        image = generate_preview_coupon(back_image_path, serial_prefix, serial_start_number)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        qt = QtGui.QPixmap()
        qt.loadFromData(image_bytes.getvalue())
        gui.previewPicture_label.setPixmap(qt)
    except:popup_error_window()



def startingGenerate_button():
    try:
        info_text = gui.precaution_plainTextEdit.toPlainText()
        write_info_text(info_text)
        gui.progressBar.setFormat('%v/%m')
        amount, serial_start_number, serial_prefix, back_image_path, output_path = get_parameters()

        if gui.generateTableOrNot_checkBox.isChecked():
            generate_table(amount, serial_start_number, serial_prefix, 36, f'{output_path}.xlsx')

        

        blank_coupon = generate_coupon_image(back_image_path, default_upper_element_path, get_info_text())
        paper = generate_paper(PAPER_SIZE)
        copied_paper = copy.deepcopy(paper)
        processbar_total = amount//6
        if  processbar_total == 0:
            processbar_total = 1
        gui.progressBar.setRange(0, processbar_total)

        pieces_counting = 0
        pages_counting = 0

        output = []

        for i in range(serial_start_number, serial_start_number + amount):
            serial_number = f'NO. {serial_prefix}{str(i).zfill(4)}'
            coupon = coupon_add_number(copy.deepcopy(blank_coupon), serial_number)
            copied_paper.paste(coupon, COUPONS_POSITIONS[pieces_counting + 1], coupon)
            print(f'Generate coupon: {serial_number}', end='\r')
            pieces_counting += 1

            gui.progressBar.setValue(pages_counting)
            
            if pieces_counting == 6:
                output.append(copied_paper)
                copied_paper = copy.deepcopy(paper)
                pieces_counting = 0
                pages_counting += 1
                print(f'Generate page: {pages_counting}', end='\r')

        if pieces_counting != 0:
            output.append(copied_paper)
            print(f'Generate page: {pages_counting}', end='\r')
            gui.progressBar.setRange(0, 0)

        combine_papers( output, f'{output_path}.pdf')
        gui.progressBar.setRange(0, processbar_total)
        gui.progressBar.setValue(processbar_total)
        popup_complete()

    except:popup_error_window()
    

    

# gui.showNewWindow




gui.startingGenerate_button.clicked.connect(startingGenerate_button)
gui.generatePreview_button.clicked.connect(generatePreview_button)
gui.browsePictureFile_button.clicked.connect(open_file_picker)
gui.browseTargetDir_button.clicked.connect(open_target_folder)


sys.exit(app.exec_())