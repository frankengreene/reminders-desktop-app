# gui.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QTextEdit, QDateTimeEdit, QComboBox, QColorDialog, QGroupBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDateTime
from database import Database
from scheduler import TaskScheduler
from datetime import datetime

# Stylesheets for Light and Dark themes
LIGHT_THEME = """
QWidget {
    background-color: #f0f0f0;
    color: #333333;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
QPushButton {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #45a049;
}
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dddddd;
}
QHeaderView::section {
    background-color: #4caf50;
    color: white;
    padding: 4px;
    border: 1px solid #dddddd;
}
"""

DARK_THEME = """
QWidget {
    background-color: #2c2f33;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
QPushButton {
    background-color: #7289da;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #5b6eae;
}
QTableWidget {
    background-color: #23272a;
    border: 1px solid #99aab5;
}
QHeaderView::section {
    background-color: #7289da;
    color: white;
    padding: 4px;
    border: 1px solid #99aab5;
}
"""

# Available themes
THEMES = {
    'Light': LIGHT_THEME,
    'Dark': DARK_THEME
}

class AddEditTaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task" if task is None else "Edit Task")
        self.task = task
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Task Title:")
        self.title_input = QLineEdit()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        # Description
        self.desc_label = QLabel("Description:")
        self.desc_input = QTextEdit()
        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_input)

        # Due Date
        self.due_label = QLabel("Due Date:")
        self.due_input = QDateTimeEdit()
        self.due_input.setCalendarPopup(True)
        self.due_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.due_input.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.due_label)
        layout.addWidget(self.due_input)

        # Reminder Time
        self.reminder_label = QLabel("Reminder Time:")
        self.reminder_input = QDateTimeEdit()
        self.reminder_input.setCalendarPopup(True)
        self.reminder_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.reminder_input.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.reminder_label)
        layout.addWidget(self.reminder_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # If editing, populate fields
        if self.task:
            self.title_input.setText(self.task['title'])
            self.desc_input.setPlainText(self.task['description'])
            due_dt = datetime.strptime(self.task['due_date'], '%Y-%m-%d %H:%M')
            reminder_dt = datetime.strptime(self.task['reminder_time'], '%Y-%m-%d %H:%M')
            self.due_input.setDateTime(QDateTime(due_dt))
            self.reminder_input.setDateTime(QDateTime(reminder_dt))

    def get_data(self):
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        due_date = self.due_input.dateTime().toString("yyyy-MM-dd HH:mm")
        reminder_time = self.reminder_input.dateTime().toString("yyyy-MM-dd HH:mm")
        return title, description, due_date, reminder_time

class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SkyWater Reminders")
        app_icon = QIcon("icon\SKYT.png")
        self.setWindowIcon(app_icon)
        self.resize(800, 600)

        self.db = Database()
        self.scheduler = TaskScheduler()

        self.current_theme = 'Light'  # Default theme
        self.init_ui()
        self.load_tasks()
        self.apply_theme(self.current_theme)

    def init_ui(self):
        layout = QVBoxLayout()

        # Theme Selector
        theme_group = QGroupBox("Customize Theme")
        theme_layout = QHBoxLayout()

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(THEMES.keys())
        self.theme_selector.currentIndexChanged.connect(self.change_theme)

        theme_layout.addWidget(QLabel("Select Theme:"))
        theme_layout.addWidget(self.theme_selector)
        theme_group.setLayout(theme_layout)

        layout.addWidget(theme_group)

        # Add Task Button
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.open_add_dialog)
        layout.addWidget(self.add_button)

        # Tasks Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Description", "Due Date", "Reminder Time", "Completed"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit Task")
        self.delete_button = QPushButton("Delete Task")
        self.complete_button = QPushButton("Mark as Completed")
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.complete_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.complete_button.clicked.connect(self.mark_completed)

    def apply_theme(self, theme_name):
        theme = THEMES.get(theme_name, THEMES['Light'])
        self.setStyleSheet(theme)

    def change_theme(self):
        self.current_theme = self.theme_selector.currentText()
        self.apply_theme(self.current_theme)

    def load_tasks(self):
        self.table.setRowCount(0)
        tasks = self.db.get_tasks()
        for task in tasks:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            id_item = QTableWidgetItem(str(task[0]))
            title_item = QTableWidgetItem(task[1])
            desc_item = QTableWidgetItem(task[2] if task[2] else "")
            due_item = QTableWidgetItem(task[3] if task[3] else "")
            reminder_item = QTableWidgetItem(task[4] if task[4] else "")
            completed_item = QTableWidgetItem("Yes" if task[5] else "No")

            # Center alignment for ID and Completed
            id_item.setTextAlignment(Qt.AlignCenter)
            completed_item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row_position, 0, id_item)
            self.table.setItem(row_position, 1, title_item)
            self.table.setItem(row_position, 2, desc_item)
            self.table.setItem(row_position, 3, due_item)
            self.table.setItem(row_position, 4, reminder_item)
            self.table.setItem(row_position, 5, completed_item)

            # Schedule reminder if not completed
            if not task[5] and task[4]:
                self.scheduler.schedule_task(task[0], task[1], task[4])

    def open_add_dialog(self):
        dialog = AddEditTaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, description, due_date, reminder_time = dialog.get_data()
            if not title:
                QMessageBox.warning(self, "Input Error", "Task title is required.")
                return
            # Validate date formats
            try:
                datetime.strptime(due_date, '%Y-%m-%d %H:%M')
                datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Incorrect date format. Please use YYYY-MM-DD HH:MM.")
                return
            self.db.add_task(title, description, due_date, reminder_time)
            task_id = self.db.conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            self.scheduler.schedule_task(task_id, title, reminder_time)
            self.load_tasks()

    def get_selected_task(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        task_id = int(self.table.item(selected, 0).text())
        task = self.db.conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        if task:
            return {
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'due_date': task[3],
                'reminder_time': task[4],
                'completed': task[5]
            }
        return None

    def edit_task(self):
        task = self.get_selected_task()
        if not task:
            QMessageBox.warning(self, "Selection Error", "No task selected.")
            return
        dialog = AddEditTaskDialog(self, task)
        if dialog.exec_() == QDialog.Accepted:
            title, description, due_date, reminder_time = dialog.get_data()
            if not title:
                QMessageBox.warning(self, "Input Error", "Task title is required.")
                return
            # Validate date formats
            try:
                datetime.strptime(due_date, '%Y-%m-%d %H:%M')
                datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Incorrect date format. Please use YYYY-MM-DD HH:MM.")
                return
            self.db.update_task(task['id'], title, description, due_date, reminder_time)
            self.scheduler.remove_task(task['id'])
            self.scheduler.schedule_task(task['id'], title, reminder_time)
            self.load_tasks()

    def delete_task(self):
        task = self.get_selected_task()
        if not task:
            QMessageBox.warning(self, "Selection Error", "No task selected.")
            return
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete the task: '{task['title']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_task(task['id'])
            self.scheduler.remove_task(task['id'])
            self.load_tasks()

    def mark_completed(self):
        task = self.get_selected_task()
        if not task:
            QMessageBox.warning(self, "Selection Error", "No task selected.")
            return
        if task['completed']:
            QMessageBox.information(self, "Info", "Task is already marked as completed.")
            return
        self.db.mark_completed(task['id'])
        self.scheduler.remove_task(task['id'])
        self.load_tasks()

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec_())
