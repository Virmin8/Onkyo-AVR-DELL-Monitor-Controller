import customtkinter as ctk

class VolumeOSD:
    def __init__(self):
        ctk.set_appearance_mode("dark")

        self.root = ctk.CTk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)

        width = 320
        height = 110

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = screen_width - width - 40
        y = screen_height - height - 120

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.frame = ctk.CTkFrame(self.root, corner_radius=20)
        self.frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.title = ctk.CTkLabel(self.frame, text="Onkyo Volume", font=("Segoe UI", 15))
        self.title.pack(pady=(8, 2))

        self.progress = ctk.CTkProgressBar(self.frame, width=250)
        self.progress.pack(pady=(0, 6))

        self.value_label = ctk.CTkLabel(self.frame, text="0", font=("Segoe UI", 18, "bold"))
        self.value_label.pack()

        self.hide_job = None  # used to cancel previous hide timer

    def show(self, volume_percent):
        volume_percent = max(0, min(100, volume_percent))

        def _update():
            # Update bar + number
            self.progress.set(volume_percent / 100)
            self.value_label.configure(text=f"{volume_percent:.1f}")

            # Show window
            self.root.deiconify()
            self.root.lift()

            # Cancel previous hide timer if holding key
            if self.hide_job:
                self.root.after_cancel(self.hide_job)

            # Set new hide timer (longer delay)
            self.hide_job = self.root.after(2000, self.root.withdraw)

        self.root.after(0, _update)