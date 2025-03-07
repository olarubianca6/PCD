import socket
import argparse
import time
import os
import ssl

def send_data(protocol, host, port, msg_size, total_size, mechanism, secure):
    num_messages = total_size // msg_size
    total_bytes = num_messages * msg_size
    retries = 3
    timeout = 5

    if protocol == 'tcp':
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(timeout)

        try:
            client_socket.connect((host, port))
            if secure:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.load_verify_locations("cert.pem")
                client_socket = context.wrap_socket(client_socket, server_hostname=host)
                print("Secure TLS connection established")
        except Exception as e:
            print(f"Connection failed: {e}")
            return

    else:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = os.urandom(msg_size)
    start_time = time.time()

    for i in range(num_messages):
        try:
            client_socket.sendall(data) if protocol == "tcp" else client_socket.sendto(data, (host, port))

            if mechanism == "stop-and-wait":
                ack_received = False
                for attempt in range(retries):
                    try:
                        client_socket.settimeout(timeout)
                        acknowledgment = client_socket.recv(1) if protocol == "tcp" else client_socket.recvfrom(1)[0]
                        if acknowledgment == b'a':
                            ack_received = True
                            break
                    except socket.timeout:
                        print(f"Error. Retrying message {i+1}/{num_messages} (Attempt {attempt+1}/{retries})")
                        client_socket.sendall(data) if protocol == "tcp" else client_socket.sendto(data, (host, port))

                if not ack_received:
                    print(f"Failed acknowledgment for message {i+1}")
                    break

        except Exception as e:
            print(f"Error sending message {i+1}: {e}")
            break

    end_time = time.time()
    client_socket.close()

    print(f'Client - Protocol: {protocol.upper()}, Duration: {end_time - start_time:.3f}s, Messages sent: {num_messages}, Bytes sent: {total_bytes}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for sending data")
    parser.add_argument("--protocol", choices=["tcp", "udp"], required=True, help="Protocol to use")
    parser.add_argument("--host", type=str, required=True, help="Server IP address")
    parser.add_argument("--port", type=int, required=True, help="Server port number")
    parser.add_argument("--msg_size", type=int, required=True, help="Size of each message")
    parser.add_argument("--total_size", type=int, required=True, help="Total data to send")
    parser.add_argument("--mechanism", choices=["streaming", "stop-and-wait"], required=True, help="Transmission mechanism")
    parser.add_argument("--secure", action="store_true", help="TLS encryption (TCP only)")
    args = parser.parse_args()

    send_data(args.protocol, args.host, args.port, args.msg_size, args.total_size, args.mechanism, args.secure)