import tkinter as tk
import os
import pygame


class mainUI:
    def __init__(self, master):
        self.master = master
        self.master.geometry("225x150")
        self.master.resizable(False, False)
        tk.Label(self.master, text='Sliding Game', justify="center").grid(column=2, columnspan=3, row=1)
        tk.Label(self.master, text="Size Of Grid", justify="center").grid(columnspan=3, row=2, column=2)
        tk.Label(self.master, text="width", justify="center").grid(column=1, row=10)
        tk.Label(self.master, text="height", justify="center").grid(column=1, row=11)
        self.width = tk.Entry(self.master)
        self.width.grid(column=2, row=10)
        self.height = tk.Entry(self.master)
        self.height.grid(row=11, column=2)
        tk.Button(self.master, text="Start", command=self.start_game).grid(column=2, row=12)
        self.master.mainloop()

    def start_game(self):
        print("test")
        self.master.destroy()


root = tk.Tk()
x = mainUI(root)
