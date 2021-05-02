import os
import stat
from shutil import copyfile, rmtree, move

import numpy as np
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from lib.RB2_characterEditor_design import *
from lib.SprpDataInfo import SprpDataInfo
from lib.SprpStruct import SprpStruct
from lib.StpkStruct import StpkStruct
from lib.Tx2dInfo import Tx2dInfo
from pyglet import image
from datetime import datetime

# types of spr file
# Character file
STPZ0 = "5354505a30"
character_file = False

# number of bytes that usually reads the program
bytes2Read = 4
# Current selected texture in the list view
current_selected_texture = 0
# Temp folder name
temp_folder = "temp_" + datetime.now().strftime("_%d-%m-%Y_%H-%M-%S")

# Paths where are the files
spr_file_path_original = ""
spr_file_path = ""
vram_file_path_original = ""
vram_file_path = ""
sprp_struct = SprpStruct()
stpk_struct = StpkStruct()

# Meta information (offset to tx2dInfos)
sprpDatasInfo = []
# Texture names
textureNames = []
# Information of the texture
tx2d_infos = []
# The textures itslef
textures_data = []
# Size of the vram file
vram_file_size_old = 0
# Indexes of textures edited
textures_index_edited = []
# Quanty of difference between the modifed texture and the old one
offset_quanty_difference = np.array(0)


def show_dds_image(imagetexture, texture_data):
    try:
        # Create the dds in disk and open it
        file = open("temp.dds", mode="wb")
        file.write(texture_data)
        file.close()
        img = read_dds_file("temp.dds")
        # Show the image
        imagetexture.setPixmap(QPixmap.fromImage(img))
    except OSError:
        imagetexture.clear()

    os.remove("temp.dds")


def del_rw(name_method, path, error):
    os.chmod(path, stat.S_IWRITE)
    os.remove(path)

    return name_method, error


def read_dds_file(file_path):
    try:
        _img = image.load(file_path)
    except OSError:
        print("The header of the image is not recognizable")
        raise OSError

    tex = _img.get_texture()
    tex = tex.get_image_data()
    _format = tex.format
    pitch = tex.width * len(_format)
    pixels = tex.get_data(_format, pitch)

    img = QImage(pixels, tex.width, tex.height, QImage.Format_RGB32)
    img = img.rgbSwapped()

    return img


def open_spr_file(spr_path, start_pointer):
    with open(spr_path, mode='rb') as file:

        # Move the pointer to the pos 16 and get the offset of the header
        file.seek(start_pointer)
        stpk_struct.data_offset = int.from_bytes(file.read(bytes2Read), "big")

        # Create the sprp_struct instance
        file.seek(stpk_struct.data_offset + 20)
        sprp_struct.type_info_base = stpk_struct.data_offset + 64
        sprp_struct.string_base = sprp_struct.type_info_base + int.from_bytes(file.read(bytes2Read), "big")
        file.seek(stpk_struct.data_offset + 24)
        sprp_struct.data_info_base = sprp_struct.string_base + int.from_bytes(file.read(bytes2Read), "big")
        file.seek(stpk_struct.data_offset + 28)
        sprp_struct.data_base = sprp_struct.data_info_base + int.from_bytes(file.read(bytes2Read), "big")
        file.seek(sprp_struct.type_info_base + 8)
        sprp_struct.data_count = int.from_bytes(file.read(bytes2Read), "big")

        # Get the names of each texture
        file.seek(sprp_struct.string_base + 1)
        texture_name = ""
        counter = 0
        record_byte = True

        while True:
            data = file.read(1)
            if record_byte:
                if data == bytes.fromhex('2E'):
                    textureNames.append(texture_name)
                    texture_name = ""
                    counter += 1
                    if counter == sprp_struct.data_count:
                        break
                    record_byte = False
                    continue
                # If in the middle of the string there is a '00' value, we replace it with '_' in hex
                elif data == bytes.fromhex('00'):
                    data = "_".encode()

                texture_name += data.decode('utf-8')
            else:
                if data == bytes.fromhex('00'):
                    record_byte = True

        # Create a numpy array of zeros
        global offset_quanty_difference
        offset_quanty_difference = np.zeros(sprp_struct.data_count)

        # Get the data info (TX2D)
        file.seek(sprp_struct.data_info_base)
        for i in range(0, sprp_struct.data_count):
            sprp_data_info = SprpDataInfo()

            # Move where the information starts
            file.seek(8, os.SEEK_CUR)
            sprp_data_info.name_offset = int.from_bytes(file.read(bytes2Read), "big")
            sprp_data_info.data_offset = int.from_bytes(file.read(bytes2Read), "big")
            sprp_data_info.dataSize = int.from_bytes(file.read(bytes2Read), "big")
            sprpDatasInfo.append(sprp_data_info)

            # Move to the next start offset
            file.seek(12, os.SEEK_CUR)

        # Get the data itself
        for sprpDataInfo in sprpDatasInfo:
            tx2_d_info = Tx2dInfo()

            # Move where the information starts
            file.seek(sprp_struct.data_base + sprpDataInfo.data_offset)

            # Move where the information starts
            file.seek(4, os.SEEK_CUR)
            tx2_d_info.data_offset = int.from_bytes(file.read(bytes2Read), "big")
            tx2_d_info.data_offset_old = tx2_d_info.data_offset
            file.seek(4, os.SEEK_CUR)
            tx2_d_info.data_size = int.from_bytes(file.read(bytes2Read), "big")
            tx2_d_info.data_size_old = tx2_d_info.data_size
            tx2_d_info.width = int.from_bytes(file.read(2), "big")
            tx2_d_info.height = int.from_bytes(file.read(2), "big")
            file.seek(2, os.SEEK_CUR)
            tx2_d_info.mip_maps = int.from_bytes(file.read(2), "big")
            file.seek(8, os.SEEK_CUR)
            tx2_d_info.dxt_encoding = int.from_bytes(file.read(1), "big")
            tx2d_infos.append(tx2_d_info)


