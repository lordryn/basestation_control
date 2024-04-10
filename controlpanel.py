import os
import json
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.button import Button
from kivy.uix.button import Button
import math
import secrets
import socket
from kivy.clock import Clock

KV = '''
BoxLayout:
    orientation: "vertical"
    MDTopAppBar:
        title: "Control Panel"
        pos_hint: {"top": 1}
        elevation: 10
        right_action_items: [["content-save", lambda x: app.save_layout()], ["plus", lambda x: app.add_button_dialog()]]
    MDTabs:
        id: tabs
'''


class TabContent(MDBoxLayout):
    """
    TabContent
    ==========

    Subclass of MDBoxLayout that represents the content for a tab in an application.

    Attributes
    ----------
    grid_layout : MDGridLayout
        The grid layout for the tab content.

    Methods
    -------
    __init__(**kwargs)
        Initializes the TabContent instance.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to initialize the MDBoxLayout.

    add_button(button_name, button_id)
        Adds a button to the tab content.

        Parameters
        ----------
        button_name : str
            The name of the button.
        button_id : str
            The identifier of the button.

        Returns
        -------
        button : MDRaisedButton
            The added button.
    """

    def __init__(self, **kwargs):
        super(TabContent, self).__init__(**kwargs)
        self.grid_layout = MDGridLayout(size_hint=(1, 1))
        self.add_widget(self.grid_layout)

    def add_button(self, button_name, button_id):
        button = MDRaisedButton(text=f"{button_name}\n{button_id}", id=button_id, size_hint=(.2, .1))
        self.grid_layout.add_widget(button)
        return button

class Tab(MDBoxLayout, MDTabsBase):
    """

    Tab Class
    =========

    This class represents a tab in a tabbed layout.

    It inherits from `MDBoxLayout` and `MDTabsBase`.

    Methods
    -------
    - `__init__(**kwargs)`: Initializes a new instance of the Tab class.
    - `add_widget(widget)`: Adds a widget to the tab's content.
    - `remove_widget(widget)`: Removes a widget from the tab's content.

    Attributes
    ----------
    - `contents`: A list of the widgets currently added to the tab's content.
    - `tab_label`: The label displayed for the tab.

    Examples
    --------
    Create a tab and add a widget to its content::

        tab = Tab(tab_label='Tab 1')
        widget = Widget()
        tab.add_widget(widget)

    Remove a widget from the tab's content::

        tab.remove_widget(widget)

    """


