from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication

from mars_app.bootstrap import build_system
from mars_app.models import ProgressEvent
from mars_app.gui.windows import ClientWindow, ProcessWindow


@dataclass
class GuiResult:
    answer: str
    notes: list[str]


class RequestWorker(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)
    progress = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._system = None

    @pyqtSlot(str)
    def process_request(self, user_request: str) -> None:
        try:
            if self._system is None:
                self._system = build_system(progress_listener=self._publish_progress)
            result = self._system.handle(user_request)
            self.finished.emit(GuiResult(answer=result.content, notes=result.notes))
        except Exception as error:  # pragma: no cover - GUI runtime path
            self.failed.emit(str(error))

    def _publish_progress(self, event: ProgressEvent) -> None:
        self.progress.emit(event)


class MarsGuiController(QObject):
    request_submitted = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.client_window = ClientWindow()
        self.process_window = ProcessWindow()

        self.worker_thread = QThread()
        self.worker = RequestWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        self.client_window.send_requested.connect(self._submit_request)
        self.request_submitted.connect(self.worker.process_request)
        self.worker.progress.connect(self._handle_progress)
        self.worker.finished.connect(self._handle_result)
        self.worker.failed.connect(self._handle_error)

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.shutdown)

    def show(self) -> None:
        self.client_window.show()
        self.process_window.show()

    def shutdown(self) -> None:
        self.worker_thread.quit()
        self.worker_thread.wait(3000)

    def _submit_request(self, user_request: str) -> None:
        self.client_window.append_user_message(user_request)
        self.client_window.set_busy(True)
        self.process_window.append_event("=" * 70)
        self.process_window.append_event(f"[system] Новый пользовательский запрос\n{user_request}")
        self.request_submitted.emit(user_request)

    def _handle_progress(self, event: ProgressEvent) -> None:
        line = self._format_event(event)
        self.process_window.append_event(line)

    def _handle_result(self, result: GuiResult) -> None:
        self.client_window.append_assistant_message(result.answer)
        self.client_window.set_busy(False)

    def _handle_error(self, message: str) -> None:
        self.client_window.show_error(message)
        self.client_window.set_busy(False)
        self.process_window.append_event(f"[error] Ошибка выполнения\n{message}")

    def _format_event(self, event: ProgressEvent) -> str:
        header = f"[{event.level.upper()}][{event.stage}] {event.title}"
        return f"{header}\n{event.details}".strip()


def run_gui() -> None:
    app = QApplication.instance() or QApplication([])
    controller = MarsGuiController()
    controller.show()
    app.exec()
