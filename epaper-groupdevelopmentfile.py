# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan, Faizan Khan, Matthew Savage, Rory White
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
import math
import socket

# Set constant variables
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 296
PORT = 9000

# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan, Faizan Khan
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

    def get_alert_type(self, alert_string):
        alert_string = alert_string.lower()
        keyword_alert_dict = { #potentially extend to add more warnings but for now this is all we have
            "flood":"Flood",
            "flooding":"Flood",
            "torrential rain":"Flood",
             "typhoon":"Typhoon",
             "disease":"Disease",
             "virus":"Disease",
             "drought":"Drought"}
        alert_string = alert_string.lower()
        alert_warning = ""
        for keyword,alert in keyword_alert_dict.items():
            if keyword in alert_string:
                alert_warning = alert
                print(alert_warning)

        if not alert_warning:
            return alert_string
        else:
            alert_warning = alert_warning.rstrip(' ,')
            return alert_warning

# #get_alert_type("We have detected that there is a typhoons and flooding hitting the provinces")  - testing more than one hazard

    def get_severity_level(self, alert_string):
        severity_level_dict = { #potentially extend to add more warnings but for now this is all we have
            "low":1,
            "moderate":2,
            "high":3,
             "severe":4,
             "critical":5,
             "disease":3,
             "virus":4,
             "minor":1,
              "significant":3,
              "major":4,
            "negligble":1,
            "dangerous":5}
        alert_string = alert_string.lower()
        for keyword,alert in severity_level_dict.items():
            if keyword in alert_string:
                alert_warning = alert
                break
            else:
                alert_warning=1 #if we dont know the severity its just going to be given 1 for now to prevent panic
        return alert_warning

    def process_data(self, data):
        if data == '':
            print("No valid data detected")
            return
        if not '.' in data: #checking if there if the alert message doesnt stick to normal structure with a period
            alert_severity = self.get_severity_level(data)
            type_of_alert = self.get_alert_type(data)
            new_alert = {"alert_type":type_of_alert,"severity":alert_severity,"info":data}
            self.display.draw_content(new_alert)
        else:
            first_period_index = data.find('.')
            second_period_index = data.find('.',first_period_index+1)
            action_needed = data[first_period_index+1:second_period_index] # gets the info/action needed for alert
            alert = data[:first_period_index] #gets the alert message itself
            alert_severity = self.get_severity_level(alert)
            type_of_alert = self.get_alert_type(alert)
            new_alert = {"alert_type":type_of_alert,"severity":alert_severity,"info":action_needed}
            self.display.draw_content(new_alert)


# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan, Matthew Savage
#
# Class:   AlertReceiver
#
# Purpose: This class handles the receiving of a sockets signal. It also handles
#          verification of the received data and authentication.
#          This class is used by the AlertSystem class to receive data for the
#          EPaperDisplay class.
#
# Notes: 12/06 15:31 Matthew| have changed verify_connection and split its main
#                             function into two smaller functions for unit testing
#                             and fixed a bug that was stopping the code from
#                             finding the address in the array
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

    def verify_host(self, address):
        # Verify host
        intended_hosts = ['127.0.0.1', '192.168.1.1']  # Add intended hosts here
        if address not in intended_hosts:
            return False
        else:
            return True

    def verify_data(self, data):
        # Verify authentication code
        auth_code = data[:4]
        if auth_code != b"1111":
            return False
        else:
            return True

    def verify_connection(self, data, address):
        # Implement the logic to verify that the connection comes from an intended host
        # and contains the correct authentication keys
        if self.verify_data(data) and self.verify_connection(address):
            return True
        else:
            return False

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
                    else:
                        print(f"Connection from {addr} not verified or authentication failed.")
                time.sleep(1)


