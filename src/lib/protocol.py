import logging as log
import socket


WINDOW_SIZE = 10

class Connection:
    def __init__(self, addr, msg):
        self.base = 0
        self.addr = addr
        seq_num = int.from_bytes(msg[:4], byteorder="big")
        if seq_num != 0:
            raise ValueError("el primer paquete tiene número de secuencia no nulo")
        log.debug(f'Se recibió un valor de operación de: {int.from_bytes(msg[4:5], byteorder="big")}')
        log.debug(f'El nombre del archivo es: "{msg[5:].decode()}"')
        # if int.from_bytes(msg[4:5], byteorder="big") == 0:
        #     self.responder = Sender(str.encode(msg[5:]))
        # elif int(msg[4:5]) == 1:
        #     self.responder = Receiver(str.encode(msg[5:]))

    def respond_to(self, msg):
        self.responder.respond_to(msg)


class Sender:
    def __init__(self, file_name):
        pass

    def respond_to(self, msg):
        pass


class Receiver:
    def __init__(self, file_name):
        self.file = open(file_name, 'wb')

    def respond_to(self, msg):
        pass

    def __del__(self):
        self.file.close()
