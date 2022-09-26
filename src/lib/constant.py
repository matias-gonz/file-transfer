DOWNLOAD = 1
UPLOAD = 2

VALID_OPS = frozenset((DOWNLOAD, UPLOAD))

MAX_PKT_SIZE = 4096
PAYLOAD_SIZE = MAX_PKT_SIZE - 4

RETRY_DELAY = 0.6  # seconds before retry
CONNECTION_TIMEOUT = 10 * RETRY_DELAY  # seconds before connection timeout
RETRY_NUMBER = 5  # number of retries before cutting the faulty connection
WINDOW_SIZE = 10  # size of the sending window (set to 1 for stop-and-wait)

SOCKET_TIMEOUT = (
    0.030  # max time in seconds between each call to socket.recvfrom
)

# sequence number of the first packet sent from client (don't change)
CONN_START_SEQNUM = 0
