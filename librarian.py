# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 15:52:44 2023

@author: sadeghi.a
"""
import os
import sys
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QCheckBox, QProgressBar, QMessageBox
from PyQt5.QtCore import QTimer, Qt

class FileSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.folder_path = None  # Initialize folder_path
        self.destination_folder = None
        self.progress_update_timer = QTimer(self)
        self.progress_update_timer.timeout.connect(self.update_progress)
        self.search_progress = 0
        self.move_progress = 0

    def initUI(self):
        self.setWindowTitle('File Search and Move')
        self.setGeometry(100, 100, 800, 600)

        # Create widgets
        self.search_folder_button = QPushButton('Select Folder')
        self.search_folder_button.clicked.connect(self.select_folder)
        self.search_text_label = QLabel('Search Text:')
        self.search_text_edit = QLineEdit()
        self.search_text_edit.returnPressed.connect(self.search_files_enter)
        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.search_files)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Select", "File", "Path", ""])
        self.select_all_checkbox = QCheckBox('Select All')
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        self.move_button = QPushButton('Move Selected Files')
        self.move_button.clicked.connect(self.move_selected_files)
        self.move_button.setEnabled(False)  # Initially disabled

        # Create a progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)  # Center-align the percentage text

        # Create a button to select the destination folder
        self.select_dest_folder_button = QPushButton('Select Destination Folder')
        self.select_dest_folder_button.clicked.connect(self.select_destination_folder)

        # Layout setup
        main_layout = QVBoxLayout()

        # Top controls layout
        top_controls_layout = QHBoxLayout()
        top_controls_layout.addWidget(self.search_folder_button)
        top_controls_layout.addWidget(self.search_text_label)
        top_controls_layout.addWidget(self.search_text_edit)
        top_controls_layout.addWidget(self.search_button)

        main_layout.addLayout(top_controls_layout)
        main_layout.addWidget(self.table_widget)

        # Bottom controls layout
        bottom_controls_layout = QHBoxLayout()
        bottom_controls_layout.addWidget(self.select_all_checkbox)
        bottom_controls_layout.addWidget(self.select_dest_folder_button)
        bottom_controls_layout.addWidget(self.move_button)

        main_layout.addLayout(bottom_controls_layout)
        main_layout.addWidget(self.progress_bar)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize variables
        self.selected_files = []

        # Connect itemChanged signal to rename files
        self.table_widget.itemChanged.connect(self.on_table_item_changed)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder:
            self.folder_path = folder  # Set folder_path
            self.search_folder_button.setText(folder)
            self.move_button.setEnabled(True)  # Enable the "Move" button

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if folder:
            self.destination_folder = folder

    def search_files(self):
        self.selected_files = []  # Clear previous selections
        self.table_widget.setRowCount(0)  # Clear previous search results

        search_text = self.search_text_edit.text().lower()  # Convert search text to lowercase
        if not search_text:
            return

        if not self.folder_path or not os.path.exists(self.folder_path):
            self.show_message("Please select the source folder first.")  # Notify if source folder not selected
            return

        # Get the total number of files for progress bar
        total_files = sum(len(files) for root, _, files in os.walk(self.folder_path))
        processed_files = 0  # To keep track of processed files

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if search_text in file.lower():  # Perform case-insensitive search
                    file_path = os.path.join(root, file)
                    row_position = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_position)
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)
                    self.table_widget.setCellWidget(row_position, 0, checkbox)  # Add checkbox
                    self.table_widget.setItem(row_position, 1, QTableWidgetItem(file))
                    self.table_widget.setItem(row_position, 2, QTableWidgetItem(file_path))
                    self.selected_files.append(file_path)

                # Update the progress bar for searching
                processed_files += 1
                progress_percentage = (processed_files / total_files) * 100
                self.search_progress = progress_percentage
                self.update_progress(self.search_progress)

        # Set the progress bar to green after searching is complete
        self.update_progress(100, is_searching=True)

    def search_files_enter(self):
        # This function is triggered when Enter key is pressed in the search text field
        self.search_files()

    def move_selected_files(self):
        if not self.selected_files or not self.destination_folder:
            return

        # Get the total number of files for progress bar
        total_files = len(self.selected_files)
        processed_files = 0  # To keep track of processed files

        for row in range(self.table_widget.rowCount()):
            checkbox_item = self.table_widget.cellWidget(row, 0)
            if checkbox_item.isChecked():
                file_path = self.selected_files[row]
                file_name = os.path.basename(file_path)
                destination_path = os.path.join(self.destination_folder, file_name)
                try:
                    shutil.move(file_path, destination_path)
                    self.selected_files[row] = destination_path  # Update the file path
                except Exception as e:
                    print(f"Error moving file '{file_path}' to '{destination_path}': {str(e)}")

                # Update the progress information for moving
                processed_files += 1
                progress_percentage = (processed_files / total_files) * 100
                self.move_progress = progress_percentage
                self.update_progress(self.move_progress, is_searching=False)

        # Clear the table and selected files
        self.table_widget.setRowCount(0)
        self.selected_files = []

        # Set the progress bar to red after moving is complete
        self.update_progress(100, is_searching=False)

    def toggle_select_all(self):
        # Toggle the selection of all checkboxes
        select_all = self.select_all_checkbox.isChecked()
        for row in range(self.table_widget.rowCount()):
            checkbox_item = self.table_widget.cellWidget(row, 0)
            checkbox_item.setChecked(select_all)

    def show_message(self, message):
        # Show a message dialog with the given message
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Message')
        msg_box.setText(message)
        msg_box.exec_()

    def update_progress(self, value, is_searching=True):
        self.progress_bar.setValue(int(value))
        if is_searching:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; color: white; }")
        else:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; color: white; }")

    def rename_file(self, row):
        if row >= 0 and row < self.table_widget.rowCount():
            new_file_name = self.table_widget.item(row, 1).text()
            file_path = self.selected_files[row]
            
            if os.path.exists(file_path):
                try:
                    # Rename the file
                    file_dir = os.path.dirname(file_path)
                    new_file_path = os.path.join(file_dir, new_file_name)
                    os.rename(file_path, new_file_path)
                    self.selected_files[row] = new_file_path
                except Exception as e:
                    print(f"Error renaming file '{file_path}' to '{new_file_name}': {str(e)}")

    def on_table_item_changed(self, item):
        if item.column() == 1:  # Check if the changed item is in the "File" column
            row = item.row()
            self.rename_file(row)

def main():
    app = QApplication(sys.argv)
    window = FileSearchApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
