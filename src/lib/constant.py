DOWNLOAD = 1
UPLOAD = 2

VALID_OPS = frozenset((DOWNLOAD, UPLOAD))

MAX_PKT_SIZE = 4096
PAYLOAD_SIZE = MAX_PKT_SIZE - 4

CONNECTION_TIMEOUT = 10  # seconds before connection timeout
SOCKET_TIMEOUT = 0.030  # socket.recvfrom timeout
RETRY_NUMBER = 5  # number of retries before cutting the faulty connection
WINDOW_SIZE = 10  # size of the sending window (set to 1 for stop-and-wait)

# sequence number of the first packet sent from client (don't change)
CONN_START_SEQNUM = 0
