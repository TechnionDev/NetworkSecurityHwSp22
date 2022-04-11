# Reads hostname and port from command line and sends a get request to the server using sockets

import socket
import argparse


def main():
    # Create command line arguments using argparse
    parser = argparse.ArgumentParser(description='GET requests HTTP')
    parser.add_argument('hostname', help='Hostname of server')
    parser.add_argument('port', help='Port to server', type=int)
    args = parser.parse_args()

    hostname = args.hostname
    port = args.port

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    sock.connect((hostname, port))

    # Send the GET request
    sock.sendall(
        f"GET / HTTP/1.1\r\nHost: {hostname}\r\n\r\n".encode(encoding='ascii'))

    # Wait for the response
    res = sock.recv(1024)

    # Print res
    print(res.decode())

    # Close the socket
    sock.close()


if __name__ == '__main__':
    main()