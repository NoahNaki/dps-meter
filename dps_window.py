import requests
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import ctypes

class DPSWindow(tk.Tk):
    BAR_HEIGHT = 30
    BAR_MAX_WIDTH = 270
    BAR_SPACING = 4

    def __init__(self, aggregator):
        super().__init__()

        # -----------------------------
        # 1) BASIC WINDOW SETUP
        # -----------------------------
        # Remove OS window frame, set topmost, default geometry
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("300x350")

        # Track offsets for dragging (custom title bar)
        self._offset_x = 0
        self._offset_y = 0

        # Default out-of-combat threshold (seconds) and last combat timestamp
        self.out_of_combat_threshold = 30  # default threshold seconds
        self.last_combat_time = datetime.now()

        # -----------------------------
        # 2) CUSTOM TITLE BAR
        # -----------------------------
        top_bar_bg = "#2E3B40"
        self.custom_title_bar = tk.Frame(self, bg=top_bar_bg, height=30)
        self.custom_title_bar.pack(fill="x", side="top")

        self.custom_title_bar.bind("<Button-1>", self.start_move)
        self.custom_title_bar.bind("<B1-Motion>", self.on_move)

        self.title_label = tk.Label(
            self.custom_title_bar,
            text="Dread DPS Meter",
            fg="white",
            bg=top_bar_bg,
            font=("Helvetica", 12, "bold")
        )
        self.title_label.pack(side="left", padx=10)

        # -----------------------------
        # 3) LOAD ICONS FROM URLS
        # -----------------------------
        # Helper function to load an image from a URL
        def load_image_from_url(url, size=None):
            import requests
            from io import BytesIO
            from PIL import Image
            headers = {"User-Agent": "Mozilla/5.0"}  # Set headers to mimic a browser
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            if size:
                pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)
            return pil_image

    # Corrected URLs:
        gear_url = "https://raw.githubusercontent.com/NoahNaki/dps-meter/main/assets/gear.png"
        info_url = "https://raw.githubusercontent.com/NoahNaki/dps-meter/main/assets/infobubble.png"
        cross_url = "https://raw.githubusercontent.com/NoahNaki/dps-meter/main/assets/cross.png"
        bin_url   = "https://raw.githubusercontent.com/NoahNaki/dps-meter/main/assets/bin.png"


