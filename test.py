import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

def main():
    # Direct image URL (converted from the Imgur page URL)
    url = "https://i.imgur.com/B40HVay.jpg"

    # Define headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        # Download the image from the URL with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error if the download fails
    except requests.exceptions.RequestException as e:
        print("Error fetching the image:", e)
        return

    # Open the image using Pillow and convert it to a format Tkinter can use
    img_data = response.content
    pil_image = Image.open(BytesIO(img_data))

    # (Optional) Resize the image if needed
    # pil_image = pil_image.resize((200, 200))

    # Create the main window
    root = tk.Tk()
    root.title("Button with Image")

    # Convert the Pillow image to a Tkinter PhotoImage
    tk_image = ImageTk.PhotoImage(pil_image)

    # Define a function to be called when the button is clicked
    def on_button_click():
        messagebox.showinfo("Button Clicked", "You clicked the button!")

    # Create a button that displays the image and triggers the function when clicked
    button = tk.Button(root, image=tk_image, command=on_button_click)
    button.pack(padx=10, pady=10)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
