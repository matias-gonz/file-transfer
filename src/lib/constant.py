DOWNLOAD = 0
UPLOAD = 1
MAX_PKT_SIZE = 4096
PAYLOAD_SIZE = MAX_PKT_SIZE - 4

RETRY_DELAY = 0.2  # seconds before connection timeout
RETRY_NUMBER = 3   # number of retries before cutting the faulty connection
WINDOW_SIZE = 10   # size of the sending window (set to 1 for stop-and-wait)

SOCKET_TIMEOUT = 0.030  # max time in seconds between each call to socket.recvfrom

CONN_START_SEQNUM = 0  # sequence number of the first packet sent from client

FILEPATH = "../archivos de prueba/"
