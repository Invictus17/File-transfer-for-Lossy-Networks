import socket
import sys
import os
import time
import errno

MESSAGE_LEN = 1400

def client_GBN_rudp(host, port, file):
    print("Hello, I am GBN client", host, port)
    try:
        addr_list = socket.getaddrinfo(host, port)
    except Exception as e:
        sys.exit("error as {}".format(e))

    for addr in addr_list:
        host, port = addr[-1][0], addr[-1][1]

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setblocking(False)

        buffer = []
        base = 0
        wind_size = 30
        pack_type = b'N'
        end_flag = False
        timeout_sec = 0.009
        SEQ = 0
        enter = True
        received_msg = None
        while True:

            while end_flag is False and SEQ < base + wind_size:
                # Create packet
                packet = b""
                packet += pack_type
                packet += str.encode(str(SEQ))
                packet += b'SEQ_del'

                file_data = file.read(MESSAGE_LEN - len(packet))

                if file_data == b'':
                    end_flag = True

                packet += file_data
                buffer.append(packet)

                # Send packet
                client_socket.sendto(buffer[SEQ], (host, port))

                if enter:
                    start_timer = time.time()
                    enter = False
                SEQ += 1

                try:
                    received_msg = client_socket.recv(MESSAGE_LEN)
                except BlockingIOError:
                    pass

                if received_msg:
                    msg_str = received_msg.decode()
                    if msg_str[0] == 'A':

                        if msg_str[1] == 'E':
                            return

                        if int(msg_str[1:]) + 1 > base:
                            base = int(msg_str[1:]) + 1
                            wind_size += 1
                            start_timer = time.time()
                        else:
                            if wind_size // 2 > 15:
                                wind_size = wind_size // 2
                    received_msg = None

            try:
                received_msg = client_socket.recv(MESSAGE_LEN)
            except BlockingIOError:
                pass

            if received_msg:
                msg_str = received_msg.decode()
                if msg_str[0] == 'A':

                    if msg_str[1] == 'E':
                        return

                    if int(msg_str[1:]) + 1 > base:
                        base = int(msg_str[1:]) + 1
                        wind_size += 1
                        start_timer = time.time()
                    else:
                        if wind_size // 2 > 15:
                            wind_size = wind_size // 2
                received_msg = None

            if time.time() - start_timer > timeout_sec:
                count = 0
                start_timer = time.time()
                if wind_size // 2 > 15:
                    wind_size = wind_size // 2
                while count < wind_size:
                    if base + count >= len(buffer):
                        break
                    client_socket.sendto(buffer[base + count], (host, port))
                    count += 1
                    
                    
def server_GBN_rudp(host, port, file):
    print("Hello, I am a GBN server")

    if host is None:
        host = '127.0.0.1'
    try:
        socket.inet_aton(host)
    except socket.error:
        sys.exit("Please provide appropriate ip for server")

    port = int(port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    server_socket.setblocking(False)
    message = None
    SEQ = '0'
    old_SEQ = '-1'
    while True:
        try:
            message, address = server_socket.recvfrom(MESSAGE_LEN + 30)
            if message:
                timer = time.time()

                i = 1
                while message[i:i+7] != b'SEQ_del':
                    i += 1
                pack_info = message[0:i+7].decode()

                if pack_info[0] == 'N':

                    recv_seq = pack_info.split('SEQ_del')[0][1:]
                    if recv_seq == SEQ:

                        if message[len(recv_seq) + 1 + 7:] == b'':
                            server_socket.sendto(b'AE', address)
                            return

                        file.write(message[len(recv_seq) + 1 + 7:])
                        file.flush()

                        packet = 'A' + SEQ
                        server_socket.sendto(str.encode(packet), address)
                        old_SEQ = SEQ
                        SEQ = str(int(SEQ) + 1)
                    else:
                        packet = 'A' + old_SEQ
                        server_socket.sendto(str.encode(packet), address)
                    message = None
            else:
                if time.time() - timer > 0.036:
                    return
        except BlockingIOError:
            pass
