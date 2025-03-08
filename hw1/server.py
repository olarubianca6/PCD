import socket
import argparse
import ssl

def start_server(protocol, port, mechanism, secure):
    if protocol == "tcp":
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        print(f'TCP Server listening on port {port}. Waiting for connections.')

        conn, addr = server_socket.accept()
        print(f'Connected by: {addr}')

        if secure:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
            conn = context.wrap_socket(conn, server_side=True)
            print("Secure TLS connection established")

        num_messages, received_bytes = 0, 0

        while True:
            try:
                data = conn.recv(65535)
                if not data:
                    break
                num_messages += 1
                received_bytes += len(data)

                if mechanism == "stop-and-wait":
                    conn.sendall(b'a')

            except ConnectionResetError:
                print("Client disconnected unexpectedly.")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        conn.close()

    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', port))
        print(f'UDP Server listening on port {port}')

        num_messages, received_bytes = 0, 0

        try:
            while True:
                data, addr = server_socket.recvfrom(65535)
                if not data:
                    break
                num_messages += 1
                received_bytes += len(data)

                if mechanism == "stop-and-wait":
                    server_socket.sendto(b'a', addr)

        except KeyboardInterrupt:
            print("\nUDP server shutting down...")

        finally:
            if server_socket:
                server_socket.close()
            print(f'Server - Protocol: {protocol.upper()}, Messages received: {num_messages}, Bytes received: {received_bytes}.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Server for measuring data transfers")
    parser.add_argument("--protocol", choices=['tcp', 'udp'], required=True, help="Protocol to use")
    parser.add_argument("--port", type=int, required=True, help="Port to listen on")
    parser.add_argument("--mechanism", choices=["streaming", "stop-and-wait"], required=True, help="Transmission mechanism")
    parser.add_argument("--secure", action="store_true", help="TLS encryption (TCP only)")
    args = parser.parse_args()

    start_server(args.protocol, args.port, args.mechanism, args.secure)