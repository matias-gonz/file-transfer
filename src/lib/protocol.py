import logging as log
import time

WINDOW_SIZE = 10
RETRY_DELAY = 1.0  # [s]
RETRY_NUMBER = 3


class Connection:
    def __init__(self, addr, msg, storage_dir):
        seq_num = int.from_bytes(msg[:4], byteorder="big")
        log.debug(f"The first sequence number is: {seq_num}")

        if seq_num != 0:
            raise ValueError(
                "the first message received has nonzero sequence number"
            )

        opcode = int.from_bytes(msg[4:5], byteorder="big")
        log.debug(f"Received an operation number of: {opcode}")

        file_name = msg[5:].decode()
        log.debug(f'Received file name: "{file_name}"')

        file_path = storage_dir + "/" + file_name

        if opcode == 0:
            self.responder = Sender(file_path)
        elif opcode == 1:
            self.responder = Receiver(file_path)

        self.t_last_msg = time.process_time_ns()

    def respond_to(self, msg):
        self.t_last_msg = time.process_time_ns()
        return self.responder.respond_to(msg)

    def timed_out(self):
        # TODO: cambiar el 0.100 por una constante
        return time.process_time_ns() - self.t_last_msg > (RETRY_DELAY * 1_000_000)

    def timeout_response(self):
        self.t_last_msg = time.process_time_ns()
        return self.responder.timeout_response()


class Sender:
    def __init__(self, file_name):
        self.file = open(file_name, "rb")

    def respond_to(self, msg):
        packet = bytearray()
        return packet

    def timeout_response(self):
        packet = bytearray()
        return packet

    def __del__(self):
        self.file.close()


class Receiver:
    def __init__(self, file_name):
        self.file = open(file_name, "wb")
        self.next = 1
        self.timeout_count = 0

    def respond_to(self, msg):
        seq_num = int.from_bytes(msg[:4], byteorder="big")

        log.debug(f"The sequence number is: {seq_num}")

        if seq_num == self.next:
            self.timeout_count = 0

            data = msg[4:]

            if len(data) == 0:
                return bytearray()

            self.file.write(data)
            # hay que truncarlo a 32 bits
            self.next = (self.next + 1) % (2**32)

        return self.next.to_bytes(4, byteorder="big")

    def timeout_response(self):
        self.timeout_count += 1

        if self.timeout_count > RETRY_NUMBER:
            raise TimeoutError("Se perdió la conexión con el cliente")

        return bytearray()

    def __del__(self):
        self.file.close()
