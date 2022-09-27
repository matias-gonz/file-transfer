DOWNLOAD = 1
UPLOAD = 2

VALID_OPS = frozenset((DOWNLOAD, UPLOAD))

MAX_PKT_SIZE = 4096
HEADER_SIZE = 4
PAYLOAD_SIZE = MAX_PKT_SIZE - HEADER_SIZE

CONNECTION_TIMEOUT = 0.6  # seconds before connection timeout
SOCKET_TIMEOUT = 0.030  # socket.recvfrom timeout
RETRY_NUMBER = 10  # number of retries before cutting the faulty connection
WINDOW_SIZE = 10  # size of the sending window (set to 1 for stop-and-wait)
DUP_ACKS_BEFORE_RETRY = 3  # number of duplicate ACKs before resending packets

# sequence number of the first packet sent from client (don't change)
CONN_START_SEQNUM = 0
