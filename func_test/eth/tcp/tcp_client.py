import socket
import logging

logger = logging.getLogger(__name__)

class TCPClient:
    def __init__(self, client_host='localhost', client_port=0, server_host='localhost', server_port=9999):
        self.client_host = client_host
        self.client_port = client_port
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置SO_REUSEADDR选项
        self.bind()

    def bind(self):
        try:
            self.client_socket.bind((self.client_host, self.client_port))
            logger.info(f"Client bound to {self.client_host}:{self.client_port}")
        except socket.error as e:
            logger.error(f"Error binding client socket: {e}")
            raise

    def send_message(self, message):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            self.client_socket.sendall(message.encode())
            response = self.client_socket.recv(1024)
            logger.info(f"Received response from server: {response.decode()}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
        finally:
            self.client_socket.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client = TCPClient(client_host='0.0.0.0', client_port=19998, server_host='localhost', server_port=9999)
    client.send_message("Hello, Server!")