import sys, requests
import os
import asyncio
import websockets
import threading
import pygetwindow as gw
import pyautogui
import cairosvg
import subprocess

from PIL import ImageGrab, Image
import numpy as np
import base64
from io import BytesIO

from PyQt6.QtWidgets import QApplication, QListWidgetItem, QLabel, QStyle, QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QSpacerItem, QLabel,QListWidget, QWidget, QPushButton, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt, QUrl, QFile, QTimer, QSize
from PyQt6.QtGui import QDesktopServices, QPainter,QColor,QBrush, QCursor, QPixmap, QImage
from PyQt6 import QtWidgets, QtCore, QtGui
from Custom_Widgets.Widgets import *
from ui_mainwindow import *

async def run_script():
    # Запуск другого Python файла с асинхронным кодом
    process = await asyncio.create_subprocess_exec(
        "python", "server.py",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

async def main():
    await run_script()

import json
Global_Email=""
Global_User=""
Global_ID = 0
Global_Friend_ID = ""
Global_Friend = ""

class RegAndLogFuncWin(QMainWindow):
    # Обработка нажатий мышкой
    def GeneralLoginEvents(self):
        # Установка лейблов как ссылок
        self.label_vk.setOpenExternalLinks(True)
        self.label_tg.setOpenExternalLinks(True)
        # Привязка события щелчка мыши к обработчику
        self.label_vk.mousePressEvent = lambda event: self.openUrl("https://vk.com/soiuzrussia")
        self.label_tg.mousePressEvent = lambda event: self.openUrl("https://t.me/souzrussia")
    # Открытие ссылок
    def openUrl(self, url):
        QDesktopServices.openUrl(QUrl(url))
    # Очистка
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clearLayout(sub_layout)
                        sub_layout.deleteLater()

class RegOrLogWin(RegAndLogFuncWin):
    def __init__(self):
        super().__init__()

        win = loadUi("LogOrReg.ui", self)
        self.GeneralLoginEvents()
        self.loginevents()
    # Различные события (в основном обработка нажатия) 
    def loginevents(self):
        self.reg_button.clicked.connect(lambda: self.openUrl("https://danissiimmo.github.io/souz/login.html#"))
        self.login_button.clicked.connect(self.login_button_clicked)
    # Обработка нажатия кнопки "Авторизация"
    def login_button_clicked(self):
        self.clearLayout(self.layout())
        log_win_widget = LogWin()
        self.setCentralWidget(log_win_widget)

class LogWin(RegAndLogFuncWin):
    def __init__(self):
        super().__init__()
        loadUi("Login.ui", self)
        self.GeneralLoginEvents()
        self.loginevents()
    # Различные события, обаботки нажатия и т.д.
    def loginevents(self):
        self.error_label.setVisible(False)
        #Ссылка на восстановление пароля
        self.forgot_label.setOpenExternalLinks(True)
        self.forgot_label.mousePressEvent = lambda event: self.openUrl("https://danissiimmo.github.io/souz/login.html#")
        # Возвращение к выбору авторизации или регистрации
        self.return_login_button.clicked.connect(self.return_button_clicked)
        # Кнопка "Войти"
        self.login_button.clicked.connect(self.login)
    # Обработка нажатия кнопки "Назад"
    def return_button_clicked(self):
        self.clearLayout(self.layout())
        log_win_widget = RegOrLogWin()
        self.setCentralWidget(log_win_widget)
    
    def login(self):
        global Global_Email, Global_User, Global_ID
        email = self.login_line.text().strip()
        password = self.pass_line.text().strip()
        if not email or not password:
            self.error_label.setVisible(True)
            if not email and not password:
                self.error_label.setText("* Пожалуйста, введите почту и пароль!")
            elif not email:
                self.error_label.setText("* Пожалуйста, введите вашу почту!")
            else:
                self.error_label.setText("* Пожалуйста, введите ваш пароль!")
            return
        else:
            self.error_label.setVisible(False)
        name = ""
        try:
            response = requests.post("http://26.248.111.145/mm.php", data={"email": email, "password": password})
            
            if response.status_code == 200:
                result = response.text
                if "success" in result:
                    Global_ID = int(result.split(":")[1])
                    Global_Email=email
                    Global_User = (result.split(":")[2])
                    self.clearLayout(self.layout())
                    main_win_widget = MainWin()
                    self.setCentralWidget(main_win_widget)
                    

                elif "user_not_found" in result :
                    self.error_label.setText("* Неправильная почта или пароль!")
                    self.error_label.setVisible(True)
                else:
                    self.error_label.setText("* Неожиданный ответ от сервер?!?")
                    self.error_label.setVisible(True)
            else:
                self.error_label.setText("* Не удалось подключиться к серверу!")
                self.error_label.setVisible(True)
        except requests.exceptions.RequestException as e:
            self.error_label.setText("* Не удалось подключиться к серверу!")
            self.error_label.setVisible(True)





class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Main.ui", self)
        self.repaint()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        loadJsonStyle(self, self.ui)
        self.ui.label_user.setText(Global_User)
        self.ui.add_friend_button.clicked.connect(self.openAddFriendWin)
        self.FriendsFunc()
        self.zayavki()
        self.ui.send_message.clicked.connect(self.SendMessage)
        self.ui.souzpl_button.clicked.connect(self.LOl)
        self.ui.new_demonstrasion_button.clicked.connect(self.OpenDemonstration)
        self.ui.load_demonstrasion_button.clicked.connect(self.OpenDemonstrationFriend)

    def SendMessage(self):
        message = self.ui.lineEdit_1.text().strip()
        if not message or not Global_Friend_ID:
            self.ui.lineEdit_1.clear()
            return

        response = requests.post("http://26.248.111.145/process_message.php", data={"userId": Global_ID, "message": message, "friendId": Global_Friend_ID})
        
        if response.status_code == 200:
            # Проверка успешности ответа от сервера
            response_data = response.json()
            if response_data.get("success") == True:
                self.message_with_friend(Global_Friend)
                # Очистка поля ввода
                self.ui.lineEdit_1.clear()
            else:
                print("Ошибка при отправке сообщения:", response_data.get("message", "Неизвестная ошибка"))
        else:
            print("Ошибка при отправке сообщения, статус код:", response.status_code)

    def FriendsFunc(self):
        try:
            # Отправляем POST-запрос на сервер
            response = requests.post("http://26.248.111.145/friendslist.php", data={"id": Global_ID})

            # Проверяем успешность запроса
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Проверяем наличие ключа 'friends' в данных
                    if 'friends' in data and data['friends'] is not None:

                        friends = data['friends']
                        ids = [friend['id'] for friend in friends]
                        
                        self.list_widget_friends = QListWidget()
                        self.list_widget_friends.setStyleSheet("""
                            QListWidget {
                                color: white;
                            }
                            QListWidget::item {
                                border-radius: 15px;
                            }
                            QListWidget::item:hover {
                                background-color: #393939;
                            }
                        """)
                        self.list_widget_friends.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                        self.ui.scrollArea.setWidget(self.list_widget_friends)
                        # Добавляем каждого пользователя в QListWidget
                        for user in ids:
                            if not (user == Global_ID or user == ""):
                                #print(user)
                                response2 = requests.post("http://26.248.111.145/name_and_mail.php", data={"userid": user})
                                data2 = response2.json()
                                #print(data2)
                                friend_id = user
                                user_name = data2["name"]
                                user_email = data2["email"]

                                custom_widget = CustomWidgetItem(self)
                                custom_widget.FriendFunc(user_name, friend_id, user_email, 1)
                                item = QListWidgetItem(self.list_widget_friends)
                                
                                
                                item.setSizeHint(custom_widget.sizeHint())
                                self.list_widget_friends.addItem(item)
                                self.list_widget_friends.setItemWidget(item, custom_widget)
                    else:
                        print("No friends data found in the response or it is null")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
            else:
                print(f"Error: Failed to retrieve data from the server. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
    def zayavki(self):
        self.list_widget_zayavki = QListWidget()
        self.list_widget_zayavki.setStyleSheet("""
            QListWidget {
                color: white;
            }
            QListWidget::item {
                height: 40px;
                border-radius: 15px;
            }
            QListWidget::item:hover {
                background-color: #393939;
            }
        """)
        self.list_widget_zayavki.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.scrollArea_2.setWidget(self.list_widget_zayavki)
        response = requests.post("http://26.248.111.145/chek_zayavki.php", data={"userid": Global_ID})
        data = response.json()
        if 'is_zayavki' in data:
            users = data["is_zayavki"]
            for user in users:
                # Исключаем текущего пользователя из списка
                if not (user == Global_ID or user == ""):
                    #print(user)
                    response2 = requests.post("http://26.248.111.145/name_and_mail.php", data={"userid": user})
                    data2 = response2.json()
                    #print(data2)
                    user_id = user
                    user_name = data2["name"]
                    user_email = data2["email"]
                    custom_widget = CustomWidgetItem(self)
                    custom_widget.ZayavkiFunc(user_name, user_id, user_email)
                    item = QListWidgetItem(self.list_widget_zayavki)
                    custom_widget.set_button_text("Принять")

                    custom_widget.button.clicked.connect(self.handle_button_click)
                    item.setSizeHint(custom_widget.sizeHint())
                    self.list_widget_zayavki.addItem(item)
                    self.list_widget_zayavki.setItemWidget(item, custom_widget)

    def handle_button_click(self):
        # Получаем указатель на объект, который инициировал событие
        button = self.sender()

        # Получаем указатель на родительский виджет (CustomWidgetItem)
        custom_widget = button.parent()

        # Получаем адрес электронной почты пользователя из свойства пользовательского виджета
        user_id = custom_widget.user_id()

        #print(Global_Email)
        #print(user_id)
        #print(Global_ID)
        
        requests.post("http://26.248.111.145/add2friend.php", data={"main_user_id": Global_ID, "s_user_id": user_id})
        self.zayavki()
        self.FriendsFunc()

    def message_with_friend(self, friendemail):
        self.list_widget_message = QListWidget()
        self.list_widget_message.setStyleSheet("""
            QListWidget {
                color: white;
            }
            QListWidget::item {
                height: 40px;
                border-radius: 15px;
            }
            QListWidget::item:hover {
                background-color: #393939;
            }
        """)
        self.list_widget_message.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ui.scrollArea_3.setWidget(self.list_widget_message)
        response = requests.post("http://26.248.111.145/load_messages.php", data={"email": Global_Email, "friendEmail": friendemail})
        
        if response.status_code == 200:            
            try:
                data = response.json()
                # Проверка наличия ключа 'messages'
                if  'messages' in data:
                    users = data["messages"]
                    for user in users:
                        userId = user["userId"]
                        #messageId = user["messageId"]
                        content = user["content"]
                        dateCreated = user["dateCreated"]

                        response2 = requests.post("http://26.248.111.145/name_and_mail.php", data={"userid": userId})
                        data2 = response2.json()
                        #print(data2)
                        username = data2["name"]
                        useremail = data2["email"]

                        custom_widget = CustomWidgetItem(self)
                        custom_widget.MessageFunc(username, userId, useremail, content, dateCreated)
                        item = QListWidgetItem(self.list_widget_message)
                        item.setSizeHint(custom_widget.sizeHint())
                        self.list_widget_message.addItem(item)
                        self.list_widget_message.setItemWidget(item, custom_widget)
                    self.list_widget_message.scrollToBottom()
                else:
                    print("No messages found or an error occurred.")
            except ValueError:
                print("Error parsing JSON")
        else:
            print(f"Failed to connect. Status code: {response.status_code}")

    def resizeEvent(self, event):
        
        # Вызываем базовую реализацию метода
        super().resizeEvent(event)
        try:
            self.ui.widget_bottom_right.setMinimumHeight(0)
        except RuntimeError:
            pass

    def OpenDemonstration(self):
        self.clearLayout(self.layout())
        main_win_widget = ScreenCaptureWindow("1")
        self.setCentralWidget(main_win_widget)

    def OpenDemonstrationFriend(self):
        self.clearLayout(self.layout())
        main_win_widget = ScreenCaptureWindow("0")
        self.setCentralWidget(main_win_widget)

    def openAddFriendWin(self):
        self.clearLayout(self.layout())
        main_win_widget = AddFriendWin()
        self.setCentralWidget(main_win_widget)
    #очистка    
    def clearLayout(self, layout):
        global Global_Friend_ID, Global_Friend
        Global_Friend_ID = ""
        Global_Friend = ""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clearLayout(sub_layout)
                        sub_layout.deleteLater()
    #проверка пользователя
    def LOl(self):
        #print(Global_ID)
        self.clearLayout(self.layout())
        log_win_widget = RegOrLogWin()
        self.setCentralWidget(log_win_widget)

class AddFriendWin(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        loadUi("AddFriend.ui", self)
        self.back_button.clicked.connect(self.goBack)
        self.parent = parent
        self.lineEdit.textChanged.connect(self.on_text_changed)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border-radius: 15px;
                color: white;
            }
            QListWidget::item {
                height: 40px;
                border-radius: 15px;
            }
            QListWidget::item:hover {
                background-color: #393939;
            }
            QListWidget::item:selected {
                color: white;
                background-color: #393939;
                border-radius: 15px;
                outline: 0px;
            }
            
        """)
        self.list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollArea.setWidget(self.list_widget)

    def on_text_changed(self):
        name = self.lineEdit.text().strip()
        self.list_widget.clear()

        if len(name) > 0:
            response = requests.post("http://26.248.111.145/search.php", data={"name": name})
            data = response.json()

            if 'users' in data:
                users = data["users"]
                for user in users:
                    user_id = int(user["id"])
                    user_name = user["name"]
                    user_email = user["email"]
                    
                    # Исключаем текущего пользователя из списка
                    if user_id is not Global_ID:
                        response1 = requests.post("http://26.248.111.145/check_friendship.php", data={"user_email": user_email, "userid": Global_ID})
                        data1 = response1.json()

                        custom_widget = CustomWidgetItem(self)
                        custom_widget.AddFriendWinFunc(user_name, user_id, user_email)
                        item = QListWidgetItem(self.list_widget)
                        
                        if data1["is_friend"]:
                            custom_widget.set_button_text("Удалить")
                        else:
                            custom_widget.set_button_text("Добавить")

                        custom_widget.button.clicked.connect(self.handle_button_click)
                        item.setSizeHint(custom_widget.sizeHint())
                        self.list_widget.addItem(item)
                        self.list_widget.setItemWidget(item, custom_widget)

    def handle_button_click(self):
        # Получаем указатель на объект, который инициировал событие
        button = self.sender()

        # Получаем указатель на родительский виджет (CustomWidgetItem)
        custom_widget = button.parent()

        # Получаем адрес электронной почты пользователя из свойства пользовательского виджета
        user_id = custom_widget.user_id()
        user_email = custom_widget.user_email()

        # Ваш код обработки нажатия кнопки
        # Например, вы можете выполнить запрос к серверу для добавления или удаления пользователя из друзей
        if custom_widget.button.text() == "Добавить":
            # Добавление пользователя в друзья
            #print(Global_Email)
            #print(user_id)
            #print(Global_ID)
            
            response = requests.post("http://26.248.111.145/add1friend.php", data={"main_user_id": Global_ID, "s_user_id": user_id})
            data1 = response.json()
            text1 = json.dumps(data1)
            #print(text1)
            self.on_text_changed()

            #print(response)
        else:
            # Удаление пользователя из друзей
            response = requests.post("http://26.248.111.145/remove_from_friends.php",data={"user_email": Global_Email, "friend_email": user_email, "userid": Global_ID})
            self.on_text_changed()

        # Обновление текста кнопки на пользовательском виджете в соответствии с результатом запроса
    #очистка
    def clearLayout(self, layout):
        global Global_Friend_ID, Global_Friend
        Global_Friend_ID = ""
        Global_Friend = ""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clearLayout(sub_layout)
                        sub_layout.deleteLater()

    def goBack(self):
        self.clearLayout(self.layout())
        main_win_widget = MainWin()
        self.setCentralWidget(main_win_widget)
   
class CustomWidgetItem(QWidget):
    def __init__(self, main_window, parent=None):
        self.main_window = main_window
        super().__init__(parent)
    
    def AddFriendWinFunc(self, username, userid, useremail):
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self._userid=userid
        self._useremail=useremail
        # Создаем QLabel для отображения имени пользователя
        self.label = QLabel(username)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #1D1D1D;
                border-radius: 15px;
                padding-left: 20px;
            }
        """)
        
        self.layout.addWidget(self.label)
        
        
        self.button = QPushButton("Добавить в друзья")  # Устанавливаем изначальный текст кнопки
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #4352ec;
                height: 30px;
                border-radius: 15px;
            }
        """)
        self.button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(self.button)
    
    def ZayavkiFunc(self, username, userid, useremail):
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self._userid=userid
        self._useremail=useremail
        # Создаем QLabel для отображения имени пользователя
        self.label = QLabel(username)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #1D1D1D;
                border-radius: 15px;
                padding-left: 10px;
            }
        """)
        self.layout.addWidget(self.label)
        
        
        self.button = QPushButton("Добавить")  # Устанавливаем изначальный текст кнопки
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #4352ec;
                height: 30px;
                border-radius: 15px;
            }
        """)
        self.button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(self.button)
    
    def MessageFunc(self, username, userId, useremail, content, dataCreated):

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        if (int(userId) == Global_ID):
            self.labelName = QLabel("Вы")
        else:
            self.labelName = QLabel(username)
        self.labelMessage = QLabel(content)
        self.labelDataCreated = QLabel(dataCreated)

        self.labelName.setStyleSheet("""
            QLabel {
                color: #4352ec;
                background-color: transparent;
            }
        """)
        self.labelMessage.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
            }
        """)
        self.labelDataCreated.setStyleSheet("""
            QLabel {
                color: #b5b5b5;
                background-color: transparent;
                font-size: 8px;
            }
        """)
        # горизонтальный layout для имени и даты
        self.nameDateLayout = QHBoxLayout()
        self.nameDateLayout.addWidget(self.labelName)
        self.nameDateLayout.addWidget(self.labelDataCreated)
        self.nameDateLayout.addStretch(1)  # Добавьте растяжку, чтобы сдвинуть надписи влево

        self.layout.addLayout(self.nameDateLayout)
        self.layout.addWidget(self.labelMessage)
        self.layout.addStretch(1)  # Add stretch to push everything to the top

        self.labelName.setAlignment(Qt.AlignLeft)
        self.labelMessage.setAlignment(Qt.AlignLeft)
        self.labelDataCreated.setAlignment(Qt.AlignBottom)

    def FriendFunc(self, username, friendid, friendemail, flag):
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = ClickableLabel(username)
        self.label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border-radius: 15px;
                height: 30px;
                padding: 10px;
            }
        """)

        self.layout.setContentsMargins(0, 0, 0, 0)  # Убедитесь, что нет внутренних отступов
        self.layout.setSpacing(0)  # Убедитесь, что нет промежутков между элементами
        

        self.label.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(self.label)
        if(flag):
            self.label.setCallback(lambda: self.labelClicked(friendid, friendemail))
        else:
            self.label.setCallback(lambda: self.labelClicked_D(friendid, friendemail))
    
    def labelClicked(self, friendid, friendemail):
        global Global_Friend_ID, Global_Friend
        self.main_window.message_with_friend(friendemail)
        Global_Friend_ID = friendid
        Global_Friend = friendemail

    def labelClicked_D(self, friendid, friendemail):
        global Global_Friend_ID, Global_Friend
        self.main_window.Iti()
        Global_Friend_ID = friendid
        Global_Friend = friendemail
    
    def user_email(self):
        return self._useremail

    def user_id(self):
        return self._userid # Метод для получения адреса электронной почты пользователя
        
    def set_button_text(self, text):
        # Метод для установки текста кнопки
        self.button.setText(text)

class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._callback = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._callback:
            self._callback() 

    def setCallback(self, callback):
        self._callback = callback

class ScreenCaptureWindow(QMainWindow):
    def __init__(self, new_or_load):
        super().__init__()
        loadUi("demonstrasion.ui", self)
        self.recording_enabled = False
        self.FriendsFunc()
        self.timer_interval = 30  # 1 frame per second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.grab_screen)

        self.websocket = None
        self.stop_event = threading.Event()

        if new_or_load == "1":
            self.websocket_thread = threading.Thread(target=self.start_websocket)
            self.websocket_thread.start()
            self.start_button.clicked.connect(self.toggle_recording_new)
        else:
            self.start_button.clicked.connect(self.toggle_recording_load)
        

        self.exit_button.clicked.connect(self.ReturnToMain)
    
    def Iti(self):
        print("1")
    
    def FriendsFunc(self):
        try:
            # Отправляем POST-запрос на сервер
            response = requests.post("http://26.248.111.145/friendslist.php", data={"id": Global_ID})

            # Проверяем успешность запроса
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Проверяем наличие ключа 'friends' в данных
                    if 'friends' in data and data['friends'] is not None:

                        friends = data['friends']
                        ids = [friend['id'] for friend in friends]
                        
                        self.list_widget_friends = QListWidget()
                        self.list_widget_friends.setStyleSheet("""
                            QListWidget {
                                color: white;
                            }
                            QListWidget::item {
                                border-radius: 15px;
                            }
                            QListWidget::item:hover {
                                background-color: #393939;
                            }
                        """)
                        self.list_widget_friends.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                        self.scrollArea.setWidget(self.list_widget_friends)
                        # Добавляем каждого пользователя в QListWidget
                        for user in ids:
                            if not (user == Global_ID or user == ""):
                                #print(user)
                                response2 = requests.post("http://26.248.111.145/name_and_mail.php", data={"userid": user})
                                data2 = response2.json()
                                #print(data2)
                                friend_id = user
                                user_name = data2["name"]
                                user_email = data2["email"]

                                custom_widget = CustomWidgetItem(self)
                                custom_widget.FriendFunc(user_name, friend_id, user_email, 0)
                                item = QListWidgetItem(self.list_widget_friends)
                                
                                
                                item.setSizeHint(custom_widget.sizeHint())
                                self.list_widget_friends.addItem(item)
                                self.list_widget_friends.setItemWidget(item, custom_widget)
                    else:
                        print("No friends data found in the response or it is null")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
            else:
                print(f"Error: Failed to retrieve data from the server. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def ReturnToMain(self):
        self.clearLayout(self.layout())
        main_win_widget = MainWin()
        self.setCentralWidget(main_win_widget)

    def grab_screen(self):
        if self.recording_enabled:
            screenshot_img = pyautogui.screenshot()
            buffered = BytesIO()
            screenshot_img.save(buffered, format="JPEG")
            screenshot_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            asyncio.run_coroutine_threadsafe(self.send_frame(screenshot_base64), self.loop)

            screenshot_qimage = QImage.fromData(base64.b64decode(screenshot_base64))
            self.update_frame(screenshot_qimage)

    async def send_frame(self, frame):
        if self.websocket:
            try:
                await self.websocket.send(frame)
                print("Frame sent")
            except websockets.ConnectionClosed:
                print("WebSocket connection closed")

    async def receive_frame(self):
        try:
            async for message in self.websocket:
                if self.stop_event.is_set():
                    break
                print("Frame received")
                screenshot_data = base64.b64decode(message)
                screenshot_qimage = QImage.fromData(screenshot_data)
                self.update_frame(screenshot_qimage)
        except websockets.ConnectionClosed:
            print("WebSocket connection closed")

    def update_frame(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        print("Frame updated on label")

    def toggle_recording_load(self):
        self.recording_enabled = not self.recording_enabled
        if self.recording_enabled:
            self.stop_event.clear()
            self.websocket_thread = threading.Thread(target=self.start_websocket)
            self.websocket_thread.start()
            self.start_button.setText("Выключить")
        else:
            self.stop_websocket()
            self.label.clear()
            self.start_button.setText("Включить")
    
    def toggle_recording_new(self):
        self.recording_enabled = not self.recording_enabled
        if self.recording_enabled:
            self.timer.start(self.timer_interval)
            self.start_button.setText("Закончить")
        else:
            self.timer.stop()
            self.label.clear()
            self.start_button.setText("Начать")

    def start_websocket(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())

    async def connect_to_server(self):
        await main()
        uri = "ws://26.248.111.145:8766"
        async with websockets.connect(uri) as websocket:
            self.websocket = websocket
            print("Connected to server")
            await self.receive_frame()

    def stop_websocket(self):
        self.stop_event.set()
        if self.websocket_thread is not None:
            self.websocket_thread.join()
            self.websocket_thread = None
        if self.websocket is not None:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)

    def clearLayout(self, layout):
        self.timer.stop()
        self.label.clear()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clearLayout(sub_layout)
                        sub_layout.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegOrLogWin()
    window.show()
    sys.exit(app.exec())