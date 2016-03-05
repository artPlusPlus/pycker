import sys
import logging
import win32gui

from PySide.QtCore import *
from PySide.QtGui import *

from _session import Session
import _actions as actions

_LOG = logging.getLogger(__name__)
_DEFAULT_TARGET_WINDOW = 'Clicker Heroes'


class SessionThread(QThread):
    def __init__(self, parent=None):
        super(SessionThread, self).__init__(parent)

        tick_frequency = 1
        # duration = datetime.timedelta(seconds=60*5)
        duration = None
        optimal_level = 2100
        ruby_clickable = 'pie'
        skill_clickable = 'bumble_bee'
        attacks_per_second = 40
        auto_ascend = True
        auto_raid = True

        self._session = Session(
            tick_frequency=tick_frequency, optimal_level=optimal_level,
            ruby_clickable=ruby_clickable, skill_clickable=skill_clickable,
            attacks_per_second=attacks_per_second, auto_ascend=auto_ascend,
            auto_raid=auto_raid, duration=duration)

        # action = actions.update_static_ui_elements()
        # self._session.actions.append(action)

        action = actions.update_current_zone()
        self._session.actions.append(action)

        action = actions.idle()
        self._session.actions.append(action)

        action = actions.accept_discovered_relic()
        self._session.actions.append(action)

        action = actions.activate_clickables()
        self._session.actions.append(action)

        action = actions.activate_skills()
        self._session.actions.append(action)

        action = actions.update_hero()
        self._session.actions.append(action)

        action = actions.seek_hero()
        self._session.actions.append(action)

        action = actions.level_hero()
        self._session.actions.append(action)

        action = actions.attack_monster()
        self._session.actions.append(action)

        action = actions.attack_immortal()
        self._session.actions.append(action)

        action = actions.ascend()
        self._session.actions.append(action)

    def run(self):
        # profile = cProfile.Profile()
        # profile.enable()
        self._session.start()
        # profile.disable()
        # profile.print_stats()

    def handle_activation_changed(self, status):
        self._session.active = status

    def __del__(self):
        self._session.stop()
        self.wait()


class PyckerWidget(QMainWindow):
    activation_changed = Signal(bool)

    @property
    def _target_hwnd(self):
        return win32gui.FindWindow(None, self._target_window)

    @property
    def _target_rect(self):
        return win32gui.GetWindowRect(self._target_hwnd)

    @property
    def _target_size(self):
        return (
            self._target_rect[2] - self._target_rect[0],
            self._target_rect[3] - self._target_rect[1]
        )

    def __init__(self, target_window=None):
        super(PyckerWidget, self).__init__()

        self._target_window = target_window or _DEFAULT_TARGET_WINDOW
        self._active = False

        self._init_session()
        self._init_controls()
        self._init_layout()
        self._init_position()

    def _init_session(self):
        self._session = SessionThread(self)
        self.activation_changed.connect(self._session.handle_activation_changed,
                                        Qt.QueuedConnection)
        self._session.start()

    def _init_controls(self):
        self._status_button = QPushButton('Activate', self)
        self._status_button.clicked.connect(self._handle_status_button_clicked)

    def _init_layout(self):
        self._layout = QGridLayout()
        self._layout.setSpacing(2)

        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(0)
        self._status_button.setSizePolicy(size_policy)
        self._layout.addWidget(self._status_button, 5, 5)

        self.setLayout(self._layout)

    def _init_position(self):
        self._update_position_timer = QTimer(self)
        self._update_position_timer.timeout.connect(self._update_position)
        self._update_position_timer.start(100)

        self.resize(250, self.height())

        self._update_position()

    def _update_position(self):
        target_rect = self._target_rect

        self.setGeometry(target_rect[2], target_rect[1],
                         self.width(), target_rect[3] - target_rect[1])

    def _update_status_button(self):
        if self._active:
            self._status_button.setText('Deactivate')
        else:
            self._status_button.setText('Activate')

    def _handle_status_button_clicked(self):
        if self._active:
            self._deactivate()
        else:
            self._activate()

    def _activate(self):
        if self._active:
            return

        self._active = True

        self._update_status_button()

        self.activation_changed.emit(True)

    def _deactivate(self):
        if not self._active:
            return

        self._active = False

        self._update_status_button()

        self.activation_changed.emit(False)
        
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self._deactivate()
        super(PyckerWidget, self).keyPressEvent(e)


def _main():
    app = QApplication(sys.argv)

    widget = PyckerWidget()
    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    _main()
