import socket
import threading
import logging

logger = logging.getLogger(__name__)

class UDPServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.is_running = False

    def bind(self):
        self.server_socket.bind((self.host, self.port))
        logger.info(f"Server listening on {self.host}:{self.port}")

    def start(self):
        self.is_running = True
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while self.is_running:
            try:
                data, addr = self.server_socket.recvfrom(1024)
                logger.info(f"Received message from {addr}: {data.decode()}")
                self.handle_message(data, addr)
            except Exception as e:
                logger.error(f"Error receiving message: {e}")

    def handle_message(self, data, addr):
        response = f"Received: {data.decode()}"
        self.send_message(response.encode(), addr)

    def send_message(self, message, addr):
        self.server_socket.sendto(message, addr)
        logger.info(f"Sent message to {addr}: {message.decode()}")

    def stop(self):
        self.is_running = False
        self.server_socket.close()
        logger.info("Server stopped")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server = UDPServer(host='0.0.0.0', port=9999)
    server.bind()
    server.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()