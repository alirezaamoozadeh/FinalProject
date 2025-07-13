import sys
import socket
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal

from messenger import PanjarehAsli

class ClientChat(QObject):
    payam_daryaft_shod = Signal(str, str)

    def __init__(self, host='localhost', port=12345):
        super().__init__()
        self.soket = None
        self.host = host
        self.port = port
        self.dar_hale_ejra = False
        self.username = None

    def vasl_shodan(self, username):
        self.username = username
        try:
            self.soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soket.connect((self.host, self.port))
            self.soket.sendall(self.username.encode('utf-8'))
            self.dar_hale_ejra = True
            threading.Thread(target=self.goosh_dadan_be_payamha, daemon=True).start()
            print(f"[INFO] Connected to server as '{self.username}'")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            return False

    def goosh_dadan_be_payamha(self):
        while self.dar_hale_ejra:
            try:
                payam = self.soket.recv(2048).decode('utf-8')
                if not payam: break
                ferestande, mohtava = payam.split(':', 1)
                self.payam_daryaft_shod.emit(ferestande, mohtava)
            except:
                break
        self.dar_hale_ejra = False

    def ersale_payam_be_karbar(self, girande, mohtava):
        if self.dar_hale_ejra:
            try:
                payam_format_shode = f"{girande}:{mohtava}"
                self.soket.sendall(payam_format_shode.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")

def main():
    barnameh = QApplication(sys.argv)

    panjare_asli = PanjarehAsli()
    client_chat = ClientChat()

    panjare_asli.login_movafagh.connect(client_chat.vasl_shodan)

    safhe_payamresan = panjare_asli.safheha[2]
    safhe_payamresan.darkhaste_ersale_payam.connect(client_chat.ersale_payam_be_karbar)
    client_chat.payam_daryaft_shod.connect(safhe_payamresan.namayeshePayameVoroodi)

    panjare_asli.show()
    sys.exit(barnameh.exec())

if __name__ == '__main__':
    main()