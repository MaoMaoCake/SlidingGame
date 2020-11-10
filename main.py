import tkinter as tk
from tkinter import messagebox
from game import SlidingGame


class mainUI:
    def __init__(self, master):
        self.master = master

        # center the selection ui
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        size = tuple(int(_) for _ in self.master.geometry().split('+')[0].split('x'))
        x = screen_width / 2 - size[0] / 2
        y = screen_height / 2 - size[1] / 2
        self.master.geometry("180x150+%d+%d" % (x - (180 / 2), y - (150 / 2)))

        # force ui to not resize
        self.master.resizable(False, False)

        # putting of all the ui element
        # put labels with text
        tk.Label(self.master, text='Sliding Game', justify="center").grid(column=2, columnspan=3, row=1)
        tk.Label(self.master, text="Size Of Grid", justify="center").grid(columnspan=3, row=2, column=2)
        tk.Label(self.master, text="width", justify="center").grid(column=1, row=10)
        tk.Label(self.master, text="height", justify="center").grid(column=1, row=11)
        tk.Label(self.master, text="difficulty", justify="center").grid(column=1, row=12)

        # entry elements
        self.width = tk.Entry(self.master)
        self.width.grid(column=2, row=10)
        self.height = tk.Entry(self.master)
        self.height.grid(row=11, column=2)

        # select difficulty
        self.difficulty = tk.StringVar()
        self.difficulty.set('normal')
        OPTIONS = ['impossible', 'expert', 'hard', 'normal', 'easy+', 'easy', 'very easy', 'idiot']
        self.difficulty_option = tk.OptionMenu(master, self.difficulty, *OPTIONS).grid(row=12, column=2)

        # bind the button
        tk.Button(self.master, text="Start", command=self.start_game).grid(column=2, row=13)

        # start the ui Loop
        self.master.mainloop()

    # command to call the main pygame window
    def start_game(self):
        # get height and width from the UI
        height, width = self.height.get(), self.width.get()

        # check the inputs for empty input and raise an error message
        if height == "" or width == "":
            messagebox.showerror("Error", "Error the required fields are empty")

        # if no error try to convert the input into an int instance
        else:
            try:
                # try to convert to int
                height, width = int(height), int(width)
                # check if height and width is a valid number ( more than 2)
                if height < 2 or width < 2:
                    # if values are not valid clear the number and show an error message
                    self.height.delete(0, "end")
                    self.width.delete(0, "end")
                    messagebox.showerror("Error", "Row or column cannot be less than 2")
                # number too big
                elif height > 5 or width > 5:
                    # if values are not valid clear the number and show an error message
                    self.height.delete(0, "end")
                    self.width.delete(0, "end")
                    messagebox.showerror("Error", "Row or column cannot be more than 5")

                else:
                    # if numbers are valid
                    # destroy the selection UI
                    self.master.destroy()
                    # call the sliding game instance with specified dimensions
                    S = SlidingGame(width=width, height=height, difficulty=self.difficulty.get())
                    S.main()
            # catch invalid value errors
            except ValueError as e:
                messagebox.showerror("Error", "There was an error \n \n {}".format(e))
                self.height.delete(0, "end")
                self.width.delete(0, "end")


# driver
root = tk.Tk()
app = mainUI(root)
