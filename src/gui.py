#!/usr/bin/python

import os
import subprocess
from Tkinter import Tk
from Tkinter import Label
from Tkinter import Entry
from Tkinter import Button
from Tkinter import StringVar
from Tkinter import N, S, E, W
import tkFileDialog

def select_directory_callback():
    download_directory = tkFileDialog.askdirectory()
    if download_directory:
        E_path_text.set(download_directory)

def set_default_directory():
    E_path_text.set(os.getcwd()+'/'+E_username.get())
    def cancel(event):
        top.after_cancel(path_update_id)
    B_path_select.bind("<Button-1>", cancel)
    E_path.bind("<Button-1>", cancel)
    path_update_id = top.after(100, set_default_directory)

def start_callback():
    count = 0

    command = ' '.join(['python', os.getcwd()+'/run.py', '--dest',
        E_path.get(), E_username.get()])

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    print command

    # # Monitor the subprocess' stdout and count the files downloaded
    # queue = Queue()
    # thread = Thread(target=start_callback)
    # thread.start()

    # while proc.poll() is None:
    #     queue.put(proc.stdout.readline())

    # def update_lines():
    #     try:
    #         line = queue.get(False)
    #         L_downloads = Label(top, text=str(randint(0, 9)))
    #         L_downloads.grid(row=2, column=1)
    #     except Empty:
    #         pass

    #     if proc.poll() is None:
    #         top.after(100, update_lines)

    # top.after(100, update_lines)


top = Tk()
top.title('Instagram Downloader')
top.update_idletasks()


# Username or url label and entry box
L_username = Label(top, text="Username or url")
L_username.grid(row=0, column=0, sticky=N+S+E+W)

E_username_text = StringVar()
E_username = Entry(top, bd=2, textvariable=E_username_text)
E_username.grid(row=0, column=1, columnspan=2, sticky=N+S+E+W)


# Download path label, file browser button, and download path entry box
L_path = Label(top, text="Download path")
L_path.grid(row=1, column=0, sticky=N+S+E+W)

B_path_select = Button(top, text="...", command=select_directory_callback)
B_path_select.grid(row=1, column=1, sticky=N+S+E+W)

E_path_text = StringVar()
E_path_text.set(os.getcwd()+'/')
E_path = Entry(top, bd=2, textvariable=E_path_text)
E_path.grid(row=1, column=2)


# Start button
# L_downloads = Label(top, text='Downloaded:')
# L_downloads.grid(row=2, column=0)

# L_downloads = Label(top, text='0')
# L_downloads.grid(row=2, column=1)

B_start = Button(top, text="Go", command=start_callback)
# B_start.grid(row=2, column=2, sticky=N+S+E+W)
B_start.grid(row=2, column=0, columnspan=3, sticky=N+S+E+W)


# # Stdout from the run.py subprocess
# T_stdout = Text(top)
# T_stdout.grid(row=4, column=0, columnspan=3, sticky=N+S+E+W)


# Main loop
path_update_id = top.after(100, set_default_directory)
top.mainloop()