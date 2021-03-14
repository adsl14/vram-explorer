from lib.RB2_characterEditor_design import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from lib.STPK_struct import STPK_struct
from lib.SPRP_struct import SPRP_struct
from lib.SPRP_DATA_INFO import SPRP_DATA_INFO
from lib.TX2D_INFO import TX2D_INFO

import os, numpy as np
from pyglet import image
from shutil import copyfile

# number of bytes that usually reads the program
bytes2Read = 4
# Current selected texture in the list view
currentSelectedTexture = 0

# Paths where are the files
spr_file_path_original = ""
spr_file_path = ""
vram_file_path_original = ""
vram_file_path = ""
sprp_struct = SPRP_struct()
stpk_struct = STPK_struct()

# Meta information (offset to tx2dInfos)
sprpDatasInfo = []
# Texture names
textureNames = []
# Information of the texture
tx2dInfos = []
# The textures itslef
textures_data = []
# Size of the vram file
vram_fileSize = 0
# Indexes of textures edited
textures_index_edited = []
# Quanty of difference between the modifed texture and the old one
offset_quanty_difference = None

def readDDSFile(filePath):

    _img = image.load(filePath)
    tex = _img.get_texture()
    tex = tex.get_image_data()
    _format = tex.format
    pitch = tex.width * len(_format)
    pixels = tex.get_data(_format, pitch)

    img = QImage(pixels, tex.width, tex.height, QImage.Format_RGB32)
    img = img.rgbSwapped()

    return img


def openSPRFile(spr_path):

    with open(spr_path, mode='rb') as file:

        # Move the pointer to the pos 16 and get the offset of the header
        file.seek(16)
        stpk_struct.dataOffset = int.from_bytes(file.read(bytes2Read), "big")

        # Create the sprp_struct instance
        file.seek(stpk_struct.dataOffset + 20)
        sprp_struct.typeInfoBase = stpk_struct.dataOffset + 64
        sprp_struct.stringBase = sprp_struct.typeInfoBase + int.from_bytes(file.read(bytes2Read), "big")
        file.seek(stpk_struct.dataOffset + 24)
        sprp_struct.dataInfoBase = sprp_struct.stringBase + int.from_bytes(file.read(bytes2Read), "big")
        file.seek(stpk_struct.dataOffset + 28)
        sprp_struct.dataBase = sprp_struct.dataInfoBase + int.from_bytes(file.read(bytes2Read), "big")
        file.seek(sprp_struct.typeInfoBase + 8)
        sprp_struct.dataCount = int.from_bytes(file.read(bytes2Read), "big")

        # Get the names of each texture
        file.seek(sprp_struct.stringBase)
        texture_name = ""
        counter = 0

        while True:
            data = file.read(1)
            data = data.decode("ISO-8859-1")
            texture_name += data
            if ".tga" in texture_name:
              textureNames.append(texture_name[1:].replace(".tga",""))
              texture_name = ""
              counter += 1
              if counter == sprp_struct.dataCount:
                  break

        # Create a numpy array of zeros
        global offset_quanty_difference
        offset_quanty_difference = np.zeros(sprp_struct.dataCount)

        # Get the data info (TX2D)
        file.seek(sprp_struct.dataInfoBase)
        for i in range(0,sprp_struct.dataCount):
            sprp_data_info = SPRP_DATA_INFO()

            # Move where the information starts
            file.seek(8, os.SEEK_CUR)
            sprp_data_info.nameOffset = int.from_bytes(file.read(bytes2Read), "big")
            sprp_data_info.dataOffset = int.from_bytes(file.read(bytes2Read), "big")
            sprp_data_info.dataSize = int.from_bytes(file.read(bytes2Read), "big")
            sprpDatasInfo.append(sprp_data_info)

            # Move to the next start offset
            file.seek(12, os.SEEK_CUR)

        # Get the data itself
        for sprpDataInfo in sprpDatasInfo:
            tx2D_info = TX2D_INFO()

            # Move where the information starts
            file.seek(sprp_struct.dataBase + sprpDataInfo.dataOffset)

            # Move where the information starts
            file.seek(4, os.SEEK_CUR)
            tx2D_info.dataOffset = int.from_bytes(file.read(bytes2Read), "big")
            file.seek(4, os.SEEK_CUR)
            tx2D_info.dataSize = int.from_bytes(file.read(bytes2Read), "big")
            tx2D_info.width = int.from_bytes(file.read(2), "big")
            tx2D_info.height = int.from_bytes(file.read(2), "big")
            file.seek(12, os.SEEK_CUR)
            tx2D_info.dxtEncoding = int.from_bytes(file.read(1), "big")
            tx2dInfos.append(tx2D_info)


