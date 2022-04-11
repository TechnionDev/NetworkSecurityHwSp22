import socket
import argparse

def main():
    # Create command line arguments using argparse
    parser = argparse.ArgumentParser(description='HTTP server')
    parser.add_argument('port', help='Port to listen to', type=int)
    args = parser.parse_args()

    port = args.port

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Listen to loopback on the port
    sock.bind(('127.0.0.1', port))

    # Wait for request from client
    sock.listen(1)

    # Connection accept loop
    while True:
        conn, addr = sock.accept()
        print(f'Connected to {addr=}')

        # Read content of file `compi_checker.html`
        with open('compi_checker.html', 'r') as f:
            content = f.read()

        # Send response and close connection
        conn.sendall(
            f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{content}'.encode())
        conn.close()

    # Close the socket
    sock.close()


if __name__ == '__main__':
    main()
