import hid, time, serial, SocketServer, threading
from webserversocket import WebSocketsHandler

grams = 0

# Server function
server = None
def server_function():
    global server
    server = SocketServer.TCPServer(("localhost", 9999), WebSocketsHandler)
    print 'Serving'
    server.serve_forever()

server_thread = threading.Thread(target=server_function)
server_thread.setDaemon(True)
server_thread.start()

# Scale

def scale_function():
    h = hid.device(0x0922, 0x8005)
    h.set_nonblocking(True)
    data_ack = False
    while True:
        data = h.read(6)
        if data:
            if not data_ack:
                print 'Connected to Dymo'
                data_ack = True

            global grams
            grams = data[4] + (256 * data[5])
            print 'grams:', grams
            WebSocketsHandler.send('grams ' + str(grams))
        time.sleep(0.1)

scale_thread = threading.Thread(target=scale_function)
scale_thread.setDaemon(True)
scale_thread.start()



ser = serial.Serial('/dev/tty.usbserial-AD01Z760', 9600, timeout=1000)
print 'Connected to Arduino'


def onPush(category):
    print 'entered', category
    WebSocketsHandler.send('enter ' + category)

# Read buttons
try:
    while True:
        s = ser.read()
        if s == '1':
            onPush('meat')
        if s == '2':
            onPush('fruit')

except KeyboardInterrupt:
    print 'Shutting down'
    server.shutdown()

    ser.close()