class ControlPanelApp(MDApp):
    """

    :class: ControlPanelApp

    This class represents a control panel application.

    :attribute base_station_ip: A string representing the IP address of the base station. Default value is '192.168.1.235'.
    :attribute base_station_port: An integer representing the port number of the base station. Default value is 59595.
    :attribute layout_file: A string representing the path to the layout file. Default value is 'layout.json'.

    :method build(self) -> Built:
        This method is responsible for building the user interface of the application. It returns a built layout.

    :method on_start(self) -> None:
        This method is called when the application starts. It initializes the tabs in the user interface and loads the layout.

    :method print_widget_tree(self, widget: Widget, indent: int) -> None:
        This method recursively prints the widget tree starting from the given widget.

    :method add_button_dialog(self) -> None:
        This method opens a dialog for adding a new button.

    :method add_button(self, instance: Object) -> None:
        This method adds a button to the current tab with the given button name and generates a unique button ID.

    :method add_button_to_layout(self, button_name: str, button_id: str, tab: Tab) -> None:
        This method adds a button with the given name and ID to the specified tab.

    :method find_buttons_in_children(self, parent: Widget) -> List[Button]:
        This method recursively finds all buttons in the children of the given parent widget.

    :method save_layout(self) -> None:
        This method saves the current layout to a file.

    :method load_layout(self) -> None:
        This method loads the layout from the layout file.

    :method load_buttons(self) -> None:
        This method loads the buttons from the loaded layout and adds them to the respective tabs.

    :method adjust_grid_layout(self, grid_layout: GridLayout) -> None:
        This method adjusts the grid layout based on the number of buttons.

    :method send_button_data(self, button_id: str, button_name: str) -> None:
        This method sends button data to the base station.

    """
    base_station_ip = '192.168.1.235'
    base_station_port = 59595
    layout_file = 'layout.json'

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        for i in range(1, 13):
            tab = Tab()
            tab.title = f"Page {i}"
            content = TabContent()
            tab.add_widget(content)
            self.root.ids.tabs.add_widget(tab)
            print(f"Added TabContent to tab with title '{tab.title}'")  # Debugging print statement.
        Clock.schedule_once(lambda dt: self.load_layout(), 0)

    def print_widget_tree(self, widget, indent=0):
        print(' ' * indent + str(widget))
        for child in widget.children:
            self.print_widget_tree(child, indent + 2)

    def add_button_dialog(self):
        self.dialog = MDDialog(
            title="Add a New Button",
            type="custom",
            content_cls=MDTextField(hint_text="Button name"),
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Add", on_release=self.add_button)
            ],
        )
        self.dialog.open()

    def add_button(self, instance):
        button_name = self.dialog.content_cls.text
        button_id = secrets.token_hex(5)
        if button_name:
            current_tab = self.root.ids.tabs.get_current_tab()
            print(f"Current tab is: {current_tab.title}")  # note the .title here

            self.add_button_to_layout(button_name, button_id, current_tab)

        self.dialog.dismiss()

    def add_button_to_layout(self, button_name, button_id, tab):
        print(
            f"Adding button with name '{button_name}' and id '{button_id}' to tab with title '{tab.title}'")  # Debugging print statement.
        tab_content = tab.children[0]  # Get TabContent instance from Tab
        button = tab_content.add_button(button_name, button_id)
        button.bind(on_release=lambda x: self.send_button_data(button_id, button_name))
        self.adjust_grid_layout(tab_content.grid_layout)

    def find_buttons_in_children(self, parent):
        buttons = []
        for child in parent.children:
            if isinstance(child, MDRaisedButton):
                buttons.append(child)
            buttons += self.find_buttons_in_children(child)
        return buttons

    def save_layout(self):
        layout = {}
        for i, tab in enumerate(self.root.ids.tabs.carousel.slides):
            layout[i] = {'title': tab.title, 'buttons': []}
            for button in self.find_buttons_in_children(tab.children[0]):
                layout[i]['buttons'].append({'text': button.text})
        with open(self.layout_file, 'w') as f:
            json.dump(layout, f)

    def load_layout(self):
        if os.path.exists(self.layout_file):
            with open(self.layout_file, 'r') as f:
                self.layout = json.load(f)
                Clock.schedule_once(lambda dt: self.load_buttons(), 1)

    def load_buttons(self):
        for i, tab_info in self.layout.items():
            if int(i) < len(self.root.ids.tabs.get_tab_list()):
                tab_label = self.root.ids.tabs.get_tab_list()[int(i)]
                print(f"Loading buttons to tab with title '{tab_label.text}'")  # Debugging print statement
                slide = self.root.ids.tabs.carousel.slides[int(i)]  # Get corresponding slide (Tab instance)
                tab_content = slide.children[0]  # Get TabContent instance from Tab
                button_info_list = tab_info.get('buttons', [])
                if isinstance(button_info_list, list):
                    for button_info in button_info_list:
                        button_name, button_id = button_info['text'].split("\n")
                        self.add_button_to_layout(button_name, button_id, slide)  # Pass slide (Tab) instance

    def adjust_grid_layout(self, grid_layout):
        button_count = len(grid_layout.children)
        columns = 3 if button_count > 6 else 2
        grid_layout.cols = columns
        rows = math.ceil(button_count / columns)
        size_hint_y = 1 / rows if rows else 1
        for button in grid_layout.children:
            button.size_hint_y = size_hint_y
            button.size_hint_x = 1 / columns

    def send_button_data(self, button_id, button_name):
        data = f"{button_name}|{button_id}".encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.base_station_ip, self.base_station_port))
                sock.sendall(data)
                print("Data sent to Base Station successfully.")
            except Exception as e:
                print(f"Could not send data to Base Station: {e}")


ControlPanelApp().run()
