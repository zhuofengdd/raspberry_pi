import socket
import select
import logging

logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
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

        self.clients = {}

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
                        client_socket, addr = self.server_socket.accept()
                        logger.info(f"Accepted connection from {addr}")
                        self.epoll.register(client_socket.fileno(), select.EPOLLIN)
                        self.clients[client_socket.fileno()] = client_socket
                    elif event & select.EPOLLIN:
                        self.handle_client(self.clients[fileno])
        except Exception as e:
            logger.error(f"Error in epoll run: {e}")
        finally:
            self.cleanup()

    def run_select(self):
        try:
            while self.is_running:
                readable, _, _ = select.select([self.server_socket] + list(self.clients.values()), [], [])
                for s in readable:
                    if s == self.server_socket:
                        client_socket, addr = self.server_socket.accept()
                        logger.info(f"Accepted connection from {addr}")
                        self.clients[client_socket] = client_socket
                    else:
                        self.handle_client(s)
        except Exception as e:
            logger.error(f"Error in select run: {e}")
        finally:
            self.cleanup()

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024)
            if data:
                logger.info(f"Received message: {data.decode()}")
                response = f"Received: {data.decode()}"
                client_socket.sendall(response.encode())
            else:
                self.remove_client(client_socket)
        except Exception as e:
            logger.error(f"Error handling client: {e}")
            self.remove_client(client_socket)

    def remove_client(self, client_socket):
        fileno = client_socket.fileno()
        if self.use_epoll:
            self.epoll.unregister(fileno)
        client_socket.close()
        del self.clients[fileno]

    def cleanup(self):
        for client_socket in self.clients.values():
            client_socket.close()
        self.server_socket.close()
        if self.use_epoll:
            self.epoll.unregister(self.server_socket.fileno())
            self.epoll.close()
        logger.info("Server cleaned up")

    def stop(self):
        self.is_running = False
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