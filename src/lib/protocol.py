import collections
import logging as log
import time

from . import constant


def sequence_number(pkt_number):
    """Returns the sequence number for the `pkt_number`th packet"""
    # truncate to 32 bytes and skip 0 (CONN_START_SEQNUM)
    return (pkt_number - 1) % (2**32 - 1) + 1


def compose_request_msg(opcode, file_name):
    """
    Composes an operation request packet.

    Args:
        opcode (int): operation code for requested operation
        file_name (string): name of the file

    Returns:
        the composed request in a `bytes` iterable
    """
    if opcode not in constant.VALID_OPS:
        raise ValueError("the request has an invalid operation code")
    return compose_msg(
        constant.CONN_START_SEQNUM,
        (opcode.to_bytes(1, byteorder="big") + file_name.encode()),
    )


def compose_msg(header, payload=bytes()):
    """Composes a message with a header of 4 bytes and a payload"""
    return header.to_bytes(4, byteorder="big") + payload


def msg_number(msg):
    """Extracts the header number of a packet"""
    if len(msg) < 4:
        raise ValueError("the message is less than 4 bytes")
    return int.from_bytes(msg[:4], byteorder="big")


def parse_request_msg(msg):
    """
    Parses and validates a request message

    Args:
        msg (bytes): request message to parse

    Returns:
        a tuple with the sequence number, operation code, and file name
        of the request
    """
    if len(msg) < 6:
        raise ValueError("the first message received has an invalid size")

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
    """Extracts the header and payload of a message"""
    return msg_number(msg), msg[4:]


class Connection:
    """
    Represents a server connection with a client
    """

    def __init__(self, msg, storage_dir):
        seq_num, opcode, file_name = parse_request_msg(msg)

        log.debug(f"The first sequence number is: {seq_num}")
        log.debug(f"Received an operation number of: {opcode}")
        log.debug(f'Received file name: "{file_name}"')

        file_path = storage_dir + file_name

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
            constant.CONNECTION_TIMEOUT * 1_000_000
        )

    def timeout_response(self):
        self.t_last_msg = time.process_time_ns()
        return self.responder.timeout_response()

    def finished(self):
        return self.responder.finished()


class Sender:
    """
    A helper class that responds to ACK messages and sends data from a file
    """

    def __init__(self, file_name):
        log.debug(f"Reading from file: '{file_name}'")
        self.file = open(file_name, "rb")
        self.base = 1  # next expected ack
        self.last_sent = 0
        self.dup_ack = 0
        self.timeout_count = 0
        self.buffer = collections.deque(maxlen=constant.WINDOW_SIZE)
        self.final_pkt = None

    def respond_to(self, msg):
        """
        Responds to a message. Raises `StopIteration` when it's
        finished sending packets. Raises `TimeoutError` if
        connection timed-out.

        :param msg: message to respond to
        :return: an iterable with responses
        """
        ack_n = msg_number(msg)
        log.debug(f"Received ACK={ack_n}")

        if (
            sequence_number(self.base)
            < ack_n
            <= sequence_number(self.last_sent + 1)
        ):
            self.dup_ack = 0
            self.timeout_count = 0
            self.base = ack_n
        elif ack_n == sequence_number(self.base):
            self.dup_ack = (self.dup_ack + 1) % 3
            if self.dup_ack == 0:
                return self.timeout_response()

        if self.finished():
            log.info("Finished sending file")
            raise StopIteration("finished sending packets")

        log.debug(f"Current base={self.base}, last_sent={self.last_sent}")
        return self._fill_window()

    def timeout_response(self):
        """
        Creates a response to a time-out event.
        :return: an iterable of responses
        """
        if self.timeout_count == constant.RETRY_NUMBER:
            if self.final_pkt is not None and self.base == self.final_pkt:
                raise StopIteration(
                    "finished sending packets and connection was lost"
                )
            raise TimeoutError("connection was lost")

        self.timeout_count += 1
        # go-back-n
        log.debug(f"Resending {len(self.buffer)} packets")
        return (
            compose_msg(sequence_number(i), data)
            for i, data in enumerate(self.buffer, self.base)
        )

    def finished(self):
        return self.base - 1 == self.final_pkt

    def _fill_window(self):
        n_to_send = constant.WINDOW_SIZE - self.last_sent + self.base - 1
        data = [self._read_next_chunk() for _ in range(n_to_send)]
        msgs = [
            compose_msg(sequence_number(i), read)
            for i, read in enumerate(data, self.last_sent + 1)
            if len(read) > 0
        ]

        self.last_sent += len(msgs)

        if len(msgs) < n_to_send and self.final_pkt is None:
            self.last_sent += 1
            self.final_pkt = self.last_sent
            msgs.append(compose_msg(self.final_pkt))

        log.debug(f"Sent {len(msgs)} messages, last_sent={self.last_sent}")
        return msgs

    def _read_next_chunk(self):
        read = self.file.read(constant.PAYLOAD_SIZE)
        if len(self.buffer) > 0 and len(self.buffer[-1]) == 0:
            if len(self.buffer) > 1:
                self.buffer.popleft()
        else:
            self.buffer.append(read)
        return read

    def __del__(self):
        try:
            self.file.close()
        except AttributeError:
            pass


class Receiver:
    """
    A helper class that responds to data messages with ACKs and writes
    data to a file
    """

    def __init__(self, file_name):
        log.debug(f"Writing to file: '{file_name}'")
        self.file = open(file_name, "wb")
        self.next = 1
        self.timeout_count = 0
        self._finished = False

    def respond_to(self, msg):
        """
        Responds to a message. Raises `StopIteration` when it's
        finished receiving packets. Raises `TimeoutError` if
        connection timed-out.

        :param msg: message to respond to
        :return: an iterable with responses
        """
        if self.finished():
            raise StopIteration("finished receiving packets")

        seq_num, data = parse_data_msg(msg)

        log.debug(
            f"Received SEQ={seq_num}, "
            f"expected SEQ={sequence_number(self.next)}"
        )

        if seq_num == sequence_number(self.next):
            self.timeout_count = 0

            if len(data) == 0:
                log.info("Finished receiving file")
                self._finished = True

            self.file.write(data)
            self.next += 1

        log.debug(f"Sending ACK={sequence_number(self.next)}")
        return (compose_msg(sequence_number(self.next)),)

    def timeout_response(self):
        """
        Creates a response to a time-out event.
        :return: an iterable of responses
        """
        self.timeout_count += 1

        if self.timeout_count > constant.RETRY_NUMBER:
            raise TimeoutError("connection with client timed out")

        return tuple()

    def finished(self):
        return self._finished

    def __del__(self):
        try:
            self.file.close()
        except AttributeError:
            pass
