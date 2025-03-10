import tkinter as tk

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Infernal Lord UI")
    # Optionally set a fixed size or leave it to adjust automatically
    # root.geometry("300x150")

    # --- Top Bar / Title Bar ---
    top_bar_bg = "#2E3B40"  # Adjust as needed to match your desired color
    top_bar = tk.Frame(root, bg=top_bar_bg)
    top_bar.pack(side="top", fill="x")

    # Title label
    title_label = tk.Label(
        top_bar,
        text="Infernal Lord",
        bg=top_bar_bg,
        fg="white",
        font=("Helvetica", 12, "bold")
    )
    title_label.pack(side="left", padx=10, pady=5)

    # Load images (update paths if needed)
    cogwheel_img = tk.PhotoImage(file=r"C:\Users\noahs\Desktop\dreadps\assets\cogwheel.png")
    share_img    = tk.PhotoImage(file=r"C:\Users\noahs\Desktop\dreadps\assets\share.png")
    info_img     = tk.PhotoImage(file=r"C:\Users\noahs\Desktop\dreadps\assets\info.png")
    x_img        = tk.PhotoImage(file=r"C:\Users\noahs\Desktop\dreadps\assets\x.png")

    # Create icon buttons
    # (no commands assigned yet — they're placeholders)
    # Adjust button styling as desired
    cogwheel_btn = tk.Button(top_bar, image=cogwheel_img, bg=top_bar_bg,
                             borderwidth=0, highlightthickness=0,
                             activebackground=top_bar_bg)
    cogwheel_btn.pack(side="right", padx=5)

    share_btn = tk.Button(top_bar, image=share_img, bg=top_bar_bg,
                          borderwidth=0, highlightthickness=0,
                          activebackground=top_bar_bg)
    share_btn.pack(side="right", padx=5)

    info_btn = tk.Button(top_bar, image=info_img, bg=top_bar_bg,
                         borderwidth=0, highlightthickness=0,
                         activebackground=top_bar_bg)
    info_btn.pack(side="right", padx=5)

    x_btn = tk.Button(top_bar, image=x_img, bg=top_bar_bg,
                      borderwidth=0, highlightthickness=0,
                      activebackground=top_bar_bg)
    x_btn.pack(side="right", padx=5)

    # --- Main Content Area (placeholder) ---
    content_bg = "#3C4550"  # Adjust as needed
    content_frame = tk.Frame(root, bg=content_bg)
    content_frame.pack(fill="both", expand=True)

    # Just a placeholder label in the content area
    placeholder_label = tk.Label(
        content_frame,
        text="(Main UI Content Goes Here)",
        bg=content_bg,
        fg="white"
    )
    placeholder_label.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
