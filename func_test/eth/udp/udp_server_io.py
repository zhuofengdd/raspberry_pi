import socket
import logging
import select

logger = logging.getLogger(__name__)

class UDPServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        logger.info(f"Server listening on {self.host}:{self.port}")

        self.is_running = False

        try:
            self.epoll = select.epoll()
            self.epoll.register(self.server_socket.fileno(), select.EPOLLIN)
            self.use_epoll = True
            logger.info("Using epoll for I/O event notification")
        except AttributeError:
            self.use_epoll = False
            logger.info("Epoll not available, using select for I/O event notification")

    def start(self):
        self.is_running = True
        if self.use_epoll:
            self.run_epoll()
        else:
            self.run_select()

    def run_epoll(self):
        try:
            while self.is_running:
                events = self.epoll.poll()
                for fileno, event in events:
                    if fileno == self.server_socket.fileno():
                        data, addr = self.server_socket.recvfrom(1024)
                        logger.info(f"Received message from {addr}: {data.decode()}")
                        self.handle_message(data, addr)
        except Exception as e:
            logger.error(f"Error in epoll run: {e}")
        finally:
            self.epoll.unregister(self.server_socket.fileno())
            self.epoll.close()
            self.server_socket.close()

    def run_select(self):
        try:
            while self.is_running:
                readable, _, _ = select.select([self.server_socket], [], [])
                for s in readable:
                    if s == self.server_socket:
                        data, addr = self.server_socket.recvfrom(1024)
                        logger.info(f"Received message from {addr}: {data.decode()}")
                        self.handle_message(data, addr)
        except Exception as e:
            logger.error(f"Error in select run: {e}")
        finally:
            self.server_socket.close()

    def handle_message(self, data, addr):
        response = f"Received: {data.decode()}"
        self.send_message(response.encode(), addr)

    def send_message(self, message, addr):
        self.server_socket.sendto(message, addr)
        logger.info(f"Sent message to {addr}: {message.decode()}")

    def stop(self):
        self.is_running = False
        logger.info("Server stopped")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    server = UDPServer(host='0.0.0.0', port=9999)
    server.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()