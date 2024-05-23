import socket
import logging

logger = logging.getLogger(__name__)

class UDPClient:
    def __init__(self, client_host='localhost', client_port=0, server_host='localhost', server_port=9999):
        self.client_host = client_host
        self.client_port = client_port
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
            self.client_socket.sendto(message.encode(), (self.server_host, self.server_port))
            logger.info(f"Sent message to {self.server_host}:{self.server_port}: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def receive_message(self):
        try:
            data, addr = self.client_socket.recvfrom(1024)
            logger.info(f"Received message from {addr}: {data.decode()}")
            return data.decode()
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # 使用实际的客户端和服务器IP地址和端口
    client = UDPClient(client_host='0.0.0.0', client_port=19998, server_host='0.0.0.0', server_port=9999)
    
    client.send_message("Hello, Server!")
    response = client.receive_message()
    if response:
        logger.info(f"Response from server: {response}")