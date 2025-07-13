import sys
import os
import shutil
from PySide6.QtWidgets import (QMainWindow, QApplication, QWidget, QHBoxLayout, QVBoxLayout,
                               QPushButton, QTextEdit, QLineEdit, QStackedWidget, QMessageBox,
                               QScrollArea, QFormLayout, QLabel, QFileDialog)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPainterPath
from PySide6.QtCore import Qt, QSize, Signal

from Database import (ezafe_kardan_karbar, barresi_vorood, beroozresani_karbar,
                      peida_kardan_mokhatab, namayesh_karbar, MASIR_ASLI_BARNAMEH, MASIR_AKS_PROFILE)


class LabelGerde(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setScaledContents(True)

    def setPixmap(self, ax):
        ax_gerd = self.gerdKardaneAks(ax)
        super().setPixmap(ax_gerd)

    def gerdKardaneAks(self, ax):
        if ax.isNull():
            return QPixmap()

        size = min(ax.width(), ax.height())
        ax_gerd = QPixmap(size, size)
        ax_gerd.fill(Qt.GlobalColor.transparent)

        painter = QPainter(ax_gerd)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        ax_scaled = ax.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                              Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(0, 0, ax_scaled)
        painter.end()

        return ax_gerd


class LabelGerdeGhabeleClick(LabelGerde):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class WidgetPasZamine(QWidget):
    def __init__(self, masire_aks, parent=None):
        super().__init__(parent)
        self.ax = QPixmap(masire_aks)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.ax.isNull():
            ax_scaled = self.ax.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                       Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(self.rect(), ax_scaled)


class PanjarehAsli(QMainWindow):
    login_movafagh = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PayamResan")
        self.resize(450, 550)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.safheha = [Vorood(self.avazKardaneSafhe),
                        SabtNam(self.avazKardaneSafhe),
                        PayamResan(self.avazKardaneSafhe)]
        for safhe in self.safheha:
            self.stack.addWidget(safhe)
        self.stack.setCurrentIndex(0)

    def avazKardaneSafhe(self, index, username=None):
        if index == 2:
            self.resize(1000, 700)
            if username:
                safhe_payamresan = self.safheha[2]
                safhe_payamresan.tanzimKarbarFeli(username)
                self.login_movafagh.emit(username)
        else:
            self.resize(450, 550)
        self.stack.setCurrentIndex(index)


class Vorood(WidgetPasZamine):
    def __init__(self, callback_avaz_kardane_safhe):
        super().__init__(os.path.join(MASIR_ASLI_BARNAMEH, "lntro.jpg"))
        self.callback_avaz_kardane_safhe = callback_avaz_kardane_safhe

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Username')

        self.password = QLineEdit(self)
        self.password.setPlaceholderText('Password')
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        dokme_vorood = QPushButton('Sign In', self)
        dokme_vorood.clicked.connect(self.voroodBeHesab)

        dokme_sabtnam = QPushButton('Go to Sign Up', self)
        dokme_sabtnam.clicked.connect(lambda: self.callback_avaz_kardane_safhe(1))

        layout_dokmeha = QHBoxLayout()
        layout_dokmeha.addWidget(dokme_vorood)
        layout_dokmeha.addWidget(dokme_sabtnam)

        layout_asli = QVBoxLayout()
        layout_asli.addStretch()
        layout_asli.addWidget(self.username)
        layout_asli.addWidget(self.password)
        layout_asli.addLayout(layout_dokmeha)
        layout_asli.addStretch()

        self.setLayout(layout_asli)

    def voroodBeHesab(self):
        username = self.username.text()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        if barresi_vorood(user_name=username, password=password):
            self.callback_avaz_kardane_safhe(2, username)
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")


class SabtNam(WidgetPasZamine):
    def __init__(self, callback_avaz_kardane_safhe):
        super().__init__(os.path.join(MASIR_ASLI_BARNAMEH, "lntro.jpg"))
        self.callback_avaz_kardane_safhe = callback_avaz_kardane_safhe

        self.shomare_telefon = QLineEdit(self)
        self.shomare_telefon.setPlaceholderText('Phone Number')

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Username')

        self.password = QLineEdit(self)
        self.password.setPlaceholderText('Password')
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.takrar_password = QLineEdit(self)
        self.takrar_password.setPlaceholderText('Confirm Password')
        self.takrar_password.setEchoMode(QLineEdit.EchoMode.Password)

        dokme_sabtnam = QPushButton('Sign Up', self)
        dokme_sabtnam.clicked.connect(self.sabtNamKarbar)

        dokme_vorood = QPushButton('Go to Sign In', self)
        dokme_vorood.clicked.connect(lambda: self.callback_avaz_kardane_safhe(0))

        layout_dokmeha = QHBoxLayout()
        layout_dokmeha.addWidget(dokme_sabtnam)
        layout_dokmeha.addWidget(dokme_vorood)

        layout_asli = QVBoxLayout()
        layout_asli.addStretch()
        layout_asli.addWidget(self.shomare_telefon)
        layout_asli.addWidget(self.username)
        layout_asli.addWidget(self.password)
        layout_asli.addWidget(self.takrar_password)
        layout_asli.addLayout(layout_dokmeha)
        layout_asli.addStretch()

        self.setLayout(layout_asli)

    def sabtNamKarbar(self):
        phone = self.shomare_telefon.text()
        username = self.username.text()
        password = self.password.text()
        confirm_password = self.takrar_password.text()

        if not all([phone, username, password, confirm_password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        natije = ezafe_kardan_karbar(user_name=username, phone=phone, password=password)

        if natije == "Success":
            QMessageBox.information(self, "Success", "Account created successfully! Please sign in.")
            self.callback_avaz_kardane_safhe(0)
        else:
            QMessageBox.critical(self, "Error", natije)


class PayamResan(WidgetPasZamine):
    darkhaste_ersale_payam = Signal(str, str)

    def __init__(self, callback_avaz_kardane_safhe):
        super().__init__(os.path.join(MASIR_ASLI_BARNAMEH, "back3.jpg"))
        self.callback_avaz_kardane_safhe = callback_avaz_kardane_safhe
        self.karbar_feli = None
        self.mokhatabin_ezafe_shode = set()
        self.chat_faal_ba = None

        layout_koli = QHBoxLayout(self)
        layout_koli.setContentsMargins(0, 0, 0, 0)
        layout_koli.setSpacing(0)
        widget_kenari = self.sakhteNawareKenari()
        layout_koli.addWidget(widget_kenari)
        widget_asli = self.sakhteBakhsheAsli()
        layout_koli.addWidget(widget_asli)

    def tanzimKarbarFeli(self, username):
        self.karbar_feli = username
        self.beroozresaniNamayesheProfil()

    def beroozresaniNamayesheProfil(self):
        if not self.karbar_feli:
            return
        data_karbar = namayesh_karbar(self.karbar_feli)
        if data_karbar:
            self.dokme_profil.setText(data_karbar.user_name)
            ax = QPixmap(data_karbar.profile_image)
            self.label_aks_profil.setPixmap(ax)

    def sakhteNawareKenari(self):
        widget_kenari = QWidget()
        widget_kenari.setFixedWidth(250)
        widget_kenari.setStyleSheet("background-color: #111B21;")
        layout_kenari = QVBoxLayout(widget_kenari)
        layout_kenari.setContentsMargins(10, 10, 10, 10)
        layout_kenari.setSpacing(10)

        widget_sarbar = QWidget()
        layout_sarbar = QHBoxLayout(widget_sarbar)
        layout_sarbar.setContentsMargins(0, 0, 0, 0)

        self.label_aks_profil = LabelGerde()
        self.dokme_profil = QPushButton()
        self.dokme_profil.setStyleSheet(
            "color: white; border: none; font-size: 16px; font-weight: bold; text-align: left; padding-left: 5px;")
        self.dokme_profil.clicked.connect(self.namayesheProfileKarbar)

        layout_sarbar.addWidget(self.label_aks_profil)
        layout_sarbar.addWidget(self.dokme_profil)
        layout_sarbar.addStretch()

        dokme_mokhatabin = QPushButton()
        dokme_mokhatabin.setIcon(QIcon(os.path.join(MASIR_ASLI_BARNAMEH, "Contact.png")))
        dokme_mokhatabin.setIconSize(QSize(40, 40))
        dokme_mokhatabin.setFixedSize(50, 50)
        dokme_mokhatabin.setStyleSheet("border: none; cursor: pointer;")
        dokme_mokhatabin.clicked.connect(self.clickRoyeMokhatabin)

        dokme_tanzimat = QPushButton()
        dokme_tanzimat.setIcon(QIcon(os.path.join(MASIR_ASLI_BARNAMEH, "setting.png")))
        dokme_tanzimat.setIconSize(QSize(40, 40))
        dokme_tanzimat.setFixedSize(50, 50)
        dokme_tanzimat.setStyleSheet("border: none; cursor: pointer;")
        dokme_tanzimat.clicked.connect(self.clickRoyeTanzimat)

        layout_sarbar.addWidget(dokme_mokhatabin)
        layout_sarbar.addWidget(dokme_tanzimat)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        self.mohtavaye_mokhatabin = QWidget()
        self.layout_mokhatabin = QVBoxLayout(self.mohtavaye_mokhatabin)
        self.layout_mokhatabin.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_mokhatabin.setContentsMargins(0, 0, 0, 0)
        self.layout_mokhatabin.setSpacing(1)
        self.scroll_area.setWidget(self.mohtavaye_mokhatabin)

        layout_kenari.addWidget(widget_sarbar)
        layout_kenari.addWidget(self.scroll_area)
        return widget_kenari

    def sakhteBakhsheAsli(self):
        widget_asli = QWidget()
        layout_asli = QVBoxLayout(widget_asli)
        layout_asli.setContentsMargins(0, 0, 0, 0)
        layout_asli.setSpacing(0)
        sarbar_chat = QWidget()
        sarbar_chat.setFixedHeight(59)
        sarbar_chat.setStyleSheet("background-color: #202C33; padding-left: 15px;")
        layout_sarbar_chat = QHBoxLayout(sarbar_chat)
        self.label_esm_mokhatab = QLabel("Select a contact to start chatting")
        self.label_esm_mokhatab.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout_sarbar_chat.addWidget(self.label_esm_mokhatab)
        layout_asli.addWidget(sarbar_chat)
        self.namayeshgar_chat = QTextEdit()
        self.namayeshgar_chat.setReadOnly(True)
        self.namayeshgar_chat.setStyleSheet(
            "background-color: transparent; color: white; font-size: 14px; border: none;")
        paszamine_chat = WidgetPasZamine(os.path.join(MASIR_ASLI_BARNAMEH, 'back3.jpg'))
        layout_paszamine_chat = QVBoxLayout(paszamine_chat)
        layout_paszamine_chat.addWidget(self.namayeshgar_chat)
        layout_asli.addWidget(paszamine_chat)
        widget_naware_voroodi = QWidget()
        widget_naware_voroodi.setFixedHeight(62)
        widget_naware_voroodi.setStyleSheet("background-color: #202C33;")
        layout_naware_voroodi = QHBoxLayout(widget_naware_voroodi)
        self.matne_payam = QLineEdit()
        self.matne_payam.setPlaceholderText("Type a message...")
        self.matne_payam.setStyleSheet(
            "QLineEdit { background-color: #2A3942; color: #E9EDEF; border-radius: 8px; padding: 10px; font-size: 14px; }")
        dokme_ersal = QPushButton("Send")
        dokme_ersal.setFixedWidth(80)
        dokme_ersal.setStyleSheet(
            "QPushButton { background-color: #00A884; color: white; border-radius: 8px; padding: 10px; font-weight: bold; } QPushButton:hover { background-color: #008a6b; }")
        dokme_ersal.clicked.connect(self.ersalePayam)
        self.matne_payam.returnPressed.connect(self.ersalePayam)
        layout_naware_voroodi.addWidget(self.matne_payam)
        layout_naware_voroodi.addWidget(dokme_ersal)
        layout_asli.addWidget(widget_naware_voroodi)
        return widget_asli

    def ersalePayam(self):
        if not self.chat_faal_ba:
            QMessageBox.warning(self, "No Chat Selected", "Please select a contact to send a message.")
            return
        payam = self.matne_payam.text().strip()
        if payam:
            self.namayeshgar_chat.append(f"<p style='text-align: right; color: #dcf8c6;'><b>You</b>: {payam}</p>")
            self.darkhaste_ersale_payam.emit(self.chat_faal_ba, payam)
            self.matne_payam.clear()

    def namayeshePayameVoroodi(self, ferestande, mohtava):
        if ferestande == self.chat_faal_ba:
            self.namayeshgar_chat.append(f"<p style='color: #ffffff;'><b>{ferestande}</b>: {mohtava}</p>")

    def bazKardaneChatBa(self, username):
        self.chat_faal_ba = username
        self.label_esm_mokhatab.setText(username)
        self.namayeshgar_chat.clear()

    def ezafeKardaneMokhatab(self):
        username = self.voroodi_username_mokhatab.text()
        phone = self.voroodi_shomare_mokhatab.text()
        if not username or not phone:
            QMessageBox.warning(self.panjare_mokhatabin, "Error", "Please fill in all fields.")
            return

        mokhatab_yaft_shode = peida_kardan_mokhatab(username, phone)
        if not mokhatab_yaft_shode:
            QMessageBox.warning(self.panjare_mokhatabin, "Not Found",
                                "No user found with this username and phone number.")
            return

        unique_id, esme_namayeshi = (
            ("__SAVED_MESSAGES__", "Saved Messages") if mokhatab_yaft_shode.user_name == self.karbar_feli
            else (mokhatab_yaft_shode.user_name, mokhatab_yaft_shode.user_name))

        if unique_id in self.mokhatabin_ezafe_shode:
            QMessageBox.warning(self.panjare_mokhatabin, "Already Added",
                                f"'{esme_namayeshi}' is already in your contact list.")
            return

        widget_mokhatab = QWidget()
        layout_mokhatab = QHBoxLayout(widget_mokhatab)
        layout_mokhatab.setContentsMargins(5, 5, 5, 5)

        label_aks_mokhatab = LabelGerdeGhabeleClick()
        ax = QPixmap(mokhatab_yaft_shode.profile_image)
        label_aks_mokhatab.setPixmap(ax)
        label_aks_mokhatab.clicked.connect(
            lambda uname=mokhatab_yaft_shode.user_name: self.namayesheProfileMokhatab(uname))

        dokme_mokhatab = QPushButton(esme_namayeshi)
        dokme_mokhatab.setStyleSheet(
            "QPushButton { background-color: transparent; color: #E9EDEF; border: none; padding: 10px; text-align: left; font-size: 14px; }")
        dokme_mokhatab.clicked.connect(lambda checked, uname=unique_id: self.bazKardaneChatBa(uname))

        layout_mokhatab.addWidget(label_aks_mokhatab)
        layout_mokhatab.addWidget(dokme_mokhatab)
        layout_mokhatab.addStretch()

        widget_mokhatab.setStyleSheet("QWidget:hover { background-color: #2A3942; }")

        self.layout_mokhatabin.addWidget(widget_mokhatab)
        self.mokhatabin_ezafe_shode.add(unique_id)
        QMessageBox.information(self.panjare_mokhatabin, "Success", f"'{esme_namayeshi}' was added.")
        self.panjare_mokhatabin.close()

    def clickRoyeMokhatabin(self):
        self.panjare_mokhatabin = WidgetPasZamine(os.path.join(MASIR_ASLI_BARNAMEH, 'back5.jpg'))
        self.panjare_mokhatabin.setWindowTitle("Add Contact")
        self.panjare_mokhatabin.setGeometry(200, 200, 350, 200)
        self.panjare_mokhatabin.setStyleSheet("""
            QLabel { color: white; font-size: 14px; }
            QLineEdit { background-color: rgba(42, 57, 66, 0.8); color: #E9EDEF; border-radius: 8px; padding: 10px; border: 1px solid #37444C;}
            QPushButton { background-color: #00A884; color: white; border-radius: 8px; padding: 10px; font-weight: bold; }
        """)
        self.voroodi_username_mokhatab = QLineEdit()
        self.voroodi_shomare_mokhatab = QLineEdit()
        dokme_ezafe_kardan = QPushButton("Add Contact")
        dokme_ezafe_kardan.clicked.connect(self.ezafeKardaneMokhatab)
        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.voroodi_username_mokhatab)
        form_layout.addRow("Phone Number:", self.voroodi_shomare_mokhatab)
        layout_asli = QVBoxLayout(self.panjare_mokhatabin)
        layout_asli.addLayout(form_layout)
        layout_asli.addWidget(dokme_ezafe_kardan)
        layout_asli.addStretch()
        self.panjare_mokhatabin.show()

    def namayesheProfileKarbar(self):
        self.namayesheProfileMokhatab(self.karbar_feli)

    def namayesheProfileMokhatab(self, username):
        if not username: return
        data_karbar = namayesh_karbar(username)
        if not data_karbar:
            QMessageBox.critical(self, "Error", "Could not fetch user data.")
            return

        self.panjare_profil = WidgetPasZamine(os.path.join(MASIR_ASLI_BARNAMEH, 'back2.jpg'))
        self.panjare_profil.setWindowTitle(f"{data_karbar.user_name}'s Profile")
        self.panjare_profil.setGeometry(200, 200, 350, 300)
        self.panjare_profil.setStyleSheet("QLabel { color: white; font-size: 15px; }")

        layout = QVBoxLayout(self.panjare_profil)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_aks_profil_bozorg = QLabel()
        ax = QPixmap(data_karbar.profile_image)
        label_aks_profil_bozorg.setPixmap(
            ax.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        label_aks_profil_bozorg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addRow("Username:", QLabel(data_karbar.user_name))
        form_layout.addRow("Phone:", QLabel(str(data_karbar.phone)))
        form_layout.addRow("Bio:", QLabel(data_karbar.bio or "Not set"))

        layout.addWidget(label_aks_profil_bozorg)
        layout.addLayout(form_layout)
        self.panjare_profil.show()

    def clickRoyeTanzimat(self):
        self.panjare_tanzimat = WidgetPasZamine(os.path.join(MASIR_ASLI_BARNAMEH, 'back4.jpg'))
        self.panjare_tanzimat.setWindowTitle("Settings")
        self.panjare_tanzimat.setGeometry(100, 100, 400, 350)
        self.panjare_tanzimat.setStyleSheet("""
            QLabel { color: white; font-size: 14px; }
            QLineEdit { background-color: rgba(42, 57, 66, 0.8); color: #E9EDEF; border-radius: 8px; padding: 10px; border: 1px solid #37444C;}
            QPushButton { background-color: #00A884; color: white; border-radius: 8px; padding: 10px; font-weight: bold; }
        """)

        self.tanzimat_username = QLineEdit()
        self.tanzimat_username.setPlaceholderText('Enter new username')
        self.tanzimat_shomare = QLineEdit()
        self.tanzimat_shomare.setPlaceholderText('Enter new phone number')
        self.tanzimat_password = QLineEdit()
        self.tanzimat_password.setPlaceholderText('Enter new password')
        self.tanzimat_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.tanzimat_takrar_password = QLineEdit()
        self.tanzimat_takrar_password.setPlaceholderText('Confirm new password')
        self.tanzimat_takrar_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.tanzimat_bio = QLineEdit()
        self.tanzimat_bio.setPlaceholderText('Enter your bio')

        dokme_entekhab_aks = QPushButton("Choose Profile Picture")
        dokme_entekhab_aks.clicked.connect(self.entekhabeAks)

        dokme_zakhire = QPushButton("Save Changes")
        dokme_zakhire.clicked.connect(self.zakhireTanzimat)

        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.tanzimat_username)
        form_layout.addRow("Phone Number:", self.tanzimat_shomare)
        form_layout.addRow("Password:", self.tanzimat_password)
        form_layout.addRow("Confirm Password:", self.tanzimat_takrar_password)
        form_layout.addRow("Bio:", self.tanzimat_bio)

        layout_asli = QVBoxLayout(self.panjare_tanzimat)
        layout_asli.addLayout(form_layout)
        layout_asli.addWidget(dokme_entekhab_aks)
        layout_asli.addWidget(dokme_zakhire)

        self.panjare_tanzimat.show()

    def entekhabeAks(self):
        masire_file, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "", "Image Files (*.png *.jpg *.jpeg)")
        if masire_file:
            esme_file = f"{self.karbar_feli}_{os.path.basename(masire_file)}"
            maghsad = os.path.join(MASIR_AKS_PROFILE, esme_file)
            try:
                shutil.copyfile(masire_file, maghsad)
                self.masire_aks_jadid = maghsad
                QMessageBox.information(self, "Success", "Profile picture selected! Click 'Save Changes' to apply.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not update picture:\n{e}")

    def zakhireTanzimat(self):
        if not self.karbar_feli:
            QMessageBox.critical(self, "Error", "No user is logged in.")
            return

        username_jadid = self.tanzimat_username.text().strip() or None
        shomare_jadid = self.tanzimat_shomare.text().strip() or None
        password_jadid = self.tanzimat_password.text() or None
        takrar_password_jadid = self.tanzimat_takrar_password.text()
        bio_jadid = self.tanzimat_bio.text().strip() or None
        aks_profil_jadid = getattr(self, 'masire_aks_jadid', None)

        if password_jadid and (password_jadid != takrar_password_jadid):
            QMessageBox.warning(self.panjare_tanzimat, "Error", "Passwords do not match.")
            return

        natije = beroozresani_karbar(
            current_username=self.karbar_feli,
            new_username=username_jadid,
            new_phone=shomare_jadid,
            new_password=password_jadid,
            new_bio=bio_jadid,
            new_profile_image=aks_profil_jadid
        )
        if natije == "Success":
            QMessageBox.information(self.panjare_tanzimat, "Success", "Your information has been updated successfully.")
            if username_jadid:
                self.karbar_feli = username_jadid
            self.beroozresaniNamayesheProfil()
            self.panjare_tanzimat.close()
            if hasattr(self, 'masire_aks_jadid'):
                delattr(self, 'masire_aks_jadid')
        else:
            QMessageBox.critical(self.panjare_tanzimat, "Error", natije)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panjare = PanjarehAsli()
    panjare.show()
    sys.exit(app.exec())