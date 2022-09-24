import collections
import logging as log
import time

from . import constant


def compose_request_msg(opcode, file_name):
    if opcode not in constant.VALID_OPS:
        raise ValueError(
            "the request has an invalid operation code"
        )
    return compose_msg(
        constant.CONN_START_SEQNUM,
        (opcode.to_bytes(1, byteorder="big") + file_name.encode())
    )


def compose_msg(seq_num, payload=bytes()):
    return seq_num.to_bytes(4, byteorder="big") + payload


def msg_number(msg):
    if len(msg) < 4:
        raise ValueError(
            "the message is less than 4 bytes"
        )
    return int.from_bytes(msg[:4], byteorder="big")


def parse_request_msg(msg):
    if len(msg) < 6:
        raise ValueError(
            "the first message received has an invalid size"
        )

    seq_num = msg_number(msg)
    if seq_num != 0:
        raise ValueError(
            "the first message received has nonzero sequence number"
        )

    opcode = int.from_bytes(msg[4:5], byteorder="big")
    if opcode not in constant.VALID_OPS:
        raise ValueError(
            "the first message received has an invalid operation code"
        )

    file_name = msg[5:].decode()

    return (
        seq_num,
        opcode,
        file_name,
    )


def parse_data_msg(msg):
    return msg_number(msg), msg[4:]


class Connection:
    def __init__(self, msg, storage_dir):
        seq_num, opcode, file_name = parse_request_msg(msg)

        log.debug(f"The first sequence number is: {seq_num}")
        log.debug(f"Received an operation number of: {opcode}")
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
        return time.process_time_ns() - self.t_last_msg > (
            constant.RETRY_DELAY * 1_000_000
        )

    def timeout_response(self):
        self.t_last_msg = time.process_time_ns()
        return self.responder.timeout_response()


class Sender:
    def __init__(self, file_name):
        log.debug(f"Reading from file: '{file_name}'")
        self.file = open(file_name, "rb")
        self.base = 1  # next expected ack
        self.last_sent = 0
        self.dup_ack = 0
        self.timeout_count = 0
        self.buffer = collections.deque(maxlen=constant.WINDOW_SIZE)

    def respond_to(self, msg):
        ack_n = msg_number(msg)
        log.debug(f"Received ACK={ack_n}")

        if self.base < ack_n <= self.last_sent:
            self.dup_ack = 0
            self.timeout_count = 0
            self.base = ack_n
        elif ack_n == self.base:
            self.dup_ack = (self.dup_ack + 1) % 3
            if self.dup_ack == 0:
                return self.timeout_response()

        log.debug(f"Current base={self.base}, last_sent={self.last_sent}")
        return self.fill_window()

    def timeout_response(self):
        if self.timeout_count == constant.RETRY_NUMBER:
            raise TimeoutError("connection was lost")

        self.timeout_count += 1
        # go-back-n
        return iter(self.buffer)

    def fill_window(self):
        msgs = (
            compose_msg(seq_num, self.read_next_chunk())
            for seq_num in range(
                self.last_sent + 1, self.base + constant.WINDOW_SIZE
            )
        )
        self.last_sent = self.base + len(self.buffer) - 1
        return msgs

    def read_next_chunk(self):
        read = self.file.read(constant.PAYLOAD_SIZE)
        self.buffer.append(read)
        return read

    def __del__(self):
        self.file.close()


class Receiver:
    def __init__(self, file_name):
        log.debug(f"Writing to file: '{file_name}'")
        self.file = open(file_name, "wb")
        self.next = 1
        self.timeout_count = 0

    def respond_to(self, msg):
        seq_num, data = parse_data_msg(msg)

        log.debug(f"The sequence number is: {seq_num}")

        if seq_num == self.next:
            self.timeout_count = 0

            if len(data) == 0:
                log.info("Finished receiving file")
                raise StopIteration("finished sending packets")

            self.file.write(data)
            # hay que truncarlo a 32 bits
            self.next = (self.next + 1) % (2**32)

        log.debug(f"Sending ACK={self.next}")
        return compose_msg(self.next),

    def timeout_response(self):
        self.timeout_count += 1

        if self.timeout_count > constant.RETRY_NUMBER:
            raise TimeoutError("connection with client timed out")

        return tuple()

    def __del__(self):
        self.file.close()