def getDXTByte(value):

    if value == 8:
        return "DXT1".encode()
    elif value == 24 or value == 32:
        return "DXT5".encode()
    elif value == 0:
        return "RGBA".encode()


def openVRAMFile(vram_path, tx2dInfos):

    with open(vram_path, mode="rb") as file:
        # Move to the position 16, where it tells the offset of the file where the texture starts
        file.seek(16)
        texture_offset = int.from_bytes(file.read(bytes2Read), "big")

        # The size of the file is in position 20
        global vram_fileSize
        vram_fileSize = int.from_bytes(file.read(bytes2Read), "big")

        # Get each texture
        header_1 = "44 44 53 20 7C 00 00 00 07 10 00 00".strip()
        header_1 = bytes.fromhex(header_1)
        header_3_1 = "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 04 00 00 00 ".strip()
        header_3_3 = "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ".strip()
        header_3_1 = bytes.fromhex(header_3_1)
        header_3_3 = bytes.fromhex(header_3_3)
        for tx2dInfo in tx2dInfos:

            header_2 = tx2dInfo.height.to_bytes(4, 'little') + tx2dInfo.width.to_bytes(4, 'little')
            header_3_2 = getDXTByte(tx2dInfo.dxtEncoding)
            header = header_1 + header_2 + header_3_1 + header_3_2 + header_3_3

            file.seek(tx2dInfo.dataOffset + texture_offset)
            data = file.read(tx2dInfo.dataSize)
            data = header + data
            textures_data.append(data)


def actionItem(QModelIndex, imageTexture, encodingImageText, sizeImageText):

    global currentSelectedTexture
    currentSelectedTexture = QModelIndex.row()
    textureName = textureNames[currentSelectedTexture]

    # Textures with the name 'rs' or '_' at the starts, doesn't work
    if textureName[0] != "_" and textureName[0:2] != "rs":
        # Create the dds in disk and open it
        file = open("temp.dds", mode="wb")
        file.write(textures_data[currentSelectedTexture])
        file.close()
        img = readDDSFile("temp.dds")
        os.remove("temp.dds")
        # Show the image
        imageTexture.setPixmap(QPixmap.fromImage(img))
    else:
        imageTexture.clear()

    encodingImageText.setText("Encoding: %s" % (getDXTByte(tx2dInfos[currentSelectedTexture].dxtEncoding).decode('utf-8')))
    sizeImageText.setText("Size: %dx%d" % (tx2dInfos[currentSelectedTexture].width, tx2dInfos[currentSelectedTexture].height))

