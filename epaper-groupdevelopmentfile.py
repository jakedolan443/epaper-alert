# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan, ... (add your name here if you contributed to the file)
#
# File:    epaper-groupdevelopmentfile.py
#
# Purpose: This file is the prototype for the alert ePaper display. As this
#          file is intended for group development, it uses a simulated Tkinter display.
#          When finished, the code in this script will be optimised and translated
#          into MicroPython for running on a microcontroller + ePaper display.
#
# ------------------------------------------------------------------------------ #
import tkinter as tk
import threading
import time
import socket

# Set constant variables
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 256
PORT = 9000

# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan, ... (add your name here if you contributed to the class)
#
# Class:   AlertSystem
#
# Purpose: This is the main program class for the AlertSystem. It handles
#          the alert receiver and alert display, and processes alert data into
#          useable information for displaying.
#
# ------------------------------------------------------------------------------ #
class AlertSystem:
    def __init__(self):
        self.receiver = None  # will be attached after initialising
        self.display = None

    def attach_receiver(self, receiver):
        self.receiver = receiver

    def attach_display(self, display):
        self.display = display

    def process_data(self, data):
        # the alert format that the screen takes:
        # an alert_type e.g. "Flood"
        # a severity e.g. "1 - severe, 5 - not important"
        # info e.g. "Get to higher ground"
        new_alert = {"alert_type":"None", "severity":"5", "info":data}

        # send the newily compiled alert to the display class to be shown on screen.
        self.display.draw_content(new_alert)


# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan (add your name here if you contributed to the class)
#
# Class:   AlertReceiver
#
# Purpose: This class handles the receiving of a sockets signal. It also handles
#          verification of the received data and authentication.
#          This class is used by the AlertSystem class to receive data for the
#          EPaperDisplay class.
#
# ------------------------------------------------------------------------------ #
class AlertReceiver:
    def __init__(self, host='0.0.0.0', port=PORT):
        self.host = host
        self.port = port
        self.alert_handler = None

    def set_alert_handler(self, alert_handler):
        self.alert_handler = alert_handler

    def send_received_data(self, data):
        # Send verified data to the alert system for further processing
        self.alert_handler.process_data(data)

    def verify_connection(self, data, address):
        # Implement the logic to verify that the connection comes from an intended host
        # and contains the correct authentication keys

        # Verify host
        intended_hosts = ['127.0.0.1', '192.168.1.1']  # Add intended hosts here
        if address[0] not in intended_hosts:
            return False

        # Verify authentication code
        auth_code = data[:4]
        if auth_code != b"1111":
            return False

        return True

    def listen(self):
        # Set up a socket to listen for connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Listening on {self.host}:{self.port}...")

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if self.verify_connection(data, addr):
                        self.send_received_data(data[4:].decode())  # Remove auth code before sending
                        print(data)
                    else:
                        print(f"Connection from {addr} not verified or authentication failed.")
                time.sleep(1)



# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan, ... (add your name here if you contributed to the class)
#
# Class:   EPaperDisplayDummy
#
# Purpose: This class handles the hardware interfacing of the EPaperDisplay.
#          You may use this class to draw and interact with the display screen.
#          For development reasons, this class represents a dummy screen made
#          with Tkinter. It contains the same functions and variables as the
#          MicroPython display class that runs on the microcontroller, but it
#          allows you to simulate what the screen will look like on your PC.
#
#          IMPORTANT: As the screen is representing the ePaper screen, it may
#          not use images. It can only use the following items: text, lines,
#          rectangles. It is only able to use the colours white, black and red.
#          Please DO NOT use anything other than these elements when editing
#          the UI as it will not translate to the ePaper display.
#
# ------------------------------------------------------------------------------ #
class EPaperDisplayDummy():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("128x256 E-Ink Dummy Display")

        # Canvas dimensions
        self.canvas_width = SCREEN_WIDTH
        self.canvas_height = SCREEN_HEIGHT

        # Create canvas
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack()

        # Draw initial content on the canvas
        self.draw_content({"alert_type":"None", "severity":"1", "info":"No current alerts"})

    def run(self):
        self.root.mainloop()

    def draw_content(self, content):
        # Receives verified and processed alert data from the AlertSystem and draws it to the screen
        # The alert format is like so:
        # content['alert_type'] = "Flood", content['severity'] = 1, content['Info'] = "Seek higher ground"
        # When creating a UI, use all of this data! Please all stick to using the colours black, white and red.

        # Clear the canvas
        self.canvas.delete("all")

        # Draw a rectangle to represent the display border
        self.canvas.create_rectangle(1, 1, self.canvas_width-1, self.canvas_height-1, outline='black')

        # Draw some text
        self.canvas.create_text(self.canvas_width//2, self.canvas_height//2, text=content["info"], fill="black", font=("Arial", 10))




if __name__ == "__main__":
    # Initialises the alert systems
    alert_system = AlertSystem()

    # Create a simulated screen for the dummy paper display
    display = EPaperDisplayDummy()

    # Creates the receiving sockets class and assign the alert handler
    receiver = AlertReceiver()
    receiver.set_alert_handler(alert_system)

    # Attaches the receiver to the alert system
    alert_system.attach_receiver(receiver)

    # Attaches the display to the alert system
    alert_system.attach_display(display)

    # start the receiver thread and show the screen
    threading.Thread(target=receiver.listen, daemon=True).start()
    display.run()



