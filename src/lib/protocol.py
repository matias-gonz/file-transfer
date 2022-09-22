import collections
import logging as log
import time

import constant

RETRY_DELAY = 1.0  # [s]
RETRY_NUMBER = 3


class Connection:
    def __init__(self, msg, storage_dir):
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

        if opcode == constant.DOWNLOAD:
            self.responder = Sender(file_path)
        elif opcode == constant.UPLOAD:
            self.responder = Receiver(file_path)

        self.t_last_msg = time.process_time_ns()

    def respond_to(self, msg):
        self.t_last_msg = time.process_time_ns()
        return self.responder.respond_to(msg)

    def timed_out(self):
        # TODO: cambiar el 0.100 por una constante
        return time.process_time_ns() - self.t_last_msg > (
            RETRY_DELAY * 1_000_000
        )

    def timeout_response(self):
        self.t_last_msg = time.process_time_ns()
        return self.responder.timeout_response()


class Sender:
    def __init__(self, file_name):
        self.file = open(file_name, "rb")
        self.base = 1  # oldest in-flight packet
        self.dup_ack = 2
        self.timeout_count = -1
        self.buffer = collections.deque(maxlen=constant.WINDOW_SIZE)
        for i in range(constant.WINDOW_SIZE):
            self.read_next_chunk()

    def respond_to(self, msg):
        ack_n = int.from_bytes(msg[:4], byteorder="big")

        if ack_n == 0:
            return self.go_back_n()

        log.debug(f"Received ACK={ack_n}")

        if ack_n < self.base:
            return tuple()

        if ack_n == self.base:
            self.dup_ack = (self.dup_ack + 1) % 3
            return tuple() if self.dup_ack != 0 else self.timeout_response()

        self.dup_ack = 0
        self.timeout_count = 0

        msgs = (
            self.compose_msg(seq_num, self.read_next_chunk())
            for seq_num in range(
                self.base + constant.WINDOW_SIZE, ack_n + constant.WINDOW_SIZE
            )
        )

        self.base = ack_n
        log.debug(f"Current base={self.base}")

        return msgs

    def timeout_response(self):
        if self.timeout_count == RETRY_NUMBER:
            raise TimeoutError("connection was lost")

        self.timeout_count += 1

        return self.go_back_n()

    def go_back_n(self):
        return (
            self.compose_msg(i, payload)
            for i, payload in enumerate(self.buffer, self.base)
        )

    def compose_msg(self, seq_num, payload):
        return seq_num.to_bytes(4, byteorder="big") + payload

    def read_next_chunk(self):
        read = self.file.read(constant.PAYLOAD_SIZE)
        self.buffer.append(read)
        return read

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
                log.info("Finished receiving file")
                raise StopIteration("finished sending packets")

            self.file.write(data)
            # hay que truncarlo a 32 bits
            self.next = (self.next + 1) % (2**32)

        return self.next.to_bytes(4, byteorder="big"),

    def timeout_response(self):
        self.timeout_count += 1

        if self.timeout_count > RETRY_NUMBER:
            raise TimeoutError("connection was lost")

        return tuple()

    def __del__(self):
        self.file.close()
