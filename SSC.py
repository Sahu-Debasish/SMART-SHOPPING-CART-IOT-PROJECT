import cv2
import numpy as np
import urllib.request
import pyzbar.pyzbar as pyzbar
import pygame
import tkinter as tk
from tkinter import ttk
import qrcode

# Initialize pygame
pygame.init()

# Define the sound file to be played when a QR code is detected
sound_file = "C:\\Users\\sahud\\Downloads\\tun file.mp3"  # Replace with the actual path to your sound file

# URL of your ESP32-CAM video stream (replace with your ESP32-CAM's actual URL)
url = 'http://192.168.137.212/cam-lo.jpg'

# Create a dictionary to store detected QR codes and their quantities
qr_code_data = {}

# Create a list to store the bill information
bill_data = []

# Define the product values
product_values = {
    "SOAP": 30,
    "BISCUIT": 50,
    "HORLICKS": 249,
    "HAIR OIL": 70,
    "T-SHIRT": 350,
    "MAGGIE": 52,
    "SAMPOO": 99,
    "PERFUME": 199,
    "BAG": 499,
}

# Your UPI ID
upi_id = "tradingdev@ybl"

# Create a function to update the total bill label
def update_bill_label():
    total = calculate_bill()
    bill_label.config(text=f"Total Bill: Rs.{total}")

# Create a function to increment quantity
def increment_quantity():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        product = item['values'][0]
        if product in qr_code_data:
            qr_code_data[product] += 1
            tree.item(selected_item, values=(product, qr_code_data[product]))
            update_bill_label()

# Create a function to decrement quantity
def decrement_quantity():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        product = item['values'][0]
        if product in qr_code_data and qr_code_data[product] > 0:
            qr_code_data[product] -= 1
            tree.item(selected_item, values=(product, qr_code_data[product]))
            update_bill_label()

# Create a function to generate a QR code with total amount and UPI ID
def generate_qr_code():
    total = calculate_bill()
    payment_info = f"upi://pay?pa={upi_id}&pn=TradingDev&mc=&tid=&tr=&tn=Total%20Bill&am={total}&cu=INR"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_info)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("payment_qr.png")
    img.show()

try:
    # Create a Tkinter window with custom styling
    root = tk.Tk()
    root.title("QR Code Scanner and Billing System")

    # Configure the style
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 16))  # Increase font size for column headings
    style.configure("Treeview", font=("Arial", 14))  # Increase text size for the table

    # Create a treeview widget for displaying the scanned QR code data
    tree = ttk.Treeview(root, columns=("Product", "Quantity"))
    tree.heading("#1", text="Product")
    tree.heading("#2", text="Quantity")
    tree.pack()

    # Create and configure a scrollbar for the treeview
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Create a label to display the total bill
    bill_label = tk.Label(root, text="Total Bill: Rs.0", font=("Arial", 16))  # Increase text size for the label
    bill_label.pack()

    # Create an "Increment" button to increase quantity (styled in green)
    increment_button = ttk.Button(root, text="PRODUCT ADD ++", command=increment_quantity, style="TButton")
    style.map("TButton", foreground=[("active", "blue")])
    increment_button.pack()

    # Create a "Decrement" button to decrease quantity (styled in red)
    decrement_button = ttk.Button(root, text="PRODUCT REMOVE --", command=decrement_quantity, style="TButton")
    style.map("TButton", foreground=[("active", "red")])
    decrement_button.pack()

    # Create a "Generate QR Code" button to generate the payment QR code
    generate_qr_button = ttk.Button(root, text="PAY BILL", command=generate_qr_code, style="TButton")
    style.map("TButton", foreground=[("active", "green")])
    generate_qr_button.pack()

    while True:
        # Open the video stream from the ESP32-CAM
        cap = cv2.VideoCapture(url)

        while True:
            ret, frame = cap.read()  # Read a frame from the video stream
            if not ret:
                break

            # Scan for QR codes in the frame
            decoded_objects = pyzbar.decode(frame)

            # Process and append detected QR code data
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                if qr_data not in qr_code_data:
                    qr_code_data[qr_data] = 0
                    # Play the sound when a QR code is detected
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.play()
                    # Display the detected QR code in the treeview
                    tree.insert("", "end", values=(qr_data, qr_code_data[qr_data]))
                    update_bill_label()

except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cap' in locals():
        cap.release()  # Release the video stream
    root.mainloop()
