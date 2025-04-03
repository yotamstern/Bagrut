import struct


def receive_data(client_socket):
    size = b''

    # Receive the first 4 bytes which represent the size
    while len(size) < 4:
        size += client_socket.recv(4 - len(size))

    # Decode the size and convert to integer
    size = struct.unpack("I", size)[0]

    data = b''

    # Receive the actual data based on the extracted size
    while len(data) < size:
        data += client_socket.recv(size - len(data))

    # Decode the received data
    actual_data = data

    return size, actual_data
