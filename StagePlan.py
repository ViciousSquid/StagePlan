import sys
import os

if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
elif sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
    if 'DISPLAY' in os.environ:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

import tkinter as tkinter
from tkinter import simpledialog, filedialog, colorchooser
import pickle

try:
    from networking import NetworkManager
    networking_enabled = True
except ImportError:
    networking_enabled = False

class DragNumbers(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stage Plan")
        self.geometry("620x420")
        self.configure(background="grey")
        self.dark_mode = False
        self.minsize(620, 400)
        self.is_host = False

        self.numbers = []
        self.create_black_rectangle()
        self.create_number_boxes()
        self.create_menu_bar()
        self.rectangle.bind("<Double-1>", self.create_new_number_box)

        self.label_text = tkinter.StringVar(value="Stage plan")
        self.label = tkinter.Label(self, textvariable=self.label_text, font=("Arial", 16, "bold"), background="#555555", foreground="white", padx=10, pady=5)
        self.label.place(x=10, y=10)
        self.label.bind("<Button-3>", self.rename_label)

        self.toggle_dark_mode()

        self.bind("<Configure>", self.on_window_resize)

        if networking_enabled:
            self.network_manager = NetworkManager(self)

    def rename_label(self, event):
        new_text = simpledialog.askstring("Rename Label", "Enter new label text:", parent=self, initialvalue=self.label_text.get())
        if new_text:
            self.label_text.set(new_text)

    def create_black_rectangle(self):
        self.rectangle = tkinter.Canvas(self, highlightthickness=4, highlightbackground="black")
        self.rectangle.place(x=30, y=75, width=self.winfo_width()-60, height=self.winfo_height()-150)

    def create_number_boxes(self):
        initial_positions = [
            (160, 275),
            (260, 275),
            (360, 275)
        ]

        for i, position in enumerate(initial_positions, start=1):
            self.create_new_number_box(number=str(i), position=position)

    def create_new_number_box(self, event=None, number=None, position=None):
        if not number:
            number = simpledialog.askstring("New Channel", "Enter a number:", parent=self)
            if not number or not number.isdigit() or len(number) > 2:
                return

        num_box = tkinter.Label(self, text=number, background="grey" if self.dark_mode else "white", foreground="white" if self.dark_mode else "black", relief="raised", width=3, height=1, font=("Arial", 16))
        num_box.bind("<Button-1>", self.start_drag)
        num_box.bind("<B1-Motion>", self.drag_motion)
        num_box.bind("<Button-3>", self.show_right_click_menu)

        if event is None and position is None:
            x, y = 145, 125
        elif event is not None:
            x, y = event.x - 15, event.y - 15
        else:
            x, y = position

        num_box.place(x=x, y=y)
        num_box.description = tkinter.Label(self, text="", background=num_box.cget("background"), foreground=num_box.cget("foreground"), font=("Arial", 10))
        num_box.update_idletasks()
        num_box.description.place_forget()
        self.numbers.append(num_box)

    def create_menu_bar(self):
        menu_bar = tkinter.Menu(self, tearoff=False)
        self.config(menu=menu_bar)

        file_menu = tkinter.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Layout", command=self.load_layout)
        file_menu.add_command(label="Save Layout", command=self.save_layout)

        view_menu = tkinter.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Light/Dark", command=self.toggle_dark_mode)

        network_menu = tkinter.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Network", menu=network_menu)
        network_menu.add_command(label="Start Server", command=self.start_server)
        network_menu.add_command(label="Connect to Server", command=self.connect_to_server)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        background_color = "grey" if self.dark_mode else "white"
        foreground_color = "white" if self.dark_mode else "black"
        rectangle_color = "#555555" if self.dark_mode else "white"

        self.configure(background=background_color)
        self.label.configure(background="#555555", foreground="white")
        self.rectangle.configure(background=rectangle_color, highlightbackground="black")

        for num_box in self.numbers:
            num_box.configure(background=background_color, foreground=foreground_color)
            num_box.description.configure(background=background_color, foreground=foreground_color)

    def show_right_click_menu(self, event):
        widget = event.widget
        menu = tkinter.Menu(self, tearoff=0, font=("Arial", 12))
        menu.add_command(label="Channel", command=lambda: self.change_number(widget), font=("Arial", 14, "bold"))
        menu.add_command(label="Label", command=lambda: self.add_description(widget), font=("Arial", 12))
        menu.add_command(label="Colour", command=lambda: self.change_colour(widget), font=("Arial", 12))
        menu.add_command(label="Remove", command=lambda: self.remove_number(widget), font=("Arial", 12))
        menu.tk_popup(event.x_root, event.y_root)

    def change_number(self, widget):
        current_number = widget.cget("text")
        new_number = simpledialog.askstring("Channel", "Channel number:", parent=self, initialvalue=current_number)
        if new_number and new_number.isdigit() and len(new_number) <= 2:
            widget.configure(text=new_number)
        else:
            self.hide_description(widget)

    def add_description(self, widget):
        description = simpledialog.askstring("Add Label", "Label:", parent=self)
        if description:
            widget.description.configure(text=description)
            widget.description.place(x=widget.winfo_x(), y=widget.winfo_y() + widget.winfo_height() + 5)
            index = self.numbers.index(widget)
            if networking_enabled:
                self.network_manager.send_label(index, description)
        else:
            self.hide_description(widget)

    def hide_description(self, widget):
        widget.description.configure(text="")
        widget.description.place_forget()

    def remove_number(self, widget):
        widget.place_forget()
        widget.description.place_forget()
        self.numbers.remove(widget)

    def change_colour(self, widget):
        current_color = widget.cget("background")
        new_color = colorchooser.askcolor(parent=self, initialcolor=current_color)[1]
        if new_color:
            widget.configure(background=new_color)
            widget.description.configure(background=new_color)

            brightness = self.get_brightness(new_color)
            text_color = "black" if brightness > 128 else "white"
            widget.configure(foreground=text_color)
            widget.description.configure(foreground=text_color)

    def get_brightness(self, hex_color):
        red, green, blue = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        hsp = 0.299 * red + 0.587 * green + 0.114 * blue
        return hsp

    def save_layout(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".layout")
        if file_path:
            layout_data = [(num_box.winfo_x(), num_box.winfo_y(), num_box.cget("text"), num_box.description.cget("text"), num_box.cget("background"), num_box.cget("foreground")) for num_box in self.numbers]
            with open(file_path, "wb") as file:
                pickle.dump(layout_data, file)

    def load_layout(self):
        file_path = filedialog.askopenfilename(defaultextension=".layout")
        if file_path:
            with open(file_path, "rb") as file:
                layout_data = pickle.load(file)
            for widget in self.numbers:
                widget.place_forget()
                widget.description.place_forget()
            self.numbers.clear()
            for x, y, number, description, background_color, text_color in layout_data:
                num_box = tkinter.Label(self, text=number, background=background_color, foreground=text_color, relief="raised", width=3, height=1, font=("Arial", 16))
                num_box.bind("<Button-1>", self.start_drag)
                num_box.bind("<B1-Motion>", self.drag_motion)
                num_box.bind("<Button-3>", self.show_right_click_menu)
                num_box.place(x=x, y=y)
                num_box.description = tkinter.Label(self, text=description, background=background_color, foreground=text_color, font=("Arial", 8))
                num_box.update_idletasks()
                if description:
                    num_box.description.place(x=x, y=y + num_box.winfo_height() + 5)
                else:
                    num_box.description.place_forget()
                self.numbers.append(num_box)

    def start_drag(self, event):
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y

    def drag_motion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget.startX + event.x
        y = widget.winfo_y() - widget.startY + event.y
        widget.place(x=x, y=y)
        if isinstance(widget, tkinter.Label) and hasattr(widget, "description"):
            if widget.description.cget("text"):
                widget.description.place(x=x, y=y + widget.winfo_height() + 5)
        index = self.numbers.index(widget)
        if networking_enabled:
            data = f"update_number_box:{index}:{x}:{y}"
            self.network_manager.send_data(data)

    def on_window_resize(self, event):
        self.rectangle.place_configure(width=self.winfo_width()-60, height=self.winfo_height()-150)

        if self.is_host:
            if networking_enabled:
                self.network_manager.send_window_size(self.winfo_width(), self.winfo_height())

    def update_window_size(self, width, height):
        self.geometry(f"{width}x{height}")
        self.rectangle.place_configure(width=width-60, height=height-150)

    def start_server(self):
        if networking_enabled:
            self.network_manager.start_server()
            self.is_host = True

    def connect_to_server(self):
        if networking_enabled:
            server_ip = simpledialog.askstring("Connect to Server", "Enter server IP address:", parent=self)
            if server_ip:
                self.network_manager.connect_to_server(server_ip)
                self.resizable(False, False)

    def update_label(self, index, label):
        num_box = self.numbers[index]
        num_box.description.configure(text=label)
        if label:
            num_box.description.place(x=num_box.winfo_x(), y=num_box.winfo_y() + num_box.winfo_height() + 5)
        else:
            num_box.description.place_forget()

if __name__ == "__main__":
    app = DragNumbers()
    app.mainloop()