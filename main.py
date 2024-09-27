import threading
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import pyautogui
import socket
import subprocess

# print(pyautogui.KEYBOARD_KEYS)


class KeySelectionDialog(tk.Toplevel):
    """
    Represents a dialog window for selecting keys.

    Args:
        parent (tk.Tk | tk.Toplevel): The parent window for the dialog.
        button_id (str): The ID of the button for which the keys are being selected.
        current_keys (list[str]): The current keys selected for the button.

    Attributes:
        button_id (str): The ID of the button.
        current_keys (list[str]): The current keys selected for the button.
        key_options (list[str]): The available key options.
        variables (list[tk.StringVar]): The tkinter StringVars for storing selected keys.

    Methods:
        __init__(self, parent, button_id, current_keys):
            Initializes a new instance of the KeySelectionDialog class.
        save(self):
            Saves the selected keys and updates the main application's mappings.
    """
    def __init__(self, parent, button_id, current_keys):
        super().__init__(parent)
        self.button_id = button_id
        self.current_keys = current_keys
        self.key_options = ['none'] + list(pyautogui.KEYBOARD_KEYS)
        self.variables = [tk.StringVar(self) for _ in range(3)]
        self.script_var = tk.StringVar(self)
        self.script_var.set(self.master.mappings[self.button_id].get('script', ''))


        for i, var in enumerate(self.variables):
            var.set(self.current_keys[i])  # Set the current key if one exists
            tk.Label(self, text=f'Key {i+1}:').grid(row=i, column=0)
            dropdown = ttk.Combobox(self, textvariable=var, values=self.key_options)
            dropdown.grid(row=i, column=1)

        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.grid(row=4, column=1)

        tk.Label(self, text='Script:').grid(row=3, column=0)
        script_entry = ttk.Entry(self, textvariable=self.script_var)
        script_entry.grid(row=3, column=1)

        self.transient(parent)  # Set to be on top of the main window
        self.grab_set()  # Take over input focus

    def save(self):
        # Retrieve selected keys from the dropdown menus
        keys = [var.get() for var in self.variables]

        # Retrieve the script path from the entry field
        script = self.script_var.get()  # Ensure script_var is defined in __init__

        # If the button ID already exists, preserve the name (if any)
        mapping_name = self.master.mappings.get(self.button_id, {}).get('name', 'Unnamed')

        # Update the mappings for the current button_id with both keys and the script
        self.master.mappings[self.button_id] = {
            'name': mapping_name,  # Preserve or set default name
            'keys': keys,  # Save selected keys
            'script': script  # Save script path
        }

        # Save the updated mappings to the mappings.json file
        self.master.save_mappings()

        # Refresh the UI to reflect the new changes
        self.master.refresh_ui()

        # Close the dialog window
        self.destroy()


