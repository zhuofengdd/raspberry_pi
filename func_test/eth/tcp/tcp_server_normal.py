import socket
import threading
import logging

logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f"Server listening on {self.host}:{self.port}")

        self.is_running = False

    def start(self):
        self.is_running = True
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while self.is_running:
            try:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"Accepted connection from {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")

    def handle_client(self, client_socket, addr):
        with client_socket:
            try:
                data = client_socket.recv(1024)
                if data:
                    logger.info(f"Received message from {addr}: {data.decode()}")
                    response = f"Received: {data.decode()}"
                    client_socket.sendall(response.encode())
            except Exception as e:
                logger.error(f"Error handling client {addr}: {e}")

    def stop(self):
        self.is_running = False
        self.server_socket.close()
        logger.info("Server stopped")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server = TCPServer(host='0.0.0.0', port=9999)
    server.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()