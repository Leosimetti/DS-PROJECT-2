# TOLYA, SDELAY CLI TYT


import os
import socket
import sys


BUFF = 1488
PORT = 6969

def find_batya():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(b'Dai IP', ('<broadcast>', 1337))
    data, addr = s.recvfrom(1024)
    print(f'Server found at {addr}')
    return addr


def main():

    print("FINDING SERVER...")
    BATYA_IP = find_batya()[0]#input("ENTER BATYA IP:")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((BATYA_IP, int(PORT)))
    print("Connected to Nameserver...")


if __name__ == "__main__":
    main()


# if len(sys.argv) != 4:
#     print("Wrong arguments!")
#     exit(228)
#
# name = sys.argv[1]
# SERV_IP = sys.argv[2]
# SERV_PORT = sys.argv[3]
#
# size = os.path.getsize(name)
# print("Trying to connect to", SERV_IP + ":"+ SERV_PORT)
#
# # create the client socket
# s = socket.socket()
# s.connect((SERV_IP, int(SERV_PORT)))
# print("!!!Connected to server!!!")  # if it is not displayed ==> OOF
#
# # Send them together, so that they do not get lost :)
# msg = name + "?CON?" + str(size)
# s.send(msg.encode())
#
# # Counter initialization
# sas = 0
# pr_digit = '0'
#
# # Read/Send
# with open(name, "rb") as f:
#     for i in range(size):
#         snd = f.read(BUFF)
#         if snd:
#
#             # To make output less annoying
#             # msg = str(round(sas / float(size) * 100))
#             # if pr_digit != msg[0] and round(sas / float(size) * 100) > 9:
#             #     print(msg, " %")
#             #     pr_digit = msg[0]
#
#             sas += BUFF
#             s.sendall(snd)
#         else:
#             print("Transfer complete!!")
#             break
#
# # Cleanup
# s.close()