def create_header(value):
    if value == 8:
        return bytes.fromhex("04000000"), "DXT1".encode(), bytes.fromhex(
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 ".strip())
    elif value == 24 or value == 32:
        return bytes.fromhex("04000000"), "DXT5".encode(), bytes.fromhex(
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 10 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 ".strip())
    else:
        return bytes.fromhex("41000000"), bytes.fromhex("00000000"), bytes.fromhex(
            "20 00 00 00 00 00 FF 00 00 FF 00 00 FF 00 00 00 00 00 00 FF 02 10 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00".strip())


def get_dxt_byte(value):
    # 0x00 RGBA, 0x08 DXT1, 0x24 and 0x32 as DXT5
    if value == 8:
        return "DXT1".encode()
    elif value == 24 or value == 32:
        return "DXT5".encode()
    else:
        return "RGBA".encode()


def open_vram_character_file(vram_path):
    global vram_file_size_old, tx2d_infos

    with open(vram_path, mode="rb") as file:
        # Move to the position 16, where it tells the offset of the file where the texture starts
        file.seek(16)
        texture_offset = int.from_bytes(file.read(bytes2Read), "big")

        # The size of the file is in position 20
        vram_file_size_old = int.from_bytes(file.read(bytes2Read), "big")

        # Get each texture
        header_1 = "44 44 53 20 7C 00 00 00 07 10 00 00".strip()
        header_1 = bytes.fromhex(header_1)
        header_3 = "00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 " \
                   "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 ".strip()
        header_3 = bytes.fromhex(header_3)
        for tx2dInfo in tx2d_infos:
            header_2 = tx2dInfo.height.to_bytes(4, 'little') + tx2dInfo.width.to_bytes(4, 'little') + (
                    tx2dInfo.width * tx2dInfo.height).to_bytes(4, 'little')
            header_4, header_5, header_6 = create_header(tx2dInfo.dxt_encoding)
            header = header_1 + header_2 + header_3 + header_4 + header_5 + header_6

            file.seek(tx2dInfo.data_offset + texture_offset)
            data = file.read(tx2dInfo.data_size)
            data = header + data
            textures_data.append(data)


def open_vram_file(vram_path):
    global vram_file_size_old, tx2d_infos

    with open(vram_path, mode="rb") as file:
        # Move to the position 0, where it tells the offset of the file where the texture starts
        texture_offset = 0

        # The size of the file is the size of the texture
        vram_file_size_old = tx2d_infos[0].data_size

        # Get each texture
        header_1 = "44 44 53 20 7C 00 00 00 07 10 00 00".strip()
        header_1 = bytes.fromhex(header_1)
        header_3 = "00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 " \
                   "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 ".strip()
        header_3 = bytes.fromhex(header_3)
        for tx2dInfo in tx2d_infos:
            header_2 = tx2dInfo.height.to_bytes(4, 'little') + tx2dInfo.width.to_bytes(4, 'little') + (
                    tx2dInfo.width * tx2dInfo.height).to_bytes(4, 'little')
            header_4, header_5, header_6 = create_header(tx2dInfo.dxt_encoding)
            header = header_1 + header_2 + header_3 + header_4 + header_5 + header_6

            file.seek(tx2dInfo.data_offset + texture_offset)
            data = file.read(tx2dInfo.data_size)
            data = header + data
            textures_data.append(data)


def action_item(q_model_index, image_texture, encoding_image_text, mip_maps_image_text, size_image_text):
    global current_selected_texture

    if current_selected_texture != q_model_index.row():
        current_selected_texture = q_model_index.row()

        show_dds_image(image_texture, textures_data[current_selected_texture])

        encoding_image_text.setText(
            "Encoding: %s" % (get_dxt_byte(tx2d_infos[current_selected_texture].dxt_encoding).decode('utf-8')))
        mip_maps_image_text.setText("Mipmaps: %s" % tx2d_infos[current_selected_texture].mip_maps)
        size_image_text.setText(
            "Resolution: %dx%d" % (tx2d_infos[current_selected_texture].width, tx2d_infos[current_selected_texture]
                                   .height))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # File tab
        self.actionOpen.triggered.connect(self.action_open_logic)
        self.actionSave.triggered.connect(self.action_save_logic)
        self.actionClose.triggered.connect(self.close)

        # About tab
        self.actionAuthor.triggered.connect(self.action_author_logic)
        self.actionCredits.triggered.connect(self.action_credits_logic)

        # Buttons
        self.exportButton.clicked.connect(self.action_export_logic)
        self.exportAllButton.clicked.connect(self.action_export_all_logic)
        self.importButton.clicked.connect(self.action_import_logic)
        self.exportButton.setVisible(False)
        self.exportAllButton.setVisible(False)
        self.importButton.setVisible(False)

        # Labels
        self.encodingImageText.setVisible(False)
        self.mipMapsImageText.setVisible(False)
        self.sizeImageText.setVisible(False)

    def action_export_logic(self):

        # Save dds file
        dds_export_path = QFileDialog.getSaveFileName(self, "Save file", os.path.join(os.path.abspath(os.getcwd()),
                                                                                      textureNames[
                                                                                          current_selected_texture] +
                                                                                      ".dds"),
                                                      "DDS file (*.dds)")[0]
        if dds_export_path:
            file = open(dds_export_path, mode="wb")
            file.write(textures_data[current_selected_texture])
            file.close()

    @staticmethod
    def action_export_all_logic():

        # Create folder
        if not os.path.exists("textures"):
            os.mkdir("textures")
        name_folder = os.path.basename(vram_file_path_original).replace(".vram", "")
        dds_folder_export_path = os.path.join(os.path.abspath(os.getcwd()), "textures", name_folder)
        if not os.path.exists(dds_folder_export_path):
            os.mkdir(dds_folder_export_path)

        for i in range(0, sprp_struct.data_count):
            file = open(os.path.join(dds_folder_export_path, textureNames[i] + ".dds"), mode="wb")
            file.write(textures_data[i])
            file.close()

        msg = QMessageBox()
        msg.setWindowTitle("Message")
        msg.setText("All the textures were exported in %s." % dds_folder_export_path)
        msg.exec()

    def action_import_logic(self):

        # Open spr file
        dds_import_path = QFileDialog.getOpenFileName(self, "Open file",
                                                      os.path.join(os.path.abspath(os.getcwd()),
                                                                   textureNames[current_selected_texture] + ".dds"),
                                                      "DDS file (*.dds)")[0]
        if dds_import_path:
            with open(dds_import_path, mode="rb") as file:
                # Get the height and width of the modified image
                file.seek(12)
                height = int.from_bytes(file.read(bytes2Read), 'little')
                width = int.from_bytes(file.read(bytes2Read), 'little')
                # Get the dxtencoding
                file.seek(84)
                dxt_encoding = file.read(bytes2Read)
                # In the RGBA file, we got only 0x00 0x00 0x00 0x00, so we have to change the text
                if int.from_bytes(dxt_encoding, byteorder='big', signed=True) == 0:
                    dxt_encoding = "RGBA"
                else:
                    dxt_encoding = dxt_encoding.decode('utf-8')
                # Get all the data
                file.seek(0)
                data = file.read()

            # Get the tx2dinfo of the texture
            tx2d_info = tx2d_infos[current_selected_texture]
            dxt_encoding_original = get_dxt_byte(tx2d_info.dxt_encoding).decode("utf-8")
            # Check if the size of original and modified one are the same
            if tx2d_info.width != width or tx2d_info.height != height:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("The resolution for the modified file must be %dx%d\nYour file is %dx%d" % (
                    tx2d_info.width, tx2d_info.height, width, height))
                msg.exec()
            # The original and modified file must be in the same dxtencoding
            elif dxt_encoding_original != dxt_encoding:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("The encoding for the modified file must be in %s\nYour file is in %s" % (
                    dxt_encoding_original, dxt_encoding))
                msg.exec()
            # Can import the texture
            else:
                # Get the difference in size between original and modified in order to change the offsets
                len_data = len(data[128:])
                difference = len_data - tx2d_infos[current_selected_texture].data_size
                if difference != 0:
                    tx2d_infos[current_selected_texture].data_size = len_data
                    offset_quanty_difference[current_selected_texture] = difference

                # Change texture in the array
                textures_data[current_selected_texture] = data

                # Add the index texture that has been modified (if it was added before, we won't added twice)
                if current_selected_texture not in textures_index_edited:
                    textures_index_edited.append(current_selected_texture)

                try:
                    # Show texture in the program
                    img = read_dds_file(dds_import_path)

                    # Show the image
                    self.imageTexture.setPixmap(QPixmap.fromImage(img))
                except OSError:
                    self.imageTexture.clear()

    def action_open_logic(self):

        global spr_file_path_original, spr_file_path, vram_file_path_original, vram_file_path, current_selected_texture, character_file

        # Open spr file
        spr_file_path_original = \
            QFileDialog.getOpenFileName(self, "Open file", os.path.abspath(os.getcwd()), "SPR files (*.spr)")[0]
        # Check if the user has selected an spr format file
        if not os.path.exists(spr_file_path_original):
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("A spr file is needed.")
            msg.exec()
            return
        # Check if the user has selected an spr character file
        with open(spr_file_path_original, mode="rb") as spr_file:
            type_file = spr_file.read(4)
            spr_file.seek(20)
            type_file = (type_file + spr_file.read(1)).hex()
            if type_file == STPZ0:
                character_file = True

        # Open vram file
        vram_file_path_original = \
            QFileDialog.getOpenFileName(self, "Open file", os.path.abspath(os.getcwd()), "Texture files (*.vram)")[0]
        if not os.path.exists(vram_file_path_original):
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("A vram file is needed.")
            msg.exec()
            return

        # Clean the variables
        sprpDatasInfo.clear()
        textureNames.clear()
        tx2d_infos.clear()
        textures_data.clear()
        textures_index_edited.clear()

        # Convert spr and vram files if we're dealing with character file
        if character_file:
            # Create a folder where we store the necessary files or delete it. If already exists,
            # we remove every files in it
            if os.path.exists(temp_folder):
                rmtree(temp_folder, onerror=del_rw)
            os.mkdir(temp_folder)

            # Execute the script in a command line for the spr file
            basename = os.path.basename(spr_file_path_original)
            spr_file_path = os.path.join(os.path.abspath(os.getcwd()), temp_folder, basename.replace(".spr", "_u.spr"))
            args = os.path.join("lib",
                                "dbrb_compressor.exe") + " \"" + spr_file_path_original + "\" \"" + spr_file_path + "\""
            os.system('cmd /c ' + args)

            # Execute the script in a command line for the vram file
            basename = os.path.basename(vram_file_path_original)
            vram_file_path = os.path.join(os.path.abspath(os.getcwd()), temp_folder, basename.replace(".vram", "_u.vram"))
            args = os.path.join("lib",
                                "dbrb_compressor.exe") + " \"" + vram_file_path_original + "\" \"" + vram_file_path + "\""
            os.system('cmd /c ' + args)

            # Load the data from the files
            open_spr_file(spr_file_path, 16)
            open_vram_character_file(vram_file_path)

        # Generic spr file. Don't need to convert
        else:
            spr_file_path = spr_file_path_original
            vram_file_path = vram_file_path_original
            open_spr_file(spr_file_path, 12)
            open_vram_file(vram_file_path)


        # Add the names to the list view
        current_selected_texture = 0
        model = QStandardItemModel()
        self.listView.setModel(model)
        item_0 = QStandardItem(textureNames[0])
        model.appendRow(item_0)
        self.listView.setCurrentIndex(model.indexFromItem(item_0))
        for i in textureNames[1:]:
            item = QStandardItem(i)
            item.setEditable(False)
            model.appendRow(item)
        self.listView.clicked.connect(
            lambda q_model_idx: action_item(q_model_idx, self.imageTexture, self.encodingImageText,
                                            self.mipMapsImageText,
                                            self.sizeImageText))

        # Create the dds in disk and open it
        show_dds_image(self.imageTexture, textures_data[0])

        # Show the buttons
        self.exportButton.setVisible(True)
        self.exportAllButton.setVisible(True)
        self.importButton.setVisible(True)

        # Show the text labels
        self.encodingImageText.setText(
            "Encoding: %s" % (get_dxt_byte(tx2d_infos[current_selected_texture].dxt_encoding).decode('utf-8')))
        self.mipMapsImageText.setText("Mipmaps: %d" % tx2d_infos[current_selected_texture].mip_maps)
        self.sizeImageText.setText(
            "Resolution: %dx%d" % (tx2d_infos[current_selected_texture].width, tx2d_infos[current_selected_texture]
                                   .height))
        self.encodingImageText.setVisible(True)
        self.mipMapsImageText.setVisible(True)
        self.sizeImageText.setVisible(True)

    @staticmethod
    def action_save_logic():

        global spr_file_path_original, vram_file_path_original

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

            # Create the folder where we save the modified files
            basename = os.path.basename(vram_file_path_original) \
                .replace(".vram", datetime.now().strftime("_%d-%m-%Y_%H-%M-%S"))
            path_output_files = os.path.join(os.path.abspath(os.getcwd()), "outputs", basename)
            if not os.path.exists("outputs"):
                os.mkdir("outputs")
            os.mkdir(path_output_files)

            # Default paths
            spr_export_path = spr_file_path.replace(".spr", "_m.spr")
            vram_export_path = vram_file_path.replace(".vram", "_m.vram")

            # Sort the indexes of the modified textures
            textures_index_edited.sort()

            # Create a copy of the original file
            copyfile(spr_file_path, spr_export_path)

            # Update the offsets
            with open(spr_export_path, mode="rb+") as output_file_spr:
                first_index_texture_edited = textures_index_edited[0]
                # Move where the information starts to the first modified texture and change the size
                output_file_spr.seek(sprp_struct.data_base + sprpDatasInfo[first_index_texture_edited].data_offset + 12)
                output_file_spr.write(tx2d_infos[first_index_texture_edited].data_size.to_bytes(4, byteorder="big"))
                # Check if is the last texture modified and there is no more textures in the bottom
                if first_index_texture_edited + 1 < sprp_struct.data_count:
                    quanty_aux = int(offset_quanty_difference[first_index_texture_edited])
                    offset_quanty_difference[first_index_texture_edited] = 0
                    first_index_texture_edited += 1
                    for i in range(first_index_texture_edited, sprp_struct.data_count):

                        # Move where the information starts to the next textures
                        output_file_spr.seek(sprp_struct.data_base + sprpDatasInfo[i].data_offset + 4)
                        # Update the offset
                        tx2d_infos[i].data_offset += quanty_aux
                        output_file_spr.write(int(abs(tx2d_infos[i].data_offset)).to_bytes(4, byteorder="big"))
                        output_file_spr.seek(4, os.SEEK_CUR)

                        # Change the size only if they are differents.
                        # Because maybe is the same texture and don't need to modify
                        if tx2d_infos[i].data_size != tx2d_infos[i].data_size_old:
                            output_file_spr.write(tx2d_infos[i].data_size.to_bytes(4, byteorder="big"))

                        # Increment the difference only if the difference is not 0 and reset the offset differency array
                        if offset_quanty_difference[i] != 0:
                            quanty_aux += offset_quanty_difference[i]
                            offset_quanty_difference[i] = 0

            # replacing textures
            with open(vram_export_path, mode="wb") as output_file:
                with open(vram_file_path, mode="rb") as input_file:

                    # If we're dealing with a vram character file
                    if character_file:
                        # Move to the position 16, where it tells the offset of the file where the texture starts
                        data = input_file.read(16)
                        output_file.write(data)

                        data = input_file.read(bytes2Read)
                        output_file.write(data)
                        texture_offset = int.from_bytes(data, "big")
                    else:
                        texture_offset = 0

                    # Get each offset texture and write over the original file
                    for texture_index in textures_index_edited:
                        tx2d_info = tx2d_infos[texture_index]
                        data = input_file.read(abs(tx2d_info.data_offset_old + texture_offset - input_file.tell()))
                        output_file.write(data)
                        input_file.seek(tx2d_info.data_size_old, os.SEEK_CUR)
                        output_file.write(textures_data[texture_index][128:])

                    data = input_file.read()
                    output_file.write(data)

                    # Modify the bytes in pos 20 that indicates the size of the file
                    vram_file_size = abs(vram_file_size_old + output_file.tell() - input_file.tell())

            # Change the header of pos 256 in spr file because in that place indicates the size of the final output file
            with open(spr_export_path, mode="rb+") as output_file:
                output_file.seek(stpk_struct.data_offset + 48)
                output_file.write(vram_file_size.to_bytes(4, byteorder='big'))

            # If we're dealing with a vram character file
            if character_file:
                # Change the header of pos 20 in vram file because that place indicates the size of the final output file
                with open(vram_export_path, mode="rb+") as output_file:
                    output_file.seek(20)
                    output_file.write(vram_file_size.to_bytes(4, byteorder='big'))

                # Generate the final files for the game
                # Output for the spr file
                basename_spr = os.path.basename(spr_file_path_original)
                spr_file_path_modified = os.path.join(path_output_files, basename_spr)
                args = os.path.join("lib", "dbrb_compressor.exe") + " \"" + spr_export_path + "\" \"" \
                                                                    + spr_file_path_modified + "\""
                os.system('cmd /c ' + args)

                # Output for the vram file
                basename_vram = os.path.basename(vram_file_path_original)
                vram_file_path_modified = os.path.join(path_output_files, basename_vram)
                args = os.path.join("lib", "dbrb_compressor.exe") + " \"" + vram_export_path \
                                                                    + "\" \"" + vram_file_path_modified + "\" "
                os.system('cmd /c ' + args)

                # Remove the uncompressed modified files
                os.remove(spr_export_path)
                os.remove(vram_export_path)

            else:

                basename_spr = os.path.basename(spr_export_path).replace("_m.", ".")
                basename_vram = os.path.basename(vram_export_path).replace("_m.", ".")
                spr_file_path_modified = os.path.join(path_output_files, basename_spr)
                vram_file_path_modified = os.path.join(path_output_files, basename_vram)

                move(spr_export_path, spr_file_path_modified)
                move(vram_export_path, vram_file_path_modified)

            msg = QMessageBox()
            msg.setWindowTitle("Message")
            msg.setText("The files were saved and compressed in %s" % path_output_files)
            msg.exec()

    def closeEvent(self, event):
        if os.path.exists(temp_folder):
            rmtree(temp_folder, onerror=del_rw)
        event.accept()

    @staticmethod
    def action_author_logic():
        msg = QMessageBox()
        msg.setTextFormat(1)
        msg.setWindowTitle("Author")
        msg.setText(
            "RB2 character editor 1.3 by <a href=https://www.youtube.com/channel/UCkZajFypIgQL6mI6OZLEGXw>adsl13</a>")
        msg.exec()

    @staticmethod
    def action_credits_logic():
        msg = QMessageBox()
        msg.setTextFormat(1)
        msg.setWindowTitle("Credits")
        msg.setText(
            'To the Raging Blast Modding community and specially to revelation from <a '
            'href=https://forum.xentax.com>XeNTaX</a> forum who made the compress/uncompress tool.')
        msg.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
