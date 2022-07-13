from telebot import types


class FindObject:
    def __init__(self, bot, markups, inline_markups, db_repo, command_start):
        self.bot = bot
        self.markups = markups
        self.inline_markups = inline_markups
        self.db_repo = db_repo
        self.command_start = command_start
        self.property_object_menu_handler = None

    def set_property_object_menu_handler(self, prop_obj):
        self.property_object_menu_handler = prop_obj

    def get_service_type(self, message):
        self.bot.send_message(
            message.from_user.id,
            "Please, choose the service type",
            reply_markup=self.markups.get_service_type_markup(),
        )
        self.bot.register_next_step_handler(message, self.process_getting_service_type)

    def process_getting_service_type(self, message):
        if not message.content_type == "text":
            self.get_service_type(message)

        current_object = {}

        if message.text == "Rent":
            current_object["service type"] = "rent"
        elif message.text == "Sale":
            current_object["service type"] = "sale"
        else:
            self.get_service_type(message)
            return
        self.get_city(message, current_object)

    def get_city(self, message, current_object):
        page = 1
        cur_message = "Please, choose the city in which property is located..\n"
        cur_message += f"Service Type: {current_object['service type']}\n"
        cities_string, list_len = self.__get_cities_string_by_page(
            self.db_repo.get_all_cities_names(), page
        )
        cur_message += cities_string

        self.bot.send_message(
            message.from_user.id,
            cur_message,
            reply_markup=self.inline_markups.find_object_cities_inline_markup(list_len),
            parse_mode="HTML",
        )

    def edit_get_city_message(self, call):
        page, page_count = self.__get_page_and_page_count_in_message_text(
            call.message.text
        )
        factor = 1
        if call.data == "find_object_city_prev":
            factor *= -1

        if page + factor > page_count or page + factor <= 0:
            return

        cur_message = "Please, choose the city in which property is located..\n"
        cur_message += f"Service type: {self.__get_service_type_in_message_text(call.message.text)}\n"
        cities_string, list_len = self.__get_cities_string_by_page(
            self.db_repo.get_all_cities_names(), page + factor
        )
        cur_message += cities_string

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            text=cur_message,
            message_id=call.message.id,
            reply_markup=self.inline_markups.find_object_cities_inline_markup(list_len),
        )

    def get_city_callback_handler(self, call):
        if call.data == "find_object_city_prev" or call.data == "find_object_city_next":
            self.edit_get_city_message(call)
            return
        else:
            page, service_type = self.__parse_message(call.message.text)
            city_name = self.db_repo.get_city_name_by_index(
                page * 10 - 10 + int(call.data.split("_")[-1])
            )
            self.bot.delete_message(call.message.chat.id, call.message.id)
            current_object = {"service type": service_type, "city": city_name}
            self.choose_finding_method(call.message, current_object)

    def choose_finding_method(self, message, current_object):
        self.bot.send_message(
            message.chat.id,
            "Please choose the filter that you want to apply",
            reply_markup=self.markups.chose_additional_filters(),
        )
        self.bot.register_next_step_handler(
            message, self.process_choosing_finding_method, current_object
        )

    def process_choosing_finding_method(self, message, current_object):
        if not message.content_type == "text":
            self.choose_finding_method(message, current_object)
            return

        if message.text == "Find by Location":
            self.get_approx_location(message, current_object)
        elif message.text == "Show All My Objects":
            self.get_objects_to_display(message, current_object, method="all")

        elif message.text == "Find By Id":
            self.get_object_id(message, current_object)
        else:
            self.choose_finding_method(message, current_object)

    def get_object_id(self, message, current_object):
        self.bot.send_message(message.chat.id, "Please, send ID of the object")
        self.bot.register_next_step_handler(
            message, self.process_getting_id, current_object
        )

    def process_getting_id(self, message, current_object):
        if not message.content_type == "text":
            self.process_getting_id(message, current_object)
            return

        if message.text.strip():
            current_object["id"] = message.text.strip()
            current_object["manager"] = message.from_user.username
            self.get_objects_to_display(message, current_object, method="id")

    def get_approx_location(self, message, current_object):
        self.bot.send_message(
            message.chat.id, "Please send approximate location of object"
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_approx_location, current_object
        )

    def process_getting_approx_location(self, message, current_object):
        if not message.content_type == "location":
            self.get_approx_location(message, current_object)
            return

        current_object["location"] = (
            message.location.latitude,
            message.location.longitude,
        )
        self.get_radius(message, current_object)

    def get_radius(self, message, current_object):
        self.bot.send_message(
            message.chat.id,
            "Please send radius in which object is located (in kilometers)",
            reply_markup=self.markups.get_location_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_radius, current_object
        )

    def process_getting_radius(self, message, current_object):
        if not message.content_type == "text":
            self.get_radius(message, current_object)
            return

        if message.text.strip().isnumeric():
            current_object["radius in kilometers"] = int(message.text)
            current_object["manager"] = message.from_user.username
            self.get_objects_to_display(message, current_object, method="location")
            return
        else:
            self.get_radius(message, current_object)

    def get_objects_to_display(self, message, current_object, **kwargs):
        is_false_kwarg = False
        try:
            method = kwargs["method"]
        except:
            is_false_kwarg = True

        if is_false_kwarg:
            self.command_start(message)
            return

        if method == "id":
            object_to_print = self.db_repo.find_object_by_fake_id(current_object)
            if object_to_print is None:
                self.command_start(message)
                return
            self.property_object_menu_handler(message, object_to_print)
        elif method == "location":
            objects = self.db_repo.get_objects_by_location(current_object)
            current_object["filter type"] = "location"
            self.show_all_objects(message, current_object, objects)
        elif method == "all":
            current_object["manager"] = message.from_user.username
            current_object["filter type"] = "show all"
            property_objects = self.db_repo.get_all_manager_objects(current_object)
            self.show_all_objects(message, current_object, property_objects)

    def show_all_objects(self, message, current_object, objects, **kwargs):
        page = 1
        objects_string, string_len, pages_count = self.__parse_objects_into_string(
            objects, page
        )
        if objects_string == "you have no objects in this area":
            self.bot.send_message(
                message.from_user.id, "you have no objects in this area"
            )
            self.command_start(message)
            return

        cur_message = "This is what I have  found:\n"
        cur_message += self.__parse_current_object_into_string(current_object)
        cur_message += objects_string
        cur_message += f"\n\n <b>Page {page} / {pages_count}</b>"

        self.bot.send_message(
            message.from_user.id,
            cur_message,
            reply_markup=self.inline_markups.show_all_objects_inline_markup(string_len),
            parse_mode="HTML",
        )

    def show_all_objects_callback_handler(self, call):
        if call.data == "show_all_objects_prev" or call.data == "show_all_objects_next":
            self.__edit_show_all_objects_message(call)
        else:
            current_object, page = self.__parse_message_into_current_object(
                call.message
            )
            object_index = page * 10 - 10 + int(call.data.split("_")[-1])
            if current_object["filter type"] == "location":
                property_object = self.db_repo.get_objects_by_location(current_object)[
                    object_index
                ]
            elif current_object["filter type"] == "show all":
                property_object = self.db_repo.get_all_manager_objects(current_object)[
                    object_index
                ]

            self.bot.delete_message(call.message.chat.id, call.message.id)
            self.property_object_menu_handler(call.message, property_object)

    def __edit_show_all_objects_message(self, call):
        current_object, page = self.__parse_message_into_current_object(call.message)
        objects = []
        if current_object["filter type"] == "location":
            objects = self.db_repo.get_objects_by_location(current_object)
        elif current_object["filter type"] == "show all":
            objects = self.db_repo.get_all_manager_objects(current_object)

        pages_count = len(objects) / 10
        if not pages_count % 1 == 0:
            pages_count = int(pages_count) + 1

        if call.data == "show_all_objects_prev" and page - 1 > 0:
            page -= 1
            object_string, string_len, __ = self.__parse_objects_into_string(
                objects, page
            )
        elif call.data == "show_all_objects_next" and page + 1 <= pages_count:
            page += 1
            object_string, string_len, __ = self.__parse_objects_into_string(
                objects, page
            )
        else:
            return

        cur_message = "This is what I have  found:\n"
        cur_message += self.__parse_current_object_into_string(current_object)
        cur_message += object_string
        cur_message += f"\n\n <b>Page {page} / {pages_count}</b>"

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=cur_message,
            reply_markup=self.inline_markups.show_all_objects_inline_markup(string_len),
            parse_mode="HTML",
        )

    @staticmethod
    def __parse_message_into_current_object(message):
        message_lines = message.text.split("\n")
        message_lines = message_lines[1 : len(message_lines)]
        page = 0
        current_object = {}
        for line in message_lines:

            if line == "" or line[0].isnumeric():
                continue
            if line.split()[0] == "Page":
                page = int(line.split()[1])
                continue
            try:
                spec_line = line.split(":")
            except:
                continue

            if spec_line[0] == "Location":
                location_string = spec_line[1][1:-1].split(",")
                lat, long = float(location_string[0]), float(location_string[1])
                current_object[spec_line[0].lower().strip()] = (lat, long)
                continue
            if spec_line[0] == "Manager":
                manager = spec_line[1].strip()[1 : len(spec_line[1])]
                current_object[spec_line[0].lower().strip()] = manager
                continue
            if spec_line[1].strip().isnumeric():
                current_object[spec_line[0].lower().strip()] = int(spec_line[1].strip())
                continue

            current_object[spec_line[0].lower().strip()] = spec_line[1].strip()

        return current_object, page

    @staticmethod
    def __parse_objects_into_string(object_list, page):
        if len(object_list) == 0:
            return "you have no objects in this area", None, None

        object_string = ""
        pages_count = len(object_list) / 10
        string_len = 0
        if not pages_count % 1 == 0:
            pages_count = int(pages_count) + 1

        for index in range(10):
            try:
                obj = object_list[page * 10 - 10 + index]
                object_string += (
                    f"{index + 1}. <b>ID</>: {obj.fake_id}; <b>Address</b>: {obj.address}; "
                    f" <b>Property</b>:{obj.property_type} <b>Bedrooms</b>:{obj.bedrooms}\n"
                )
                string_len += 1
            except IndexError:
                break
        return object_string, string_len, pages_count

    @staticmethod
    def __parse_current_object_into_string(current_object):
        current_object_string = "<i>"
        for key, value in current_object.items():
            if key == "manager":
                current_object_string += f"{key.title()}: @{value}\n"
                continue
            elif key == "location":
                current_object_string += f"{key.title()}:{value}\n"
                continue
            current_object_string += f"{key.title()}: {value}\n"
        current_object_string += "</i>\n\n"

        return current_object_string

    @staticmethod
    def __get_cities_string_by_page(cities_list, page):
        cities_string = ""
        pages_count = len(cities_list) / 10
        string_len = 0
        if not pages_count % 1 == 0:
            pages_count = int(pages_count) + 1
        for i in range(10):
            try:
                cities_string += f"{i + 1}: {cities_list[page * 10 - 10 + i]}\n"
                string_len += 1
            except:
                pass

        cities_string += f"\nPage {page} / {pages_count}\n"

        return cities_string, string_len

    @staticmethod
    def __get_service_type_in_message_text(message):
        lines = message.split("\n")

        service_type_line = lines[1]
        return service_type_line.split(":")[-1].strip()

    def __parse_message(self, message):
        page, __ = self.__get_page_and_page_count_in_message_text(message)
        service_type = self.__get_service_type_in_message_text(message)

        return page, service_type

    @staticmethod
    def __get_page_and_page_count_in_message_text(message):
        lines = message.split("\n")
        page_line = lines[-1].split(" ")
        return int(page_line[1]), int(page_line[3])