def removeUncompressedFile(uncompressed_file):

    # Remove the output file if exists, because the script won't work if there is a output file with the same name
    if os.path.exists(uncompressed_file):
        os.system('cmd /c ' + "rm \"" + uncompressed_file + "\"")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # File tab
        self.actionOpen.triggered.connect(self.actionOpenLogic)
        self.actionSave.triggered.connect(self.actionSaveLogic)
        self.actionClose.triggered.connect(self.close)

        # About tab
        self.actionAuthor.triggered.connect(self.actionAuthorLogic)
        self.actionCredits.triggered.connect(self.actionCreditsLogic)

        # Buttons
        self.exportButton.clicked.connect(self.actionExportLogic)
        self.importButton.clicked.connect(self.actionImportLogic)
        self.exportButton.setVisible(False)
        self.importButton.setVisible(False)

        # Label
        self.encodingImageText.setVisible(False)
        self.sizeImageText.setVisible(False)

    def actionExportLogic(self):

        # Save dds file
        dds_export_path = QFileDialog.getSaveFileName(self, "Save file", os.path.join(os.path.abspath(os.getcwd()), textureNames[currentSelectedTexture]+".dds"), "DDS file (*.dds)")[0]
        if dds_export_path:
            file = open(dds_export_path, mode="wb")
            file.write(textures_data[currentSelectedTexture])
            file.close()

    def actionImportLogic(self):

        # Open spr file
        dds_import_path = QFileDialog.getOpenFileName(self, "Open file", os.path.abspath(os.getcwd()), "DDS file (*.dds)")[0]
        if dds_import_path:
            with open(dds_import_path, mode="rb") as file:
                # Get the height and width of the modified image
                file.seek(12)
                height = int.from_bytes(file.read(bytes2Read),'little')
                width = int.from_bytes(file.read(bytes2Read), 'little')
                # Get the dxtencoding
                file.seek(84)
                dxtEncoding = file.read(bytes2Read)
                # Get all the data
                file.seek(0)
                data = file.read()

            # Get the tx2dinfo of the texture
            tx2dInfo = tx2dInfos[currentSelectedTexture]
            dxtEncodingOriginal = getDXTByte(tx2dInfo.dxtEncoding)
            # Check if the size of original and modified one are the same
            if tx2dInfo.width != width or tx2dInfo.height != height:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("The size for the modified file must be %dx%d\nYour file is %dx%d" % (tx2dInfo.width, tx2dInfo.height, width, height))
                msg.exec()
            # The original and modified file must be in the same dxtencoding
            elif dxtEncodingOriginal != dxtEncoding:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("The encoding for the modified file must be in %s\nYour file is in %s" % (dxtEncodingOriginal.decode("utf-8") , dxtEncoding.decode("utf-8") ))
                msg.exec()
            # Can import the texture
            else:
                # Get the difference in size between original and modified in order to change the offsets
                len_data = len(data[128:])
                difference = len_data - tx2dInfos[currentSelectedTexture].dataSize
                if difference != 0:
                    tx2dInfos[currentSelectedTexture].dataSize = len_data
                    offset_quanty_difference[currentSelectedTexture] = difference

                # Change texture in the array
                textures_data[currentSelectedTexture] = data

                # Add the index texture that has been modified
                textures_index_edited.append(currentSelectedTexture)

                # Show texture in the program
                img = readDDSFile(dds_import_path)
                # Show the image
                self.imageTexture.setPixmap(QPixmap.fromImage(img))

    def actionOpenLogic(self):

        # Open spr file
        global spr_file_path_original
        spr_file_path_original = QFileDialog.getOpenFileName(self, "Open file", os.path.abspath(os.getcwd()), "SPR files (*.spr)")[0]
        if not os.path.exists(spr_file_path_original):
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("A spr file is needed.")
            msg.exec()
            return
        global spr_file_path
        # Execute the script in a command line
        spr_file_path = spr_file_path_original.replace(".spr","_u.spr")
        if not os.path.exists(spr_file_path):
            args = os.path.join("lib","dbrb_compressor.exe") + " \"" + spr_file_path_original + "\" \"" + spr_file_path + "\""
            os.system('cmd /c ' + args)

        # Open vram file
        global vram_file_path_original
        vram_file_path_original = QFileDialog.getOpenFileName(self, "Open file", os.path.abspath(os.getcwd()), "Texture files (*.vram)")[0]
        if not os.path.exists(vram_file_path_original):
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("A vram file is needed.")
            msg.exec()
            return

        global vram_file_path
        # Execute the script in a command line
        vram_file_path = vram_file_path_original.replace(".vram","_u.vram")
        if not os.path.exists(vram_file_path):
            args = os.path.join("lib","dbrb_compressor.exe") + " \"" + vram_file_path_original + "\" \"" + vram_file_path + "\""
            os.system('cmd /c ' + args)

        # Load the data from the files
        sprpDatasInfo.clear()
        textureNames.clear()
        tx2dInfos.clear()
        textures_data.clear()
        textures_index_edited.clear()
        openSPRFile(spr_file_path)
        openVRAMFile(vram_file_path, tx2dInfos)

        # Add list names
        global currentSelectedTexture
        currentSelectedTexture = 0
        model = QStandardItemModel()
        self.listView.setModel(model)
        item_0 = QStandardItem(textureNames[0])
        model.appendRow(item_0)
        self.listView.setCurrentIndex(model.indexFromItem(item_0))
        for i in textureNames[1:]:
            item = QStandardItem(i)
            item.setEditable(False)
            model.appendRow(item)
        self.listView.clicked.connect(lambda qModelIdx: actionItem(qModelIdx, self.imageTexture, self.sizeImageText, self.encodingImageText))

        # Create the dds in disk and open it
        file = open("temp.dds", mode="wb")
        file.write(textures_data[0])
        file.close()
        img = readDDSFile("temp.dds")
        os.remove("temp.dds")
        # Show the image
        self.imageTexture.setPixmap(QPixmap.fromImage(img))

        # Show the buttons
        self.exportButton.setVisible(True)
        self.importButton.setVisible(True)

        # Show the text labels
        self.encodingImageText.setText("Encoding: %s" % (getDXTByte(tx2dInfos[currentSelectedTexture].dxtEncoding).decode('utf-8')))
        self.sizeImageText.setText("Size: %dx%d" % (tx2dInfos[currentSelectedTexture].width, tx2dInfos[currentSelectedTexture].height))
        self.encodingImageText.setVisible(True)
        self.sizeImageText.setVisible(True)

    def actionSaveLogic(self):

        if not textures_data:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("There is no character loaded.")
            msg.exec()
        elif not textures_index_edited:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("The character hasn't been modified.")
            msg.exec()
        else:

            # Default paths
            spr_export_path = spr_file_path.replace(".spr", "_m.spr")
            vram_export_path = vram_file_path.replace(".vram","_m.vram")

            # Sort the indexes of the modified textures
            textures_index_edited.sort()

            # modifying the spr file offsets
            global spr_file_path_original
            spr_file_path_modified = spr_file_path_original.replace(".spr", "_m.spr")

            # Create a copy of the original file
            copyfile(spr_file_path, spr_export_path)

            # Update the offsets
            first_index_texture_edited = textures_index_edited[0]
            quanty_aux = 0
            if first_index_texture_edited + 1 < sprp_struct.dataCount:
                tx2dInfos[first_index_texture_edited].dataOffsetOld = tx2dInfos[first_index_texture_edited].dataOffset
                quanty_aux = int(offset_quanty_difference[first_index_texture_edited])
                for i in range(first_index_texture_edited + 1, sprp_struct.dataCount):
                    tx2dInfos[i].dataOffsetOld = tx2dInfos[i].dataOffset
                    tx2dInfos[i].dataOffset += quanty_aux
                    tx2dInfos[i].dataOffset = int(abs(tx2dInfos[i].dataOffset))
                    quanty_aux += offset_quanty_difference[i]

            with open(spr_export_path, mode="rb+") as output_file_spr:
                # Move where the information starts to the first modified texture
                output_file_spr.seek(sprp_struct.dataBase + sprpDatasInfo[first_index_texture_edited].dataOffset + 12)
                output_file_spr.write(tx2dInfos[first_index_texture_edited].dataSize.to_bytes(4, byteorder="big"))
                first_index_texture_edited += 1
                if first_index_texture_edited < sprp_struct.dataCount:
                    for i in range(first_index_texture_edited,sprp_struct.dataCount):
                        # Move where the information starts to the next textures
                        output_file_spr.seek(sprp_struct.dataBase + sprpDatasInfo[i].dataOffset + 4)
                        output_file_spr.write(tx2dInfos[i].dataOffset.to_bytes(4, byteorder="big"))
                        output_file_spr.seek(4, os.SEEK_CUR)
                        output_file_spr.write(tx2dInfos[i].dataSize.to_bytes(4, byteorder="big"))

            global vram_file_path_original
            vram_file_path_modified = vram_file_path_original.replace(".vram", "_m.vram")

            # replacing textures
            with open(vram_export_path, mode="wb") as output_file:
                with open(vram_file_path, mode="rb") as input_file:

                    # Move to the position 16, where it tells the offset of the file where the texture starts
                    data = input_file.read(16)
                    output_file.write(data)

                    data = input_file.read(bytes2Read)
                    output_file.write(data)
                    texture_offset = int.from_bytes(data, "big")

                    # Get each offset texture and write over the original file
                    for texture_index in textures_index_edited:
                        tx2dInfo = tx2dInfos[texture_index]
                        data = input_file.read(abs(tx2dInfo.dataOffsetOld + texture_offset - input_file.tell()))
                        output_file.write(data)
                        input_file.seek(tx2dInfo.dataSize - int(offset_quanty_difference[texture_index]), os.SEEK_CUR)
                        output_file.write(textures_data[texture_index][128:])

                    data = input_file.read()
                    output_file.write(data)

                    # Modify the bytes in pos 20 that indicates the size of the file
                    global vram_fileSize
                    vram_fileSize += output_file.tell() - input_file.tell()
                    vram_fileSize = abs(vram_fileSize)

            # Change the header of pos 256 in spr file because in that place indicates the size of the final output file
            with open(spr_export_path, mode="rb+") as output_file:
                output_file.seek(stpk_struct.dataOffset + 48)
                output_file.write(vram_fileSize.to_bytes(4, byteorder='big'))
            # Change the header of pos 20 in vram file because that place indicates the size of the final output file
            with open(vram_export_path, mode="rb+") as output_file:
                output_file.seek(20)
                output_file.write(vram_fileSize.to_bytes(4, byteorder='big'))

            removeUncompressedFile(spr_file_path_modified)
            args = os.path.join("lib","dbrb_compressor.exe") + " \"" + spr_export_path + "\" \"" + spr_file_path_modified + "\""
            os.system('cmd /c ' + args)

            removeUncompressedFile(vram_file_path_modified)
            args = os.path.join("lib","dbrb_compressor.exe") + " \"" + vram_export_path + "\" \"" + vram_file_path_modified + "\""
            os.system('cmd /c ' + args)

            msg = QMessageBox()
            msg.setWindowTitle("Message")
            msg.setText("The files were saved and compressed in %s" % (vram_file_path_modified.replace(".vram","")))
            msg.exec()

            # Remove the uncompressed modified files
            os.remove(spr_export_path)
            os.remove(vram_export_path)

    def closeEvent(self, event):
        # Remove the uncompressed files
        removeUncompressedFile(vram_file_path)
        removeUncompressedFile(spr_file_path)

        event.accept()

    def actionAuthorLogic(self):
        msg = QMessageBox()
        msg.setTextFormat(1)
        msg.setWindowTitle("Author")
        msg.setText("RB2 character editor 1.1 by <a href=https://www.youtube.com/channel/UCkZajFypIgQL6mI6OZLEGXw>adsl13</a>")
        msg.exec()

    def actionCreditsLogic(self):
        msg = QMessageBox()
        msg.setTextFormat(1)
        msg.setWindowTitle("Credits")
        msg.setText("To the Raging Blast Modding community and specially for revelation who made the compress/uncompress tool.")
        msg.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
