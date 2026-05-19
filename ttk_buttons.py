import tkinter as tk
from tkinter import ttk

root = tk.Tk()
style = ttk.Style()
style.theme_use("clam")

style.configure("Flat.TButton", relief="flat")
style.configure("Raised.TButton", relief="raised")
style.configure("Sunken.TButton", relief="sunken")
style.configure("Ridge.TButton", relief="ridge")
style.configure("Groove.TButton", relief="groove")
style.configure("Solid.TButton", relief="solid")

for name in ["flat", "raised", "sunken", "ridge", "groove", "solid"]:
    ttk.Button(root, text=name, style=f"{name.capitalize()}.TButton").pack(pady=2)

root.mainloop()