# Safely load each icon (16x16 as per your original code)
        try:
            cogwheel_pil      = load_image_from_url(gear_url, size=(16, 16))
            self.cogwheel_img = ImageTk.PhotoImage(cogwheel_pil)

            info_pil          = load_image_from_url(info_url, size=(16, 16))
            self.info_img     = ImageTk.PhotoImage(info_pil)

            x_pil             = load_image_from_url(cross_url, size=(16, 16))
            self.x_img        = ImageTk.PhotoImage(x_pil)

            bin_pil           = load_image_from_url(bin_url, size=(16, 16))
            self.data_cleaning_img = ImageTk.PhotoImage(bin_pil)
        except Exception as e:
            # Fallback: If any image fails to load, you can handle it here
            print(f"[DEBUG] Failed to load one of the icons: {e}")
            self.cogwheel_img      = None
            self.info_img          = None
            self.x_img             = None
            self.data_cleaning_img = None

        # -----------------------------
        # 4) TITLE BAR BUTTONS
        # -----------------------------
        self.close_button = tk.Button(
            self.custom_title_bar,
            image=self.x_img,
            bg=top_bar_bg,
            borderwidth=0,
            highlightthickness=0,
            activebackground=top_bar_bg,
            command=self.close_window
        )
        self.close_button.pack(side="right", padx=5)

        self.info_button = tk.Button(
            self.custom_title_bar,
            image=self.info_img,
            bg=top_bar_bg,
            borderwidth=0,
            highlightthickness=0,
            activebackground=top_bar_bg,
            command=self.open_info_link  # We'll define open_info_link() below
        )
        self.info_button.pack(side="right", padx=5)

        self.cogwheel_button = tk.Button(
            self.custom_title_bar,
            image=self.cogwheel_img,
            bg=top_bar_bg,
            borderwidth=0,
            highlightthickness=0,
            activebackground=top_bar_bg,
            command=self.show_settings_menu  # Opens settings via a popup menu
        )
        self.cogwheel_button.pack(side="right", padx=5)

        self.reset_png_button = tk.Button(
            self.custom_title_bar,
            image=self.data_cleaning_img,
            bg=top_bar_bg,
            borderwidth=0,
            highlightthickness=0,
            activebackground=top_bar_bg,
            command=self.reset_meter
        )
        self.reset_png_button.pack(side="right", padx=5)

        # -----------------------------
        # 5) AGGREGATOR & THEMING
        # -----------------------------
        self.aggregator = aggregator
        self.dark_mode = True
        self.bg_color = "#23242b"
        self.bar_color = "#db8d43"
        self.text_color = "#ffffff"
        self.dps_text_color = "#61dc70"

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # -----------------------------
        # 6) MAIN FRAMES
        # -----------------------------
        self.dps_frame = tk.Frame(self, bg=self.bg_color)
        self.detailed_frame = tk.Frame(self, bg=self.bg_color)
        self.settings_frame = tk.Frame(self, bg=self.bg_color)  # New settings frame

        # Build each UI
        self.build_dps_ui(self.dps_frame)
        self.build_detailed_ui(self.detailed_frame)
        self.build_settings_ui(self.settings_frame)

        # Show only the DPS frame by default
        self.dps_frame.pack(fill="both", expand=True)

        # Apply theme and start UI updates
        self.apply_theme()
        self.update_ui()

    # -----------------------------
    # 7) DRAGGABLE TITLE BAR
    # -----------------------------
    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def on_move(self, event):
        x = self.winfo_x() + event.x - self._offset_x
        y = self.winfo_y() + event.y - self._offset_y
        self.geometry(f"+{x}+{y}")

    def close_window(self):
        self.destroy()

    def minimize_window(self):
        self.update_idletasks()
        self.iconify()

    # -----------------------------
    # 8) SETTINGS / INFO MENU
    # -----------------------------
    def show_settings_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="DPS Meter Tab", command=self.switch_to_dps_meter)
        menu.add_command(label="Detailed Tab", command=self.switch_to_detailed)
        menu.add_separator()
        menu.add_command(label="Settings", command=self.switch_to_settings)
        menu.add_separator()

        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def open_info_link(self):
        import webbrowser
        webbrowser.open("https://discord.gg/dread")

    def switch_to_settings(self):
        self.dps_frame.pack_forget()
        self.detailed_frame.pack_forget()
        self.settings_frame.pack(fill="both", expand=True)
        self.geometry("300x350")

    def switch_to_dps_meter(self):
        self.detailed_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.dps_frame.pack(fill="both", expand=True)
        self.geometry("300x350")

    def switch_to_detailed(self):
        self.dps_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.detailed_frame.pack(fill="both", expand=True)
        self.geometry("700x350")

    # -----------------------------
    # 9) BUILD THE DPS UI
    # -----------------------------
    def build_dps_ui(self, container):
        top_frame = tk.Frame(container, bg=self.bg_color)
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        self.rows_frame = tk.Frame(container, bg=self.bg_color)
        self.rows_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        self.row_widgets = {}
        self.class_icons = self.load_class_icons()

    # -----------------------------
    # 10) CLASS ICONS FROM URLS
    # -----------------------------
    def load_class_icons(self):
        """
        Replace the placeholder URLs with actual links to your class icons.
        We'll do a simple resize instead of subsample for PIL images.
        """
        def load_image_from_url(url, size=None):
            import requests
            from io import BytesIO
            from PIL import Image
            response = requests.get(url)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            if size:
                pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)
            return pil_image

        try:
            # Placeholder URLs
            bm_url = "https://i.imgur.com/B40HVay.jpg"   # added .jpg
            bd_url = "https://i.imgur.com/Efuw2We.jpg"    # adjust extension if needed
            as_url = "https://i.imgur.com/eCPTk91.jpg"
            de_url = "https://i.imgur.com/FN6joij.jpg"
            fm_url = "https://i.imgur.com/6cVHqqd.jpg"
            kf_url = "https://i.imgur.com/J4Rm0ot.jpg"
            su_url = "https://i.imgur.com/bA2F5Ng.jpg"


