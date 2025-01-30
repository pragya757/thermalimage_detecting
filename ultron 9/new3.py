import cv2
import tkinter as tk
from tkinter import Label, Button, Toplevel
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import numpy as np
import mysql.connector

# Initialize MySQL database connection
def connect_to_db():
    try:
        # Replace with your MySQL credentials
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="disease_detection"
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

# Function to match temperature with diseases from MySQL
def match_disease(temperature):
    conn = connect_to_db()
    if not conn:
        return "Database connection failed"
    
    cursor = conn.cursor()
    
    query = '''
    SELECT disease_name, symptoms FROM diseases
    WHERE min_temp <= %s AND max_temp >= %s
    '''
    cursor.execute(query, (temperature, temperature))
    
    matched_diseases = cursor.fetchall()
    conn.close()

    if matched_diseases:
        result = "\n".join([f"{disease[0]}: {disease[1]}" for disease in matched_diseases])
        return result
    else:
        return "No disease detected"

# Function to create pop-up window showing results
def show_result_popup(temperature, disease_result):
    result_window = Toplevel()
    result_window.title("Detection Results")

    Label(result_window, text=f"Detected Temperature: {temperature}\u00b0C", font=("Arial", 14)).pack(pady=10)
    Label(result_window, text=f"Disease Result:\n{disease_result}", font=("Arial", 14)).pack(pady=10)

    Button(result_window, text="Close", command=result_window.destroy, font=("Arial", 12), bg="red", fg="white").pack(pady=5)

# Rest of your code remains the same...

# Initialize webcam
webcam = cv2.VideoCapture(0)
if not webcam.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Create necessary folders
image_folder = "captured_images"
os.makedirs(image_folder, exist_ok=True)

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Initialize Tkinter window
root = tk.Tk()
root.title("Thermal Vision Camera with Temperature Detection")
video_label = Label(root)
video_label.pack()

image_counter = 1

# Function to apply thermal filter
def apply_custom_thermal_filter(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    return cv2.applyColorMap(enhanced_gray, cv2.COLORMAP_JET)

# Function to map color to temperature
def map_color_to_temperature(color):
    blue, green, red = color
    blue_norm = blue / 255.0
    green_norm = green / 255.0
    red_norm = red / 255.0

    if blue_norm > green_norm and blue_norm > red_norm:
        temperature = 20 + (blue_norm * 10)
    elif green_norm > blue_norm and green_norm > red_norm:
        temperature = 30 + (green_norm * 7)
    elif red_norm > blue_norm and red_norm > green_norm:
        temperature = 37 + (red_norm * 8)
    else:
        temperature = 37 + (green_norm * 2)
    
    return round(temperature, 1)

# Function to detect full face temperature
def detect_full_face_temperature(image_path, thermal_frame):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(40, 40))
    font = cv2.FONT_HERSHEY_SIMPLEX

    global image_counter
    detected_temperature = None  # Store detected temperature

    if len(faces) > 0:
        for (x, y, w, h) in faces:
            full_face_roi = thermal_frame[y:y+h, x:x+w]  # Extract full face region
            avg_color = np.mean(full_face_roi, axis=(0, 1))  # Get average color of the full face
            avg_temperature = map_color_to_temperature(avg_color)  # Map color to temperature
            detected_temperature = avg_temperature  # Store detected temperature
            
            # Draw rectangle around face
            cv2.rectangle(thermal_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Display temperature on screen
            cv2.putText(thermal_frame, f"Temp: {avg_temperature}\u00b0C", (x, y-10), font, 0.7, (255, 255, 255), 2)
        
        detected_path = os.path.join(image_folder, f"temperature_detected_{image_counter}.png")
        cv2.imwrite(detected_path, thermal_frame)
        print(f"Temperature detected: {detected_temperature}\u00b0C, saved as '{detected_path}'.")
    else:
        print("No face detected.")

    return detected_temperature  # Return detected temperature

# Function to capture image and update GUI
def capture_image():
    print("Capture button pressed!")  # Debugging line
    global image_counter
    filename = os.path.join(image_folder, f"captured_image_{image_counter}.png")
    cv2.imwrite(filename, thermal_frame)
    detected_temperature = detect_full_face_temperature(filename, thermal_frame.copy())

    if detected_temperature is not None:
        matched_disease = match_disease(detected_temperature)

        # Display pop-up window with result
        show_result_popup(detected_temperature, matched_disease)

        # Print detected temperature and disease information to the terminal
        print(f"Detected Temperature: {detected_temperature}\u00b0C")
        print(f"Disease Result: {matched_disease}")
        print("-" * 50)

    image_counter += 1

# Function to update the video frame
def update_frame():
    global thermal_frame
    grabbed, frame = webcam.read()
    if not grabbed:
        return
    thermal_frame = apply_custom_thermal_filter(frame)
    img = cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(image=img)
    video_label.img_tk = img_tk
    video_label.configure(image=img_tk)
    root.after(10, update_frame)

# Create capture button
capture_button = Button(root, text="Capture", command=capture_image, font=("Arial", 14), bg="blue", fg="white")
capture_button.pack(pady=5)

# Start updating the frame
update_frame()
root.mainloop()

# Release resources
webcam.release()
cv2.destroyAllWindows()