# ------------------------------------------------------------------------------ #
#
# Authors: Jake Dolan, Rory White
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

    def run(self):
        self.root.mainloop()

    def draw_content(self, content):
        self.canvas.delete('all')

        if content is None or not content:
            self.draw_warning()
            self.canvas.create_text(67, 224, text="General Alert \nThông báo chung \nThông báo chung.", font='System, 7', anchor='c')
            return

        if content['alert_type'] == "Flood":
            self.draw_flood()
            self.canvas.create_text(67, 224, text="Move to higher ground \ntìm kiếm vùng đất caot \nស្វែងរកដីខ្ពស់ស្វែងរកជង។  ", font='System, 7', anchor='c')
        elif content['alert_type'] == "Typhoon":
            self.draw_typhoon()
            self.canvas.create_text(67, 224, text="Seek shelter \ntìm nơi trú ẩn \nស្វែងរកដីខ្ព។  ", font='System, 7', anchor='c')
        elif content['alert_type'] == "Heatwave":
            self.draw_heatwave()
            self.canvas.create_text(67, 224, text="Avoid sun \ntiết kiệm nước \n ស្វែងរកដីខ្ព។  ", font='System, 7', anchor='c')
        elif content['alert_type'] == "Disease":
            self.draw_disease()
            self.canvas.create_text(67, 224, text="Social Distance \nKhoảng cách xã hội \nដស្វែងnរកងដងខ្ព។  ", font='System, 7', anchor='c')
        elif content['alert_type'] == "Drought":
            self.draw_drought()
            self.canvas.create_text(67, 224, text="  Save Water  \nKhoảng cách xã hội \nដស្វែងnរកងដងខ្ព។  ", font='System, 7', anchor='c')
        else:
            self.draw_warning()
            self.canvas.create_text(67, 224, text="General Alert \nThông báo chung \nThông báo chung.")



    def draw_triangle(self):
        self.canvas.delete("triangle")
        side_length = min(self.canvas_width, self.canvas_height) - 40
        height = (math.sqrt(3) / 2) * side_length
        triangle_center_x, triangle_center_y = self.canvas_width // 2, self.canvas_height // 4

        triangle_vertices = [
            (triangle_center_x, triangle_center_y - height / 2),
            (triangle_center_x - side_length / 2, triangle_center_y + height / 2),
            (triangle_center_x + side_length / 2, triangle_center_y + height / 2)
        ]

        self.canvas.create_line(*triangle_vertices[0], *triangle_vertices[1], fill='red', width=7, tags="triangle")
        self.canvas.create_line(*triangle_vertices[1], *triangle_vertices[2], fill='red', width=7, tags="triangle")
        self.canvas.create_line(*triangle_vertices[2], *triangle_vertices[0], fill='red', width=7, tags="triangle")

        return tuple(sum(triangle_vertices, ()))

    def draw_warning(self):
        # Pass triangle coordinates
        triangle_coords = self.draw_triangle()

        # Calculate triangle center
        triangle_center_x = sum(triangle_coords[::2]) // 3
        triangle_center_y = sum(triangle_coords[1::2]) // 3

        # Draw the exclamation mark
        exclamation_width, exclamation_height, exclamation_radius = 5, 30, 5
        self.canvas.create_rectangle(triangle_center_x - exclamation_width // 2, triangle_center_y - exclamation_height,
                                     triangle_center_x + exclamation_width // 2, triangle_center_y, fill="black")
        self.canvas.create_oval(triangle_center_x - exclamation_radius, triangle_center_y + 7,
                                triangle_center_x + exclamation_radius, triangle_center_y + 7 + 2 * exclamation_radius,
                                fill="black")

        # Draw the text below the triangle
        self.canvas.create_text(self.canvas_width // 2, 25 + self.canvas_height // 2,
                                text="WARNING", fill="black", font=("Arial", 16, "bold"))

        # Redraw the triangle
        self.draw_triangle()

    def draw_flood(self):
        # House and triangle coordinates
        (triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3) = self.draw_triangle()
        triangle_center_x, triangle_center_y = (triangle_x1 + triangle_x2 + triangle_x3) // 3, (
                triangle_y1 + triangle_y2 + triangle_y3) // 3
        house_size, door_height, door_width = 20, 8, 4
        house_top_left_x, house_top_left_y, house_bottom_right_x, house_bottom_right_y = triangle_center_x - house_size // 2, triangle_center_y - house_size // 2 - 6, triangle_center_x + house_size // 2, triangle_center_y + house_size // 2 - 6
        door_top_left_x, door_top_left_y, door_bottom_right_x, door_bottom_right_y = triangle_center_x - door_width // 2, triangle_center_y - door_height // 2, triangle_center_x + door_width // 2, triangle_center_y + door_height // 2
        roof_x1, roof_y1, roof_x2, roof_y2, roof_x3, roof_y3 = house_top_left_x - 5, house_top_left_y, house_bottom_right_x + 5, house_top_left_y, triangle_center_x, house_top_left_y - 12

        # Straight line coordinates
        num_segments = 10
        wave_start_x, wave_end_x = house_top_left_x - 26, house_bottom_right_x + 26
        segment_length = (wave_end_x - wave_start_x) / num_segments

        # Draw the straight lines
        for i in range(num_segments):
            x1 = wave_start_x + i * segment_length
            x2 = x1 + segment_length
            for y in [6, 13]:
                self.canvas.create_line(x1, house_bottom_right_y + y, x2, house_bottom_right_y + y, fill='black',
                                        width=3)

        # Draw the house
        for coords in [
            (house_top_left_x, house_top_left_y + 2, house_bottom_right_x, house_bottom_right_y + 2, 'black', 'black'),
            (door_top_left_x, door_top_left_y + 2, door_bottom_right_x, door_bottom_right_y + 2, 'white', 'white')]:
            self.canvas.create_rectangle(*coords[:4], outline=coords[4], fill=coords[5])

        # Draw the roof as individual lines
        self.canvas.create_line(roof_x1 + 2, roof_y1, roof_x3, roof_y3, fill='black', width=4)
        self.canvas.create_line(roof_x3, roof_y3, roof_x2 - 2, roof_y2, fill='black', width=4)
        self.canvas.create_line(roof_x1 + 2, roof_y1, roof_x2 - 2, roof_y2, fill='black', width=4)
        self.canvas.create_line(roof_x1 + 7, roof_y1 - 3, roof_x3, roof_y3 + 3, fill='black', width=6)
        self.canvas.create_line(roof_x3, roof_y3 + 3, roof_x2 - 7, roof_y2 - 3, fill='black', width=6)
        self.canvas.create_line(roof_x1 + 7, roof_y1 - 3, roof_x2 - 7, roof_y2 - 3, fill='black', width=6)

        # Draw the text below the triangle
        self.canvas.create_text(self.canvas_width // 2, 25 + self.canvas_height // 2, text="FLOOD", fill="black",
                                font=("Arial", 16, "bold"))

        # Redraw the triangle
        self.draw_triangle()

    def draw_typhoon(self):
        # Pass triangle coordinates
        (triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3) = self.draw_triangle()

        # Center of the triangle
        triangle_center_x = (triangle_x1 + triangle_x2 + triangle_x3) // 3
        triangle_center_y = (triangle_y1 + triangle_y2 + triangle_y3) // 3

        # Adjusted start point
        start_x = triangle_center_x
        start_y = triangle_center_y

        # NUmber of lines for each half of the symbol
        num_lines = 24

        # Length of each line
        line_length = 7

        # Draw half of the symbol, getting longer each time it iterates
        for i in range(num_lines):
            angle = math.radians(10 * i)
            line_end_x = start_x + line_length * math.cos(angle)
            line_end_y = start_y + line_length * math.sin(angle)
            self.canvas.create_line(start_x, start_y, line_end_x, line_end_y, width=4)
            line_length = line_length + 0.5

        # Reset the length of each line
        line_length = 7

        # Draw the other half of the symbol, getting longer each time it iterates
        for i in range(num_lines):
            angle = math.radians(-10 * i)
            line_end_x = start_x - line_length * math.cos(angle)
            line_end_y = start_y + line_length * math.sin(angle)
            self.canvas.create_line(start_x, start_y, line_end_x, line_end_y, width=4)
            line_length = line_length + 0.5

        # Draw the text below the triangle
        self.canvas.create_text(self.canvas_width // 2, 25 + self.canvas_height // 2, text="TYPHOON", fill="black",
                                font=("Arial", 16, "bold"))

        # Redraw the triangle
        self.draw_triangle()

    def draw_heatwave(self):
        # Get triangle coordinates
        triangle_coords = self.draw_triangle()
        triangle_center_x = sum(triangle_coords[::2]) // 3
        triangle_center_y = sum(triangle_coords[1::2]) // 3

        # Draw sun
        sun_radius = 13
        for i in range(0, 360, 45):
            angle_rad = math.radians(i)
            sun_x1 = triangle_center_x + sun_radius * math.cos(angle_rad)
            sun_y1 = triangle_center_y + sun_radius * math.sin(angle_rad)
            sun_x2 = triangle_center_x + (sun_radius + 5) * math.cos(angle_rad)
            sun_y2 = triangle_center_y + (sun_radius + 5) * math.sin(angle_rad)
            self.canvas.create_line(sun_x1, sun_y1, sun_x2, sun_y2, fill="black", width=5)
        self.canvas.create_oval(triangle_center_x - sun_radius, triangle_center_y - sun_radius,
                                triangle_center_x + sun_radius, triangle_center_y + sun_radius, fill="black")

        # Draw waves
        wave_amplitude, num_segments = 3, 8
        segment_length = 36 / num_segments
        for i in range(num_segments):
            wave_x1 = triangle_center_x - 18 + i * segment_length
            wave_x2, wave_y2 = wave_x1 + segment_length / 2, triangle_center_y + (wave_amplitude * (-1) ** i)
            wave_x3 = wave_x2 + segment_length / 2
            for wave_offset in (-6, 4, 14):
                self.canvas.create_line(wave_x1, triangle_center_y + wave_offset, wave_x2, wave_y2 + wave_offset,
                                        fill='red', width=2)
                self.canvas.create_line(wave_x2, wave_y2 + wave_offset, wave_x3, triangle_center_y + wave_offset,
                                        fill='red', width=2)

        # Draw text
        self.canvas.create_text(self.canvas_width // 2, 25 + self.canvas_height // 2, text="HEATWAVE",
                                fill="black", font=("Arial", 16, "bold"))

        # Redraw triangle
        self.draw_triangle()

    def draw_disease(self):
        # Pass triangle coordinates
        (triangle_x1, triangle_y1, triangle_x2, triangle_y2, triangle_x3, triangle_y3) = self.draw_triangle()

        # Function to draw disease and lines
        def draw_disease_at(center_x, center_y, radius, line_length, line_width):
            for i in range(8):
                angle = math.radians(i * 45)
                start_x = center_x + radius * math.cos(angle)
                start_y = center_y + radius * math.sin(angle)
                end_x = center_x + (radius + line_length) * math.cos(angle)
                end_y = center_y + (radius + line_length) * math.sin(angle)
                self.canvas.create_line(start_x, start_y, end_x, end_y, fill="black", width=line_width)
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                                    fill="black", outline="black")

        # Draw diseases at different positions
        draw_disease_at(triangle_x1 - 10, (triangle_y1 + triangle_y2 + triangle_y3) // 3 + 7, 9, 4, 3)
        draw_disease_at((triangle_x1 + triangle_x2 + triangle_x3) // 3 + 3, triangle_y1 + 35, 6, 3, 2)
        draw_disease_at(triangle_x1 + 13, (triangle_y1 + triangle_y2 + triangle_y3) // 3 + 5, 4, 3, 2)

        # Draw the text below the triangle
        self.canvas.create_text(self.canvas_width // 2, 25 + self.canvas_height // 2, text="OUTBREAK", fill="black",
                                font=("Arial", 16, "bold"))

        # Redraw the triangle
        self.draw_triangle()

    def draw_drought(self):
        # Get triangle coordinates
        triangle_coords = self.draw_triangle()
        triangle_center_x = sum(triangle_coords[::2]) // 3
        triangle_center_y = sum(triangle_coords[1::2]) // 3

        # Droplet coordinates
        droplet_x1 = triangle_center_x - 12
        droplet_y1 = triangle_center_y + 5
        droplet_x2 = triangle_center_x + 12
        droplet_y2 = triangle_center_y + 5
        droplet_x3 = triangle_center_x
        droplet_y3 = triangle_center_y - 15

        # Draw the droplet
        self.canvas.create_arc(triangle_center_x - 10, triangle_center_y - 5, triangle_center_x + 10,
                               triangle_center_y + 15,
                               start=180, extent=180, style='pieslice', fill="black")
        self.canvas.create_polygon(droplet_x1, droplet_y1, droplet_x2, droplet_y2, droplet_x3, droplet_y3, fill='black')

        # Draw the cross
        cross_length = 14
        self.canvas.create_line(triangle_center_x - cross_length, triangle_center_y - cross_length,
                                triangle_center_x + cross_length, triangle_center_y + cross_length, fill="red", width=4)
        self.canvas.create_line(triangle_center_x - cross_length, triangle_center_y + cross_length,
                                triangle_center_x + cross_length, triangle_center_y - cross_length, fill="red", width=4)

        # Draw the text below the triangle
        self.canvas.create_text(self.canvas_width // 2, 25 + self.canvas_height // 2, text="DROUGHT", fill="black",
                                font=("Arial", 16, "bold"))

        # Redraw the triangle
        self.draw_triangle()

    def no_alerts(self):
        self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2, text="No Alerts", fill="black", font=("Arial", 14, "bold"))


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
    display.no_alerts()
    display.run()
