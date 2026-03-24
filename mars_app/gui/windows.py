from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class ClientWindow(QMainWindow):
    send_requested = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MARS Client Console")
        self.resize(760, 620)

        root = QWidget()
        layout = QVBoxLayout(root)

        self.status_label = QLabel("Система готова к запросам.")
        self.status_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.status_label)

        self.dialog_view = QPlainTextEdit()
        self.dialog_view.setReadOnly(True)
        self.dialog_view.setFont(QFont("Consolas", 10))
        layout.addWidget(self.dialog_view, stretch=1)

        input_label = QLabel("Введите запрос")
        layout.addWidget(input_label)

        self.input_box = QPlainTextEdit()
        self.input_box.setPlaceholderText("Опишите задачу для системы...")
        self.input_box.setMaximumBlockCount(200)
        self.input_box.setFixedHeight(120)
        layout.addWidget(self.input_box)

        button_row = QHBoxLayout()
        self.send_button = QPushButton("Отправить")
        self.clear_button = QPushButton("Очистить диалог")
        button_row.addWidget(self.send_button)
        button_row.addWidget(self.clear_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self.setCentralWidget(root)

        self.send_button.clicked.connect(self._emit_request)
        self.clear_button.clicked.connect(self.dialog_view.clear)

    def append_user_message(self, message: str) -> None:
        self._append_block("Пользователь", message)

    def append_assistant_message(self, message: str) -> None:
        self._append_block("MARS", message)

    def append_note_message(self, notes: list[str]) -> None:
        if not notes:
            return
        self._append_block("Заметки", "\n".join(f"- {note}" for note in notes))

    def set_busy(self, busy: bool) -> None:
        self.send_button.setDisabled(busy)
        self.input_box.setDisabled(busy)
        self.status_label.setText("Система обрабатывает запрос..." if busy else "Система готова к запросам.")

    def show_error(self, message: str) -> None:
        self._append_block("Ошибка", message)
        self.status_label.setText("Во время обработки произошла ошибка.")

    def _emit_request(self) -> None:
        text = self.input_box.toPlainText().strip()
        if not text:
            return
        self.input_box.clear()
        self.send_requested.emit(text)

    def _append_block(self, title: str, message: str) -> None:
        current = self.dialog_view.toPlainText().strip()
        block = f"[{title}]\n{message.strip()}"
        new_text = f"{current}\n\n{block}" if current else block
        self.dialog_view.setPlainText(new_text)
        self.dialog_view.verticalScrollBar().setValue(self.dialog_view.verticalScrollBar().maximum())


class ProcessWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MARS Process Console")
        self.resize(760, 620)

        root = QWidget()
        layout = QVBoxLayout(root)

        title = QLabel("Трассировка выполнения")
        title.setStyleSheet("font-weight: 600;")
        layout.addWidget(title)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_view, stretch=1)

        self.clear_button = QPushButton("Очистить лог")
        layout.addWidget(self.clear_button)

        self.setCentralWidget(root)

        self.clear_button.clicked.connect(self.log_view.clear)

    def append_event(self, line: str) -> None:
        current = self.log_view.toPlainText().strip()
        new_text = f"{current}\n{line}" if current else line
        self.log_view.setPlainText(new_text)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())
