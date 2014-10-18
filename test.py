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
    print 'Connected to Dymo'
    while True:
        data = h.read(6)
        if data:
            global grams
            grams = data[4] + (256 * data[5])
            WebSocketsHandler.send('grams ' + str(grams))
        time.sleep(0.1)

scale_thread = threading.Thread(target=scale_function)
scale_thread.setDaemon(True)
scale_thread.start()



ser = serial.Serial('/dev/tty.usbserial-A700dZCr', 9600, timeout=1)
print 'Connected to Arduino'



old_buttons = '111111111'
def onPush(category):
    WebSocketsHandler.send('enter ' + category)
    turnOnOnlyLight(category)

lights = {'dairy': (0, 1),
     'animal': (2, 3),
     'fruit': (4, 5),
     'meal': (6, 7),
     'grains': (8, 9),
     'vegetables': (10, 11),
     'thumbup': (12, 13),
     'thumbmid': (14, 15),
     'thumbdown': (16, 17),
    }

def turnOnOnlyLight(category):
    for cat in lights:
        setLight(cat, False)

    setLight(category, True)

def setLight(category, on):
    b = lights[category][0 if on else 1]
    ser.write([b])


# Read buttons
try:
    while True:
        print grams
        if grams > 1500:
            ser.write([27]) # Red
        else:
            ser.write([23]) # Green

        ser.write([22]) # Four lights


        # Read buttons
        ser.write([28])
        buttons = ser.read(9)
        for i in range(9):
            if old_buttons[i] == '1' and buttons[i] == '0':
                category = ['dairy', 'animal', 'fruit', 'meal', 'grains', 'vegetables', 'thumbup', 'thumbmid', 'thumbdown'][i]
                onPush(category)

        old_buttons = buttons
except KeyboardInterrupt:
    print 'Shutting down'
    server.shutdown()

    ser.close()

