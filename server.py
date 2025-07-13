import socket
import threading

HOST = 'localhost'
PORT = 12345
clients = {}
clients_lock = threading.Lock()

def shoroo_server():
    soket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soket_server.bind((HOST, PORT))
        soket_server.listen()
        print(f"[INFO] Server listening on {HOST}:{PORT}")
    except OSError as e:
        print(f"[ERROR] Could not bind to port {PORT}: {e}")
        return

    try:
        while True:
            ertebat, neshani = soket_server.accept()
            threading.Thread(target=modiriat_client, args=(ertebat, neshani), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down server.")
    finally:
        soket_server.close()

def modiriat_client(ertebat, neshani):
    print(f"[NEW CONNECTION] {neshani} connected.")
    nam_karbari = None
    try:
        nam_karbari = ertebat.recv(1024).decode('utf-8').strip()
        if not nam_karbari: raise ValueError("Username cannot be empty")
        with clients_lock:
            clients[nam_karbari] = ertebat
        print(f"[LOGIN] User '{nam_karbari}' logged in.")

        while True:
            payam = ertebat.recv(2048).decode('utf-8')
            if not payam: break

            try:
                girande, mohtava = payam.split(':', 1)
                ferestande = nam_karbari

                with clients_lock:
                    if girande in clients:
                        ertebat_girande = clients[girande]
                        payam_format_shode = f"{ferestande}:{mohtava}"
                        ertebat_girande.sendall(payam_format_shode.encode('utf-8'))
                    else:
                        print(f"[DELIVERY FAILED] Recipient '{girande}' not found.")
            except ValueError:
                print(f"[MALFORMED DATA] from {nam_karbari}: {payam}")
    except Exception:
        pass
    finally:
        with clients_lock:
            if nam_karbari and nam_karbari in clients:
                del clients[nam_karbari]
        print(f"[DISCONNECTED] User '{nam_karbari}' disconnected.")
        ertebat.close()

if __name__ == '__main__':
    shoroo_server()