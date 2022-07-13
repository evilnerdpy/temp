import datetime
from telebot import types
import random


class AddObjectHandlers:
    def __init__(self, bot, markups, inline_markups, db_repo, command_start):
        self.bot = bot
        self.markups = markups
        self.inline_markups = inline_markups
        self.db_repo = db_repo
        self.command_start = command_start

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
            reply_markup=self.inline_markups.add_object_cities_inline_markup(list_len),
            parse_mode="HTML",
        )

    def edit_get_city_message(self, call):
        page, page_count = self.__get_page_and_page_count_in_message_text(
            call.message.text
        )
        factor = 1
        need_to_print = False
        if call.data == "choose_city_city_add":
            factor = 0
            need_to_print = True
        elif call.data == "choose_city_city_prev":
            factor *= -1

        if page + factor > page_count or page + factor <= 0:
            return

        cur_message = "Please, choose the city in which property is located..\n"
        cur_message += f"Service type: {self.__get_service_type_in_message_text(call.message.text)}\n"
        cities_string, list_len = self.__get_cities_string_by_page(
            self.db_repo.get_all_cities_names(), page + factor
        )
        cur_message += cities_string
        if need_to_print:
            self.bot.send_message(
                call.message.chat.id,
                cur_message,
                reply_markup=self.inline_markups.add_object_cities_inline_markup(
                    list_len
                ),
            )
            return
        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            text=cur_message,
            message_id=call.message.id,
            reply_markup=self.inline_markups.add_object_cities_inline_markup(list_len),
        )

    def get_city_callback_handler(self, call):
        if call.data == "choose_city_city_prev" or call.data == "choose_city_city_next":
            self.edit_get_city_message(call)
            return
        elif call.data == "choose_city_city_add":
            self.bot.delete_message(call.message.chat.id, call.message.id)
            self.add_city(call)

        else:
            page, service_type = self.__parse_message(call.message.text)
            city_name = self.db_repo.get_city_name_by_index(
                page * 10 - 10 + int(call.data.split("_")[-1])
            )
            self.bot.delete_message(call.message.chat.id, call.message.id)
            current_object = {"service type": service_type, "city": city_name}
            self.get_address(call.message, current_object)

    def add_city(self, call):
        self.bot.send_message(call.message.chat.id, "Please, type a New City Name")
        self.bot.register_next_step_handler(
            call.message, self.process_getting_the_city, call
        )

    def process_getting_the_city(self, message, call):
        if not message.content_type == "text":
            self.command_start(message)
            return
        self.db_repo.add_city(message.text.strip().title())
        self.edit_get_city_message(call)

    def get_address(self, message, current_object):

        cur_message = self.__get_props_as_string(current_object, [])

        cur_message += "<b>Please, send the address of the property...</b>\n\n"

        self.bot.send_message(message.chat.id, cur_message, parse_mode="HTML")
        self.bot.register_next_step_handler(
            message, self.process_getting_address, current_object
        )

    def process_getting_address(self, message, current_object):
        if not message.content_type == "text":
            self.get_address(message, current_object)
            return
        current_object["address"] = message.text
        self.get_pictures(message, current_object)

    def get_pictures(self, message, current_object):
        has_photos = False
        photos = []

        try:
            photos = current_object["photos"]
            if len(photos) > 0:
                has_photos = True
        except:
            current_object["photos"] = []

        if has_photos:
            media_group = []
            for index, photo in enumerate(photos):
                media_group.append(types.InputMediaPhoto(photo))

            self.bot.send_media_group(message.from_user.id, media=media_group)
            self.bot.send_message(
                message.from_user.id,
                "Please ,send the picture of the object\n"
                "Please, note that you can send only one "
                "by one.\n"
                "The limit is 10 photos.\n\n"
                f"<b>Photos {len(photos)}/10</b>",
                parse_mode="HTML",
            )
        else:
            self.bot.send_message(
                message.from_user.id,
                "Please ,send the picture of the object\n"
                "Please, note that you can send only one by one.\n"
                "The limit is 10 photos.\n\n"
                "<b>Photos 0/10</b>",
                parse_mode="HTML",
                reply_markup=self.markups.get_pictures_markup(),
            )

        self.bot.register_next_step_handler(
            message, self.process_getting_pictures, current_object
        )

    def process_getting_pictures(self, message, current_object):
        if message.content_type == "photo":
            if len(current_object["photos"]) + 1 == 11:
                self.bot.send_message(
                    message.from_user.id, "To many photos!Sorry , I can't add more..."
                )
            else:
                current_object["photos"].append(message.photo[-1].file_id)

        if not message.content_type == "text":
            self.get_pictures(message, current_object)
            return

        if message.text == "Delete By Order":
            self.delete_picture_by_order(message, current_object)
            return

        elif message.text == "Delete all":
            current_object["photos"].clear()

        elif message.text == "Continue":
            self.get_property_type(message, current_object)
            return

        self.get_pictures(message, current_object)

    def get_property_type(self, message, current_object):
        cur_message = "Please, specify the type of property...\n"
        cur_message += self.__get_props_as_string(
            current_object, ["property", "photos"]
        )

        self.bot.send_message(
            message.from_user.id,
            cur_message,
            reply_markup=self.markups.get_property_type_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_property_type, current_object
        )

    def process_getting_property_type(self, message, current_object):
        if not message.content_type == "text":
            self.get_property_type(message, current_object)
            return

        if message.text == "Villa":
            current_object["property"] = "villa"
        elif message.text == "Bungalow":
            current_object["property"] = "bungalow"
        elif message.text == "Apartments":
            current_object["property"] = "apartments"
        else:
            self.command_start(message)
            return

        self.get_additional_specs(message, current_object)

    def get_additional_specs(self, message, current_object):
        is_rent = False
        specs = [
            "bathrooms",
            "bedrooms",
            "floor",
            "elevator",
            "beach",
            "patio",
            "solarium",
            "parking",
            "pool",
            "central gas system",
            "solar panels for water heating",
            "photos",
        ]

        if current_object["service type"] == "rent":
            specs.append("pets")
            is_rent = True

        cur_message = "Please, specify additional specifications...\n<i>"
        cur_message += self.__get_props_as_string(current_object, specs)
        specs.remove("photos")
        cur_message += "</i>\n\n<b>"
        for item in specs:
            try:
                cur_message += f"{item} : {current_object[item]} \n"
            except:
                if item == "beach":
                    cur_message += "Beach : No beach nearby\n"
                    current_object["beach"] = "No beach nearby"
                elif item in [
                    "elevator",
                    "pets",
                    "patio",
                    "patio",
                    "solarium",
                    "parking",
                    "pool",
                    "central gas system",
                    "solar panels for water heating",
                ]:
                    cur_message += f"{item.title()} : No\n"
                    current_object[item] = "No"
                else:
                    cur_message += f"{item.title()} : 1\n"
                    current_object[item] = 1
        cur_message += "</b>"
        self.bot.send_message(
            message.from_user.id,
            cur_message,
            parse_mode="HTML",
            reply_markup=self.markups.get_additional_specs_markup(is_rent),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_additional_specs, current_object
        )

    def process_getting_additional_specs(self, message, current_object):
        if not message.content_type == "text":
            self.get_additional_specs(message, current_object)
            return
        number_spec = ["Bathrooms", "Bedrooms", "Floor"]
        yes_no_spec = [
            "Elevator",
            "Pets",
            "Patio",
            "Solarium",
            "Parking",
            "Pool",
            "Central Gas System",
            "Solar Panels For Water Heating",
        ]

        if message.text in number_spec:

            self.get_numeric_spec(message, current_object)
            return
        elif message.text in yes_no_spec:
            self.get_yes_no_spec(message, current_object)
            return
        elif message.text == "Beach":
            self.get_beach_spec(message, current_object)
            return
        elif message.text == "Back To Main Menu":
            self.command_start(message)
            return
        elif message.text == "Continue":
            self.post_additional_spec_menu_handler(message, current_object)
            return
        else:
            self.get_additional_specs(message, current_object)

    def get_beach_spec(self, message, current_object):
        self.bot.send_message(
            message.from_user.id,
            "Is there a beach nearby?",
            reply_markup=self.markups.get_beach_spec_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_beach_spec, current_object
        )

    def process_getting_beach_spec(self, message, current_object):
        if not message.content_type == "text":
            self.get_additional_specs(message, current_object)
            return
        if message.text in ["5 min", "10 min", "15 min", "No Beach Nearby"]:
            current_object["beach"] = message.text.lower()

        self.get_additional_specs(message, current_object)

    def get_yes_no_spec(self, message, current_object):
        if message.text == "Elevator":
            cur_message = "Is there an elevator?"
        elif message.text == "Pets":
            cur_message = "Are pets allowed?"
        elif message.text == "Patio":
            cur_message = "Is there a Patio?"
        elif message.text == "Solarium":
            cur_message = "Is there a Solarium?"
        elif message.text == "Parking":
            cur_message = "Is there a Parking?"
        elif message.text == "Pool":
            cur_message = "Is there a Pool?"
        elif message.text == "Central Gas System":
            cur_message = "Is there a Central Gas System?"
        elif message.text == "Solar Panels For Water Heating":
            cur_message = "Are there a Solar Panels For Water Heating?"

        current_object["current_spec"] = message.text.lower()

        self.bot.send_message(
            message.from_user.id, cur_message, reply_markup=self.markups.yes_no_markup()
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_yes_no_spec, current_object
        )

    def process_getting_yes_no_spec(self, message, current_object):

        if not message.content_type == "text":
            current_object.pop("current_spec")
            self.get_additional_specs(message, current_object)
            return

        if message.text in ["Yes", "No"]:

            current_object[current_object["current_spec"]] = message.text.capitalize()
            current_object.pop("current_spec")
            self.get_additional_specs(message, current_object)
            return
        else:
            current_object.pop("current_spec")
            self.get_additional_specs(message, current_object)
            return

    def get_numeric_spec(self, message, current_object):
        current_object["current_spec"] = message.text.lower()
        self.bot.send_message(
            message.from_user.id,
            f"Please, send how many {message.text.lower()} are there...",
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_numeric_spec, current_object
        )

    def process_getting_numeric_spec(self, message, current_object):

        if not message.content_type == "text":
            current_object.pop("current_spec")
            self.get_additional_specs(message, current_object)
            return
        if message.text.strip().isnumeric():
            current_object[current_object["current_spec"]] = int(message.text.strip())
            current_object.pop("current_spec")
            self.get_additional_specs(message, current_object)
            return
        else:
            current_object.pop("current_spec")
            self.get_additional_specs(message, current_object)

    def post_additional_spec_menu_handler(self, message, current_object):
        if not message.content_type == "text":
            self.post_additional_spec_menu_handler(message, current_object)
            return

        if current_object["service type"] == "rent":
            self.get_rent_price(message, current_object)
            return
        elif current_object["service type"] == "sale":
            self.get_object_price(message, current_object)
            return
        else:
            self.post_additional_spec_menu_handler(message, current_object)

    def get_rent_price(self, message, current_object):
        price_is_specified = self.__check_if_rent_price_is_specified(current_object)
        self.bot.send_message(
            message.from_user.id,
            "Please, send the rent price of the object",
            reply_markup=self.markups.get_rent_price_markup(price_is_specified),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_rent_price, current_object
        )

    def process_getting_rent_price(self, message, current_object):
        if not message.content_type == "text":
            self.get_rent_price(message, current_object)
            return

        if message.text == "Continue":
            if current_object["service type"] == "rent":
                self.get_availability_date(message, current_object)
                return

        elif message.text in ["Per Day", "Weekly", "Monthly"]:
            self.get_rent_price_by_factor(message, current_object)
            return
        else:
            self.get_rent_price(message, current_object)

    def get_rent_price_by_factor(self, message, current_object):
        self.bot.send_message(
            message.from_user.id, f"Please send {message.text} price..."
        )
        current_object["factor"] = message.text.lower()
        self.bot.register_next_step_handler(
            message, self.process_getting_rent_price_by_factor, current_object
        )

    def process_getting_rent_price_by_factor(self, message, current_object):
        if not message.content_type == "text":
            current_object.pop("factor")
            self.post_additional_spec_menu_handler(message, current_object)
            return

        current_object[current_object["factor"]] = message.text.strip()
        current_object.pop("factor")
        self.post_additional_spec_menu_handler(message, current_object)

    def get_object_price(self, message, current_object):
        self.bot.send_message(
            message.from_user.id,
            "Please, send the price of the object",
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_object_price, current_object
        )

    def process_getting_object_price(self, message, current_object):
        if not message.content_type == "text":
            self.post_additional_spec_menu_handler(message, current_object)
            return

        current_object["price"] = message.text.strip()
        self.get_landlord_name(message, current_object)

    def get_availability_date(self, message, current_object):
        self.bot.send_message(
            message.from_user.id,
            "Please, specify the date when the object will be available for rent\n"
            "Send the date in (YYYY.MM.DD) format",
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_availability_date, current_object
        )

    def process_getting_availability_date(self, message, current_object):
        if not message.content_type == "text":
            self.get_availability_date(message, current_object)
            return

        is_date_created = False
        try:
            date_string = list(map(int, message.text.strip().split(".")))
            availability_date = datetime.datetime(
                date_string[0], date_string[1], date_string[2]
            )
            is_date_created = True
        except:
            pass

        if is_date_created:
            current_object["availability_date"] = availability_date
            self.check_if_availability_date_is_right(message, current_object)
        else:
            self.bot.send_message(
                message.from_user.id, "Wrong date spelling, please try again."
            )
            self.get_availability_date(message, current_object)

    def check_if_availability_date_is_right(self, message, current_object):
        self.bot.send_message(
            message.from_user.id,
            f"The date you specified is "
            f"{current_object['availability_date'].strftime(' %d %B %Y')}.\n"
            f"Is that true?",
            reply_markup=self.markups.yes_no_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_availability_date_response, current_object
        )

    def process_getting_availability_date_response(self, message, current_object):
        if not message.content_type == "text":
            self.check_if_availability_date_is_right(message, current_object)
            return

        if message.text == "Yes":
            self.get_landlord_name(message, current_object)
            return
        elif message.text == "No":
            self.get_availability_date(message, current_object)
            return
        else:
            self.get_availability_date(message, current_object)

    def get_landlord_name(self, message, current_object):
        self.bot.send_message(message.from_user.id, "Please, send Landlord name")
        self.bot.register_next_step_handler(
            message, self.process_getting_landlord_name, current_object
        )

    def process_getting_landlord_name(self, message, current_object):
        if not message.content_type == "text":
            self.get_landlord_name(message, current_object)
            return
        current_object["related to landlord"] = {}
        current_object["related to landlord"]["name"] = message.text.strip().title()

        self.get_landlord_number(message, current_object)

    def get_landlord_number(self, message, current_object):
        self.bot.send_message(message.from_user.id, "Please , send Landlord number")
        self.bot.register_next_step_handler(
            message, self.process_getting_landlord_number, current_object
        )

    def process_getting_landlord_number(self, message, current_object):
        if not message.content_type == "text":
            self.get_landlord_number(message, current_object)
            return

        current_object["related to landlord"]["number"] = message.text.strip()
        self.get_landlord_status(message, current_object)

    def get_landlord_status(self, message, current_object):
        self.bot.send_message(
            message.from_user.id,
            "He/She is a an...?",
            reply_markup=self.markups.get_landlord_status_markup(),
        )

        self.bot.register_next_step_handler(
            message, self.process_getting_landlord_status, current_object
        )

    def process_getting_landlord_status(self, message, current_object):
        if not message.content_type == "text":
            self.get_landlord_status(message, current_object)
            return

        current_object["related to landlord"]["status"] = message.text.strip().lower()
        self.get_location(message, current_object)

    def delete_picture_by_order(self, message, current_object):
        if len(current_object["photos"]) > 0:
            self.bot.send_message(
                message.from_user.id,
                "Please , send the number of the photo you want to delete.\n"
                "It should be on range of 1 and 10.",
            )
            self.bot.register_next_step_handler(
                message, self.process_deleting_picture_by_order, current_object
            )
        else:
            self.bot.send_message(
                message.from_user.id, "There are no photos.\nNothing to delete"
            )

    def process_deleting_picture_by_order(self, message, current_object):
        if not message.content_type == "text":
            self.get_pictures(message, current_object)
            return

        if message.text.strip().isnumeric():
            index = int(message.text.strip()) - 1
            if -1 < index < 11:
                current_object["photos"].pop(index)

        self.get_pictures(message, current_object)

    def get_location(self, message, current_object):
        self.bot.send_message(
            message.from_user.id,
            "The last step,Please send us location of the object!\n"
            "Try to look at telegram gallery,there  you can find a 'location' menu.\n",
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_location, current_object
        )

    def process_getting_location(self, message, current_object):
        if not message.content_type == "location":
            self.get_location(message, current_object)
            return

        current_object["location"] = (
            message.location.latitude,
            message.location.longitude,
        )
        self.show_record_before_uploading(message, current_object)

    def show_record_before_uploading(self, message, current_object):
        message_string, media_group = self.__parse_whole_current_object(current_object)
        if media_group is not None:
            self.bot.send_media_group(message.from_user.id, media=media_group)
        self.bot.send_message(
            message.from_user.id,
            message_string,
            reply_markup=self.markups.show_record_before_uploading_markup(),
            parse_mode="HTML",
        )
        self.bot.register_next_step_handler(
            message, self.process_showing_record_before_uploading, current_object
        )

    def process_showing_record_before_uploading(self, message, current_object):
        if not message.content_type == "text":
            self.show_record_before_uploading(message, current_object)
            return

        if message.text == "Back to Main Menu":
            self.command_start(message)
            return
        if message.text == "ADD OBJECT":
            print(current_object)
            current_object["manager"] = message.from_user.username
            id = self.db_repo.save_current_object(current_object)
            object = self.db_repo.get_object_by_id_for_object_menu(id)
            object.fake_id = f"ARE{random.randint(1000,9999)}{id}"
            object.save()
            self.bot.send_message(
                message.from_user.id,
                f"The object was successfully saved under {object.fake_id} id\n."
                f"You can access it by pressing 'My Objects' button\n"
                f"in main menu.",
            )
            self.command_start(message)

    @staticmethod
    def __parse_whole_current_object(current_object):
        message_string = (
            "This Is full object description, please press, 'ADD OBJECT'\n "
            "in order to upload it in your profile\n<b>"
        )
        media_group = []

        for item, value in current_object.items():
            if item == "related to landlord":
                message_string += (
                    f"Landlord: {value['name']}\n"
                    f"Number: {value['number']}\n"
                    f"Status: {value['status']}\n"
                )
                continue
            elif item == "photos":
                has_photos = False
                photos = []

                try:
                    photos = current_object["photos"]
                    if len(photos) > 0:
                        has_photos = True
                except:
                    current_object["photos"] = []

                if has_photos:
                    for index, photo in enumerate(photos):
                        media_group.append(types.InputMediaPhoto(photo))
                else:
                    continue
                continue
            if item == "location":
                message_string += f'<a href="http://www.google.com/maps/place/{value[0]},{value[1]}">location</a>'
                continue

            message_string += f"{item.title()}: {value}\n"

        message_string += "</b>"
        return message_string, media_group if len(media_group) > 0 else None

    @staticmethod
    def __check_if_rent_price_is_specified(current_object):
        return (
            "per day" in current_object
            or "weekly" in current_object
            or "monthly" in current_object
        )

    @staticmethod
    def __get_props_as_string(current_object, banned_list):
        cur_message = ""
        for key, value in current_object.items():
            if key not in banned_list:
                cur_message += f"{key.title()}: {value}\n"

        return cur_message

    @staticmethod
    def __get_service_type_in_message_text(message):
        lines = message.split("\n")

        service_type_line = lines[1]
        return service_type_line.split(":")[-1].strip()

    @staticmethod
    def __get_page_and_page_count_in_message_text(message):
        lines = message.split("\n")
        page_line = lines[-1].split(" ")
        return int(page_line[1]), int(page_line[3])

    @staticmethod
    def __get_cities_string_by_page(cities_list, page):
        cities_string = ""
        pages_count = len(cities_list) / 10
        string_len = 0
        if not pages_count % 1 == 0:
            pages_count = int(pages_count) + 1
        for i in range(10):
            try:
                cities_string += f"{i+1}: {cities_list[page*10-10+i]}\n"
                string_len += 1
            except:
                pass

        cities_string += f"\nPage {page} / {pages_count}\n"

        return cities_string, string_len

    def __parse_message(self, message):
        page, __ = self.__get_page_and_page_count_in_message_text(message)
        service_type = self.__get_service_type_in_message_text(message)

        return page, service_type
