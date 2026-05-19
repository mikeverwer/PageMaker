import tkinter as tk

# Color themes
LIGHT_THEME = {
    "bg": "#ffffff",
    "fg": "#000000",
    "button_bg": "#f0f0f0",
    "entry_bg": "#ffffff"
}

DARK_THEME = {
    "bg": "#2e2e2e",
    "fg": "#ffffff",
    "button_bg": "#3e3e3e",
    "entry_bg": "#4e4e4e"
}

class DarkModeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dark Mode Toggle")
        self.geometry("300x200")
        self.theme = LIGHT_THEME

        self.label = tk.Label(self, text="Hello, Tkinter!", font=("Arial", 14))
        self.label.pack(pady=10)

        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)

        self.toggle_btn = tk.Button(self, text="Toggle Dark Mode", command=self.toggle_theme)
        self.toggle_btn.pack(pady=10)

        self.apply_theme()

    def apply_theme(self):
        self.configure(bg=self.theme["bg"])
        self.label.configure(bg=self.theme["bg"], fg=self.theme["fg"])
        self.entry.configure(bg=self.theme["entry_bg"], fg=self.theme["fg"], insertbackground=self.theme["fg"])
        self.toggle_btn.configure(bg=self.theme["button_bg"], fg=self.theme["fg"])

    def toggle_theme(self):
        self.theme = DARK_THEME if self.theme == LIGHT_THEME else LIGHT_THEME
        self.apply_theme()

if __name__ == "__main__":
    app = DarkModeApp()
    app.mainloop()