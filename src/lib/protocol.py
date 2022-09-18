import logging as log

WINDOW_SIZE = 10


class Connection:
    def __init__(self, addr, msg):
        seq_num = int.from_bytes(msg[:4], byteorder="big")
        log.debug(f'El número de secuencia es: {seq_num}')

        if seq_num != 0:
            raise ValueError(
                "el primer paquete tiene número de secuencia no nulo"
            )

        opcode = int.from_bytes(msg[4:5], byteorder="big")
        log.debug(
            f'Se recibió un valor de operación de: {opcode}'
        )

        file_name = msg[5:].decode()
        log.debug(f'El nombre del archivo es: "{file_name}"')

        if opcode == 0:
            self.responder = Sender(file_name)
        elif opcode == 1:
            self.responder = Receiver(file_name)

    def respond_to(self, msg):
        return self.responder.respond_to(msg)


class Sender:
    def __init__(self, file_name):
        self.file = open(file_name, "rb")

    def respond_to(self, msg):
        packet = bytearray()
        return packet

    def __del__(self):
        self.file.close()


class Receiver:
    def __init__(self, file_name):
        self.file = open(file_name, "wb")
        self.next = 1

    def respond_to(self, msg):
        seq_num = int.from_bytes(msg[:4], byteorder="big")

        if seq_num == self.next:
            self.file.write(msg[4:])
            self.next = (self.next + 1) % (2 ** 32)

        return self.next.to_bytes(4, byteorder="big")

    def __del__(self):
        self.file.close()