class BaseStationApp(tk.Tk):
    """

    The `BaseStationApp` class represents an application for a base station. It inherits from `tk.Tk`, which is the main window of the application.

    Attributes:
        - `mappings_listbox` (tk.Listbox): A listbox widget used to display the mappings.
        - `add_button` (ttk.Button): A button widget used to add a new mapping.
        - `mappings` (dict): A dictionary to store the mappings.
        - `log_area` (tk.Text): A text widget used to display log messages.

    Methods:
        - `__init__()`: Initializes the application, creates the necessary widgets, loads the mappings, starts the server thread, and sets up the UI.
        - `show_edit_popup(button_id, current_keys)`: Displays a popup dialog to edit the keys for a mapping.
        - `load_mappings()`: Loads the mappings from a file.
        - `save_mappings()`: Saves the mappings to a file.
        - `refresh_ui()`: Refreshes the UI by updating the mappings listbox.
        - `add_mapping()`: Adds a new mapping.
        - `emulate_key_press(button_id)`: Emulates a key press for a given button ID.
        - `edit_mapping(event)`: Handles the double-click event on a mapping in the listbox to edit the keys.
        - `handle_data(data)`: Handles the data received by the server.
        - `log_message(message)`: Logs a message to the log area.
        - `start_server()`: Starts the server thread.
        - `run_server()`: Runs the server to listen for incoming connections and data.

    Usage:
        - Create an instance of the `BaseStationApp` class to start the application.

    """
    def __init__(self):
        super().__init__()
        self.title('BaseStation')
        self.geometry('400x300')

        self.mappings_listbox = tk.Listbox(self)
        self.mappings_listbox.pack(side='top', fill='both', expand=True)
        self.mappings_listbox.bind('<Double-Button-1>', self.edit_mapping)

        self.add_button = ttk.Button(self, text='Add Mapping', command=self.add_mapping)
        self.add_button.pack(side='bottom')

        self.mappings = self.load_mappings()
        self.refresh_ui()
        self.log_area = tk.Text(self, height=10, state='disabled')
        self.log_area.pack(side='top', fill='both', expand=True)
        self.start_server()  # Start the server thread

    def show_edit_popup(self, button_id, current_keys):
        KeySelectionDialog(self, button_id, current_keys)

    def load_mappings(self):
        try:
            with open('mappings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print('Warning: The file "mappings.json" is empty or not well-formatted. A new file will be created.')
            return {}

    def save_mappings(self):
        with open('mappings.json', 'w') as f:
            json.dump(self.mappings, f, indent=4)

    def refresh_ui(self):
        self.mappings_listbox.delete(0, tk.END)
        for button_id, mapping_info in self.mappings.items():
            display_text = f"{mapping_info['name']} - {button_id} - Script: {mapping_info.get('script', 'None')}"
            self.mappings_listbox.insert(tk.END, display_text)

    def add_mapping(self):
        # Code to add new mapping
        pass

    def emulate_key_press(self, button_id):
        print(f"Emulating key press for button ID: {button_id}")

        # Retrieve the keys from the mapping
        keys = self.mappings[button_id].get('keys', [])

        # Filter out "none" keys
        valid_keys = [key for key in keys if key != "none"]

        # Emulate key press
        try:
            if len(valid_keys) == 1:
                pyautogui.press(valid_keys[0])
            elif len(valid_keys) > 1:
                pyautogui.hotkey(*valid_keys)
        except Exception as e:
            print(f"Error during key press emulation: {e}")

        # Run the associated script if one is present
        script = self.mappings[button_id].get('script', None)

        if script:
            try:
                subprocess.run(['python', script], check=True)
                print(f"Successfully ran script: {script}")
            except subprocess.CalledProcessError as e:
                print(f"Error running script: {e}")

    def edit_mapping(self, event):
        # This function is bound to the listbox item double-click event
        index = self.mappings_listbox.curselection()[0]
        button_id = self.mappings_listbox.get(index).split(' - ')[1]
        current_keys = self.mappings[button_id].get('keys', ['none', 'none', 'none'])

        # Call the function to show the edit dialog here
        self.show_edit_popup(button_id, current_keys)

    def handle_data(self, data):
        # This function is called when data is received by the server
        def update_ui(dt):
            name, id = data.split('|')
            self.log_message(f"Received: {name} - {id}")
            # Ensure there is a 'keys' entry for every button ID
            if id not in self.mappings:
                self.mappings[id] = {"name": name, "keys": ['none', 'none', 'none']}
                self.save_mappings()
                self.refresh_ui()
            else:
                self.emulate_key_press(id)  # Emulate the key press for the received ID

        # Schedule the UI update in the main thread
        self.after(0, update_ui, None)


    def log_message(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)

    # Add to the BaseStationApp class
    def start_server(self):
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('0.0.0.0', 59595))  # Ensure this matches your client's target
            server_socket.listen()
            while True:
                client_socket, addr = server_socket.accept()
                with client_socket:
                    data = client_socket.recv(1024).decode('utf-8')
                    self.handle_data(data)



if __name__ == '__main__':
    app = BaseStationApp()
    app.mainloop()

