import collections
import logging as log
import time
from os import path

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
        raise ValueError(
            f"the message is less than 4 bytes (has {len(msg)} B)"
        )
    return int.from_bytes(msg[:4], byteorder="big")


def request_response_msg(response_code):
    return compose_msg(
        constant.CONN_START_SEQNUM, response_code.to_bytes(1, byteorder="big")
    )


def msg_response_code(msg):
    if len(msg) != 5:
        raise ValueError(f"the message is not 5 bytes (has {len(msg)} B)")
    return int.from_bytes(msg[4:5], byteorder="big")


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

    file_name = msg[5:].decode()[:255]

    if "/../" in file_name or file_name.startswith("../"):
        raise ValueError("the first message received has an invalid file name")

    return (
        seq_num,
        opcode,
        file_name,
    )


def parse_data_msg(msg):
    """Extracts the header and payload of a message"""
    return msg_number(msg), msg[4:]


def handle_clientside_conn(s, server_address, responder, initial_msg):
    msg = initial_msg
    while True:
        try:
            responses = responder.respond_to(msg)

            for resp in responses:
                s.sendto(resp, server_address)

            if responder.finished():
                return

            address = tuple()
            while address != server_address:
                try:
                    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)
                except TimeoutError:
                    for resp in responder.timeout_response():
                        s.sendto(resp, server_address)

        except StopIteration:
            return


class Connection:
    """
    Represents a server connection with a client
    """

    def __init__(self, msg, storage_dir):
        self.resp_code = constant.ALL_OK
        seq_num, opcode, file_name = parse_request_msg(msg)

        log.debug(f"The first sequence number is: {seq_num}")
        log.debug(f"Received an operation number of: {opcode}")
        log.debug(f'Received file name: "{file_name}"')

        file_path = storage_dir + file_name

        try:
            if opcode == constant.DOWNLOAD:
                log.debug(f"Reading from file: '{file_path}'")
                self.file = open(file_path, "rb")
                log.debug(f"The file has {path.getsize(file_path)} Bytes")
                self.responder = Sender(self.file)
            elif opcode == constant.UPLOAD:
                log.debug(f"Writing to file: '{file_path}'")
                self.file = open(file_path, "wb")
                self.responder = Receiver(self.file)
        except OSError:
            self.resp_code = constant.ERROR_OPENING_FILE

        self.t_last_msg = time.monotonic()

    def respond_to(self, msg):
        self.t_last_msg = time.monotonic()
        if msg_number(msg) == constant.CONN_START_SEQNUM:
            log.debug(f"Sending response code {self.resp_code}")
            return (request_response_msg(self.resp_code),)
        elif self.resp_code != constant.ALL_OK:
            raise StopIteration(
                f"finished connection with error {self.resp_code}"
            )
        return self.responder.respond_to(msg)

    def timed_out(self):
        return time.monotonic() - self.t_last_msg > (
            constant.CONNECTION_TIMEOUT
        )

    def timeout_response(self):
        self.t_last_msg = time.monotonic()
        return self.responder.timeout_response()

    def finished(self):
        return self.resp_code != constant.ALL_OK or self.responder.finished()

    def __del__(self):
        try:
            self.file.close()
        except AttributeError:
            pass


class Sender:
    """
    A helper class that responds to ACK messages and sends data from a file
    """

    def __init__(self, file):
        self.file = file
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
            self.dup_ack = (self.dup_ack + 1) % constant.WINDOW_SIZE
            if self.dup_ack == constant.DUP_ACKS_BEFORE_RETRY:
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
            if self.base == self.final_pkt:
                raise StopIteration(
                    "finished sending packets and connection was lost"
                )
            raise TimeoutError("connection was lost")

        self.timeout_count += 1
        # go-back-n
        msgs = [msg for _, msg in enumerate(self.buffer, self.base)]
        msgs_lens = ", ".join((str(len(m)) for m in msgs))
        log.debug(
            f"Resend {len(msgs)} messages from {self.base}, "
            + (f"of size {msgs_lens}, " if len(msgs_lens) > 0 else "")
            + f"last_sent={self.last_sent}"
        )
        return msgs

    def finished(self):
        return self.final_pkt is not None and self.base - 1 == self.final_pkt

    def _fill_window(self):
        not_acked = self.last_sent - self.base + 1
        n_to_remove = len(self.buffer) - not_acked
        n_to_send = constant.WINDOW_SIZE - not_acked

        self._pop_acked(n_to_remove)
        msgs = self._push_next_msgs(n_to_send)

        transfer_ended = len(msgs) == 0 and not_acked == 0
        if transfer_ended and self.final_pkt is None:
            msg = self._push_final_message()
            msgs.append(msg)

        msgs_lens = ", ".join((str(len(m)) for m in msgs))
        log.debug(
            f"Sent {len(msgs)} messages, "
            + (f"of size {msgs_lens}, " if len(msgs_lens) > 0 else "")
            + f"last_sent={self.last_sent}"
        )
        return msgs

    def _pop_acked(self, n_to_remove):
        for _ in range(n_to_remove):
            self.buffer.popleft()

    def _push_next_msgs(self, n_to_send):
        msgs = []
        for i in range(self.last_sent + 1, self.last_sent + 1 + n_to_send):
            d = self.file.read(constant.PAYLOAD_SIZE)

            if len(d) == 0:
                break

            msg = compose_msg(sequence_number(i), d)
            self.buffer.append(msg)
            msgs.append(msg)

        self.last_sent += len(msgs)
        return msgs

    def _push_final_message(self):
        self.last_sent += 1
        self.final_pkt = self.last_sent
        msg = compose_msg(
            sequence_number(self.final_pkt),
        )
        self.buffer.append(msg)
        return msg


class Receiver:
    """
    A helper class that responds to data messages with ACKs and writes
    data to a file
    """

    def __init__(self, file):
        self.file = file
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

            self.file.write(data)
            self.next += 1

            if len(data) == 0:
                log.info("Finished receiving file")
                self._finished = True

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
