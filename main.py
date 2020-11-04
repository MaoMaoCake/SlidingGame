import tkinter as tk
import os
import pygame


class mainUI:
    def __init__(self, master):
        master.geometry("900x900")
        master.resizable(False, False)
        tk.Label(master, text='Sliding Game', justify="center").grid(column=1, columnspan=6, row=1)
        tk.Label(master, text="Size Of Grid", justify="center").grid(columnspan=2, row=2)
        width = tk.Entry(master)
        width.grid(column=1, row=10)
        height = tk.Entry(master)
        master.mainloop()


root = tk.Tk()
x = mainUI(root)