# For each icon, load and resize to (32, 32) or whatever size you prefer
            bm_pil = load_image_from_url(bm_url, size=(32, 32))
            bd_pil = load_image_from_url(bd_url, size=(32, 32))
            as_pil = load_image_from_url(as_url, size=(32, 32))
            de_pil = load_image_from_url(de_url, size=(32, 32))
            fm_pil = load_image_from_url(fm_url, size=(32, 32))
            kf_pil = load_image_from_url(kf_url, size=(32, 32))
            su_pil = load_image_from_url(su_url, size=(32, 32))

            # Convert each PIL image to an ImageTk.PhotoImage
            bm_icon = ImageTk.PhotoImage(bm_pil)
            bd_icon = ImageTk.PhotoImage(bd_pil)
            as_icon = ImageTk.PhotoImage(as_pil)
            de_icon = ImageTk.PhotoImage(de_pil)
            fm_icon = ImageTk.PhotoImage(fm_pil)
            kf_icon = ImageTk.PhotoImage(kf_pil)
            su_icon = ImageTk.PhotoImage(su_pil)

            return {
                "Blade Master": bm_icon,
                "Blade Dancer": bd_icon,
                "Assassin": as_icon,
                "Destroyer": de_icon,
                "Force Master": fm_icon,
                "Kung Fu Fighter": kf_icon,
                "Summoner": su_icon
            }
        except Exception as e:
            print(f"[DEBUG] Error loading class icons: {e}")
            return {}

    # -----------------------------
    # 11) BUILD THE SETTINGS UI
    # -----------------------------
    def build_settings_ui(self, container):
        # Opacity Slider
        opacity_label = ttk.Label(container, text="Window Opacity:", style="CustomLabel.TLabel")
        opacity_label.pack(pady=(10, 0))

        self.opacity_scale = tk.Scale(
            container,
            from_=0.2,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            command=self.update_opacity,
            bg=self.bg_color,
            fg=self.text_color,
            highlightbackground=self.bg_color
        )
        self.opacity_scale.set(1.0)
        self.opacity_scale.pack(pady=10, padx=10, fill="x")

        # Out-of-Combat Reset Seconds Slider
        ooc_label = ttk.Label(container, text="Out-of-Combat Reset (sec):", style="CustomLabel.TLabel")
        ooc_label.pack(pady=(20, 0))

        self.ooc_scale = tk.Scale(
            container,
            from_=1,
            to=120,
            resolution=1,
            orient="horizontal",
            command=self.update_out_of_combat_threshold,
            bg=self.bg_color,
            fg=self.text_color,
            highlightbackground=self.bg_color
        )
        self.ooc_scale.set(self.out_of_combat_threshold)
        self.ooc_scale.pack(pady=10, padx=10, fill="x")

    def update_out_of_combat_threshold(self, value):
        try:
            self.out_of_combat_threshold = int(value)
        except Exception as e:
            print("Error updating out-of-combat threshold:", e)

    # -----------------------------
    # 12) BUILD THE DETAILED UI
    # -----------------------------
    def build_detailed_ui(self, container):
        columns = ("Name", "DPS", "Duration", "%Damage", "Crit%", "Highest Hit")
        self.detailed_tree = ttk.Treeview(container, style="Custom.Treeview", columns=columns, show="headings", height=10)
        self.detailed_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.detailed_tree.heading("Name", text="Name")
        self.detailed_tree.heading("DPS", text="DPS")
        self.detailed_tree.heading("Duration", text="Duration")
        self.detailed_tree.heading("%Damage", text="% Damage")
        self.detailed_tree.heading("Crit%", text="Crit %")
        self.detailed_tree.heading("Highest Hit", text="Highest Hit")

        self.detailed_tree.column("Name", width=100, anchor="center")
        self.detailed_tree.column("DPS", width=80, anchor="center")
        self.detailed_tree.column("Duration", width=80, anchor="center")
        self.detailed_tree.column("%Damage", width=80, anchor="center")
        self.detailed_tree.column("Crit%", width=60, anchor="center")
        self.detailed_tree.column("Highest Hit", width=80, anchor="center")

    # -----------------------------
    # 13) THEMING & UI UPDATES
    # -----------------------------
    def apply_theme(self):
        self.style.configure(
            "CustomNotebook.TNotebook",
            background=self.bg_color,
            borderwidth=0
        )
        self.style.configure(
            "CustomNotebook.TNotebook.Tab",
            background=self.bg_color,
            foreground=self.text_color,
            font=("Roboto", 10, "bold")
        )
        self.style.map("CustomNotebook.TNotebook.Tab",
                       background=[("selected", "#444444")],
                       foreground=[("selected", "#ffffff")]
                       )
        self.style.configure(
            "CustomFrame.TFrame",
            background=self.bg_color
        )
        self.style.configure(
            "CustomLabel.TLabel",
            background=self.bg_color,
            foreground=self.text_color,
            font=("Roboto", 10)
        )
        self.style.configure(
            "CustomCheckbutton.TCheckbutton",
            background=self.bg_color,
            foreground=self.text_color,
            font=("Roboto", 10)
        )
        self.style.configure(
            "Accent.TButton",
            foreground=self.text_color,
            background="#444444",
            font=("Roboto", 10, "bold"),
            padding=(4, 2)
        )
        self.style.map("Accent.TButton",
                       background=[("active", "#666666"), ("pressed", "#555555")]
                       )
        self.style.configure("Custom.Treeview",
                             background=self.bg_color,
                             fieldbackground=self.bg_color,
                             foreground=self.text_color)
        self.style.configure("Custom.Treeview.Heading",
                             background=self.bg_color,
                             foreground=self.text_color,
                             font=("Roboto", 10, "bold"))

        self.configure(bg=self.bg_color)
        self.update_dps_area_theme()

    def update_dps_area_theme(self):
        for actor, (row_frame, canvas) in getattr(self, "row_widgets", {}).items():
            row_frame.configure(bg=self.bg_color)
            canvas.configure(bg=self.bg_color)

    def update_opacity(self, value):
        try:
            alpha = float(value)
            self.attributes("-alpha", alpha)
        except Exception as e:
            print("Error updating opacity:", e)

    # -----------------------------
    # 14) MAIN UPDATE LOOP
    # -----------------------------
    def update_ui(self):
        stats = self.aggregator.get_stats()
        now = datetime.now()
        duration = (now - self.aggregator.global_start_time).total_seconds() if self.aggregator.global_start_time else 0

        sorted_actors = sorted(
            stats.items(),
            key=lambda x: (x[1]["total_damage"] / duration) if duration > 0 else 0,
            reverse=True
        )
        max_damage = max((data["total_damage"] for _, data in sorted_actors), default=1)

        # Check for combat activity.
        if any(data.get("events", 0) > 0 for _, data in sorted_actors):
            self.last_combat_time = now
            print(f"[DEBUG] Combat detected. Updating last_combat_time to {self.last_combat_time}.")
        else:
            time_since_last_combat = (now - self.last_combat_time).total_seconds()
            print(f"[DEBUG] No combat activity. Time since last combat: {time_since_last_combat:.2f} seconds.")
            # If we've been out-of-combat for longer than the threshold, reset the meter.
            if time_since_last_combat >= self.out_of_combat_threshold:
                print(f"[DEBUG] Out-of-combat threshold reached ({time_since_last_combat:.2f} seconds). Resetting meter.")
                self.reset_meter()
                self.last_combat_time = now

        self.update_dps_tab(sorted_actors, max_damage, duration)

        # Only update the detailed tab if it's visible.
        if self.detailed_frame.winfo_manager():
            self.update_detailed_tab(sorted_actors, duration)

        self.after(1000, self.update_ui)

    # -----------------------------
    # 15) DPS TAB
    # -----------------------------
    def update_dps_tab(self, sorted_actors, max_damage, duration):
        current_actors = set(a for a, _ in sorted_actors)
        existing_actors = set(self.row_widgets.keys())

        # Remove actors that no longer appear
        for actor in existing_actors - current_actors:
            frame, canvas = self.row_widgets[actor]
            frame.destroy()
            del self.row_widgets[actor]

        # Add/update current actors
        for actor, data in sorted_actors:
            if actor not in self.row_widgets:
                row_frame = tk.Frame(self.rows_frame, bg=self.bg_color)
                c = tk.Canvas(
                    row_frame,
                    width=self.BAR_MAX_WIDTH,
                    height=self.BAR_HEIGHT,
                    highlightthickness=0,
                    bg=self.bg_color
                )
                c.pack(side="top")
                self.row_widgets[actor] = (row_frame, c)
            else:
                row_frame, c = self.row_widgets[actor]
                row_frame.configure(bg=self.bg_color)
                c.configure(bg=self.bg_color)
                c.delete("all")

            total_damage = data["total_damage"]
            ratio = total_damage / max_damage if max_damage > 0 else 0
            bar_width = max(1, int(ratio * self.BAR_MAX_WIDTH))
            dps = total_damage / duration if duration > 0 else 0

            DPSWindow.create_rounded_rectangle(c, 0, 0, bar_width, self.BAR_HEIGHT,
                                               radius=1, fill=self.bar_color, outline="")

            actor_class = data.get("class", None)
            if actor_class and actor_class in self.class_icons:
                c.create_image(0, self.BAR_HEIGHT // 2, anchor="w", image=self.class_icons[actor_class])
                text_offset_x = 40
            else:
                text_offset_x = 5

            outline_offsets = [(1, 1)]
            for dx, dy in outline_offsets:
                c.create_text(
                    text_offset_x + dx,
                    self.BAR_HEIGHT // 2 + dy,
                    anchor="w",
                    text=actor,
                    fill="black",
                    font=("Roboto", 10, "bold")
                )
            c.create_text(
                text_offset_x,
                self.BAR_HEIGHT // 2,
                anchor="w",
                text=actor,
                fill=self.text_color,
                font=("Roboto", 10, "bold")
            )

            dps_text = f"{int(dps):,}/sec"
            dps_text_x = self.BAR_MAX_WIDTH - 5
            dps_text_y = self.BAR_HEIGHT // 2
            for dx, dy in outline_offsets:
                c.create_text(
                    dps_text_x + dx,
                    dps_text_y + dy,
                    anchor="e",
                    text=dps_text,
                    fill="black",
                    font=("Roboto", 10, "bold")
                )
            c.create_text(
                dps_text_x,
                dps_text_y,
                anchor="e",
                text=dps_text,
                fill=self.dps_text_color,
                font=("Roboto", 10, "bold")
            )

        # Re-pack actors in sorted order
        for idx, (actor, data) in enumerate(sorted_actors):
            row_frame, _ = self.row_widgets[actor]
            row_frame.pack_forget()
            row_frame.pack(fill="x", pady=(0 if idx == 0 else self.BAR_SPACING))

    # -----------------------------
    # 16) DETAILED TAB
    # -----------------------------
    def update_detailed_tab(self, sorted_actors, duration):
        for item in self.detailed_tree.get_children():
            self.detailed_tree.delete(item)

        total_damage_all = sum(data["total_damage"] for _, data in sorted_actors)

        for actor, data in sorted_actors:
            total_damage = data["total_damage"]
            events = data["events"]
            crit_events = data["crit_events"]
            highest_hit = data.get("highest_hit", 0)

            dps = total_damage / duration if duration > 0 else 0
            dmg_percent = (total_damage / total_damage_all * 100) if total_damage_all > 0 else 0
            crit_percent = (crit_events / events * 100) if events > 0 else 0

            duration_str = f"{int(duration)}s" if duration > 0 else "0s"
            dmg_percent_str = f"{dmg_percent:.1f}%"
            crit_percent_str = f"{crit_percent:.1f}%"

            self.detailed_tree.insert(
                "",
                tk.END,
                values=(
                    actor,
                    f"{int(dps):,}",
                    duration_str,
                    dmg_percent_str,
                    crit_percent_str,
                    f"{highest_hit:,}"
                )
            )

    # -----------------------------
    # 17) RESET METER
    # -----------------------------
    def reset_meter(self):
        self.aggregator.reset()
        for actor in list(self.row_widgets.keys()):
            frame, canvas = self.row_widgets[actor]
            frame.destroy()
            del self.row_widgets[actor]

    # -----------------------------
    # 18) ROUNDED RECTANGLE UTILITY
    # -----------------------------
    def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
        radius = min(radius, abs(x2 - x1) // 2, abs(y2 - y1) // 2)
        canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius,
                          start=90, extent=90, style="pieslice", **kwargs)
        canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius,
                          start=0, extent=90, style="pieslice", **kwargs)
        canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2,
                          start=270, extent=90, style="pieslice", **kwargs)
        canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2,
                          start=180, extent=90, style="pieslice", **kwargs)
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)

    # -----------------------------
    # 19) OPTIONAL: MAKE WINDOW APPWINDOW
    # -----------------------------
    def _make_window_appwindow(self):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000

        hwnd = self.winfo_id()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style |= WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        ctypes.windll.user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            0x0002 | 0x0001  # SWP_NOMOVE | SWP_NOSIZE
        )
