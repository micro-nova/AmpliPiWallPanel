from app import displayserial


class DropDown:
    """
    Logic for operating dropdown selection pages on the display.
    first_field_id: the id of the first text field component. the fields must be in order from least to greatest
    field_objname_prefix: the object name of the text field components without the number. e.g: "tssid" could be
       field_objname_prefix where and example of an actual field's name in nextion would be "tssid0"
    up_button_id: the id of the up button
    down_button_id: the id of the down button
    num_fields: the number of fields on the page for the dropdown menu
    """
    def __init__(self, page_name, first_field_id, field_objname_prefix, up_button_id, down_button_id, loading_text_id, num_fields):
        self.page_name = page_name
        self.first_field_id = first_field_id
        self.field_objname_prefix = field_objname_prefix
        self.up_button_id = up_button_id
        self.down_button_id = down_button_id
        self.loading_text_id = loading_text_id
        self.num_fields = num_fields

        self.callbacks = []
        self.items = []
        self.selected_index = -1
        self.selected_string = ''
        self.start_index = 0

    # clears and populates the items list
    # items must be a list of strings
    def populate(self, items):
        """Clears and populates the items list. Items must be a list of strings."""
        self.start_index = 0
        self.items.clear()
        self.items.extend(items)
        self.__update_fields()

    def set_loading_state(self):
        """Manipulates the display to show a loading state."""
        # make all fields invisible
        for i in range(self.num_fields):
            displayserial.set_visible(i + self.first_field_id, False)

        # make buttons invisible
        displayserial.set_visible(self.up_button_id, False)
        displayserial.set_visible(self.down_button_id, False)

        # make loading text visible
        displayserial.set_visible(self.loading_text_id, True)

    def add_item_index_callback(self, callb):
        """callb is a lambda one argument and no return value. Adds callb to a list of callbacks that is called
        when the user selects an option from the list."""
        self.callbacks.append(callb)

    def set_selected_string(self, selected_string):
        self.selected_string = selected_string
        # compute index of selected string
        try:
            self.selected_index = self.items.index(selected_string)
        except ValueError:
            self.selected_index = -1

    # def get_string_from_index(self, index):
    #     return

    # handles a serial message from the display
    def handle_message(self, message):
        """Receives a message from the display and processes it. Should only be
        passed messages that are relevant to the page that contains the instance of DropDown."""
        if message[0] == displayserial.BUTTON_MESSAGE and message[3] == displayserial.PRESSED_EVENT:
            id = message[2]
            if id in range(self.first_field_id, self.first_field_id + self.num_fields):
                # grab the selection's index and string
                self.selected_index = self.start_index + id - self.first_field_id
                self.selected_string = self.items[self.selected_index]
                print(message)
                for c in self.callbacks:
                    c(self.selected_index)
            elif id == self.up_button_id:
                self.__on_up()
            elif id == self.down_button_id:
                self.__on_down()

    def __on_up(self):
        self.start_index -= 3
        if self.start_index < 0:
            self.start_index = 0
        self.__update_fields()

    def __on_down(self):
        self.start_index += 3
        if self.start_index > len(self.items) - self.num_fields:
            self.start_index = len(self.items) - self.num_fields
        self.__update_fields()

    def __update_fields(self):
        num_items = len(self.items)
        print(f'{num_items} items in dropdown list.')

        # make loading text invisible
        displayserial.set_visible(self.loading_text_id, False)

        # update field visibility
        for i in range(self.num_fields):
            if i in range(num_items, self.num_fields):
                displayserial.set_visible(i + self.first_field_id, False)
            else:
                displayserial.set_visible(i + self.first_field_id, True)

        # # make sure all fields are visible
        # for i in range(self.num_fields):
        #     displayserial.set_visible(i + self.first_field_id, True)
        #
        # # if there are less than num_fields, disable unnecessary fields
        # if num_items < self.num_fields:
        #     for i in range(num_items, self.num_fields):
        #         displayserial.set_visible(i + self.first_field_id, False)

        # populate fields
        for i in range(min(self.num_fields, num_items)):
            field_string = self.items[i + self.start_index]
            self.__set_field_txt(i, field_string)

        # since we just changed the state of the displayed dropdown,
        # we need to update the up/down button visibilities
        self.__update_button_vis()

    def __update_button_vis(self):
        if self.start_index == 0:
            # make up button invisible
            displayserial.set_visible(self.up_button_id, False)
        else:
            # make up button visible
            displayserial.set_visible(self.up_button_id, True)
        # if self.start_index == len(self.items) - self.num_fields or len(self.items) <= self.num_fields:
        if self.start_index >= len(self.items) - self.num_fields:
            # make down button invisible
            displayserial.set_visible(self.down_button_id, False)
        else:
            # make down button visible
            displayserial.set_visible(self.down_button_id, True)

    def __field_name_from_index(self, index):
        return f'{self.field_objname_prefix}{index}'

    def __set_field_txt(self, index, txt):
        displayserial.set_component_txt(self.page_name, self.__field_name_from_index(index), txt)


