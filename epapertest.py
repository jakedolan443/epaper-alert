import socket

PORT = 9005


def create_test_packet(auth_code, custom_string, size=1024):
    # Ensure the authentication code is exactly 4 bytes
    if len(auth_code) != 4:
        raise ValueError("Authentication code must be exactly 4 bytes")

    # Encode the custom string
    custom_string_encoded = custom_string.encode('utf-8')

    # Ensure the total length of the auth code and custom string does not exceed the packet size
    if len(custom_string_encoded) + len(auth_code) > size:
        raise ValueError("Custom string plus auth code exceeds packet size")

    # Create the packet with the auth code, custom string, and pad with spaces
    packet = auth_code + custom_string_encoded + b' ' * (size - len(auth_code) - len(custom_string_encoded))
    print(packet)
    return packet

def send_test_packet(host='127.0.0.1', port=PORT, auth_code=b'ABCD', custom_string="Test Packet"):
    packet = create_test_packet(auth_code, custom_string)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(packet)
        print("Packet sent to server")

        # Receive echoed packet from the server
        received_packet = client_socket.recv(1024)
        print(f"Received packet from server: {received_packet[:50].decode('utf-8')}...")  # Print the first 50 bytes for brevity

if __name__ == "__main__":
    auth_code = b'1111'  # 4-byte authentication code
    custom_string = "WARNING Flooding is expected in the next 24 hours."

    send_test_packet(auth_code=auth_code, custom_string=custom_string)
