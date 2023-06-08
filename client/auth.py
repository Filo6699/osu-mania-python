from PyQt6.QtWidgets import QWidget, QLabel, QMainWindow, QPushButton, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt
from client.network import Network
from pockets import LoginPocket


class AuthWindow(QMainWindow):
    def __init__(self, network: Network):
        super().__init__()

        self.net = network
        self.setWindowTitle("Login")
        self.resize(400, 200)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        for tedit in [self.username, self.password]:
            tedit.setFixedSize(300, 30)

        self.warning = QLabel()
        self.warning.setStyleSheet("color: red")
        self.warning.setText("Don't use your actual passwords. Even if you trust me")

        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        for tedit in [self.login_button, self.register_button]:
            tedit.setFixedSize(200, 30)

        layout = QVBoxLayout()
        for w in [
            self.username,
            self.password,
            self.warning,
            self.login_button,
            self.register_button,
        ]:
            layout.addWidget(w, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def wrong_auth_details(self):
        self.enable_buttons()
        self.username.setFocus()
        self.password.setText("")
        self.warning.setText("Wrong login or password.")

    def inputIsValid(self):
        login = self.username.text()
        pwd = self.password.text()

        llen = len(login)
        if llen < 4 or llen > 20:
            self.username.setFocus()
            self.warning.setText("Login must be 4-20 characters")
            return False

        llen = len(pwd)
        if llen < 4 or llen > 20:
            self.password.setFocus()
            self.warning.setText("Password must be 4-20 characters")
            return False

        return True

    def disable_buttons(self):
        self.login_button.setDisabled(1)
        self.register_button.setDisabled(1)

    def enable_buttons(self):
        self.login_button.setDisabled(0)
        self.register_button.setDisabled(0)

    def login(self):
        if not self.inputIsValid():
            return
        self.disable_buttons()

        login = self.username.text()
        pwd = self.password.text()
        if not self.net.send(LoginPocket(login, pwd)):
            self.warning.setText("Connection wasn't established. Try again in a bit")
            self.enable_buttons()
    
    def register(self):
        if not self.inputIsValid():
            return
        self.disable_buttons()
