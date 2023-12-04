import socket
from contextlib import ExitStack
from typing import List


# copied from https://github.com/exasol/integration-test-docker-environment
def find_free_ports(num_ports: int) -> List[int]:
    def new_socket():
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def bind(sock: socket.socket, port: int):
        sock.bind(('', port))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def acquire_port_numbers(num_ports: int) -> List[int]:
        with ExitStack() as stack:
            sockets = [stack.enter_context(new_socket()) for dummy in range(num_ports)]
            for sock in sockets:
                bind(sock, 0)
                yield sock.getsockname()[1]
    def check_port_numbers(ports):
        with ExitStack() as stack:
            sockets_and_ports = [(stack.enter_context(new_socket()), port) for port in ports]
            for sock, port in sockets_and_ports:
                bind(sock, port)
    ports = list(acquire_port_numbers(num_ports))
    check_port_numbers(ports)
    return ports


def find_free_port():
    return find_free_ports(1)[0]
