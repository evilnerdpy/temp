from telebot import types
import datetime


class ObjectMenuHandlers:
    def __init__(
        self, bot, markups, inline_markups, db_repo, tgh_uploader, command_start
    ):
        self.bot = bot
        self.markups = markups
        self.inline_markups = inline_markups
        self.db_repo = db_repo
        self.tgh_uploader = tgh_uploader
        self.command_start = command_start

    def get_property_object_menu_handlers(self):
        return self.print_object

    def print_object(self, message, object_to_print):
        object_json = object_to_print.__data__
        (
            current_message,
            media_group,
            __,
        ) = self.__generate_message_string_and_media_group_for_object_by_id(
            object_json["id"]
        )

        if len(object_to_print.photos) > 0:
            self.bot.send_media_group(chat_id=message.chat.id, media=media_group)
        self.bot.send_message(
            message.chat.id,
            current_message,
            parse_mode="HTML",
            reply_markup=self.markups.show_object_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.object_menu_handler, object_json["id"]
        )

    def object_menu_handler(self, message, object_id):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.print_object(message, property_object)
            return

        if message.text == "Change Object":
            self.change_object(message, object_id)
        elif message.text == "Share Object":
            self.show_clients(message, object_id)
        elif message.text == "Mark As Sold":
            pass
        elif message.text == "Back To Main Menu":
            self.command_start(message)
        else:
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.print_object(message, property_object)
            return

    def mark_as_sold(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            "Are you sure you want to mark this object as sold?",
            reply_markup=self.markups.yes_no_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_marking_the_object_as_sold, object_id
        )

    def process_marking_the_object_as_sold(self, message, object_id):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
        else:
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            property_object.is_active_object = False
            property_object.save()
            self.print_object(message.property_object)

    def show_clients(self, message, object_id, **kwargs):
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]

        clients = self.db_repo.get_all_clients_by_manager_username(
            message.from_user.username
        )
        page_count = len(clients) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1

        current_message = "Please, Choose to Whom ypu want to send the object.\nThis is your list of the clients:\n\n"
        total_buttons = 0
        for index, client in enumerate(clients[page * 5 - 5 : page * 5]):
            current_message += self.__generate_client_string(index, client)
            total_buttons += 1

        current_message += f"Page {page} / {page_count}"
        page_info_and_object_id = {
            "page": page,
            "page_count": page_count,
            "object_id": object_id,
        }
        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.show_clients_markup(total_buttons),
            parse_mode="HTML",
        )
        self.bot.register_next_step_handler(
            message, self.process_showing_client_response, page_info_and_object_id
        )

    @staticmethod
    def __generate_client_string(index, client):
        return (
            f"<b>{index + 1}</b>:Name: {client.name}\nNumber: {client.number}\n"
            f"<b>Note:</b>\n{client.note}\n\n"
        )

    def process_showing_client_response(self, message, page_info):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                page_info["object_id"]
            )
            self.print_object(message, property_object)
            return
        if "Client №" in message.text:
            try:
                index = (
                    int(message.text[message.text.index("№") + 1 : len(message.text)])
                    - 1
                )
                clients = self.db_repo.get_all_clients_by_manager_username(
                    message.from_user.username
                )
                client_id = clients[page_info["page"] * 5 - 5 + index]
                object_to_share = {"id": page_info["object_id"], "client": client_id.id}
                self.get_share_object_language(message, object_to_share)
                return
            except:
                pass

        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            self.show_clients(
                message, page_info["object_id"], page=page_info["page"] + 1
            )
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            self.show_clients(
                message, page_info["object_id"], page=page_info["page"] - 1
            )
            return
        elif message.text == "Back":
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                page_info["object_id"]
            )
            self.print_object(message, property_object)
            return
        else:
            self.show_clients(message, page_info["object_id"], page=page_info["page"])
            return
        self.show_clients(message, page_info["object_id"], page=page_info["page"])

    def get_share_object_language(self, message, object_to_share):
        self.bot.send_message(
            message.chat.id,
            "Please, choose a language",
            reply_markup=self.markups.share_object_language_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_language, object_to_share
        )

    def process_getting_language(self, message, object_to_share):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                object_to_share["id"]
            )
            self.change_object(message, property_object)
            return

        languages = {
            "English": "eng",
            "Español": "esp",
            "Polish": "pol",
            "Norwegian": "nor",
            "Swedish": "swed",
            "French": "french",
            "German": "ger",
            "Russian": "rus",
        }
        if message.text in languages.keys():
            object_to_share["lang"] = languages[message.text]
            self.create_share_record_and_send_telegraph_article(
                message, object_to_share
            )
            return
        else:
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                object_to_share["id"]
            )
            self.change_object(message, property_object)
            return

    def create_share_record_and_send_telegraph_article(self, message, object_to_share):
        property_object = self.db_repo.create_share_object_record(
            object_to_share["client"], message.from_user.username, object_to_share["id"]
        )
        link = self.tgh_uploader.upload_property_object(
            property_object, object_to_share["lang"], self.db_repo.get_agency_number()
        )
        self.bot.send_message(message.chat.id, link)
        self.print_object(message, property_object)

    def change_object(self, message, object_id):
        (
            current_message,
            __,
            service_type,
        ) = self.__generate_message_string_and_media_group_for_object_by_id(object_id)
        self.bot.send_message(
            message.from_user.id,
            current_message,
            reply_markup=self.markups.edit_object_markup(service_type),
            parse_mode="HTML",
        )
        self.bot.register_next_step_handler(
            message, self.process_changing_object, object_id
        )

    def process_changing_object(self, message, object_id):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
            return
        yes_no = [
            "Change Elevator",
            "Change Solarium",
            "Change Parking",
            "Central Gas System",
            "Solar Panels for Watter Heating",
            "Change Pets",
            "Change Pool",
        ]

        numeric_specs = ["Change Bathrooms", "Change Bedrooms", "Change Floor"]
        string_specs = [
            "Change Address",
            "Change Price Per Day",
            "Change Price Per Week",
            "Change Price Per Month",
            "Change Price",
            "Change Landlord Name",
            "Change Landlord Number",
        ]

        if message.text in yes_no:
            self.change_yes_no_spec(message, object_id)

        elif message.text in numeric_specs:
            self.change_numeric_spec(message, object_id)
        elif message.text in string_specs:
            self.change_string_spec(message, object_id)
        elif message.text == "Change Property Type":
            self.change_property_type(message, object_id)
        elif message.text == "Change Landlord Status":
            self.change_landlord_status(message, object_id)
        elif message.text == "Change Beach":
            self.change_beach(message, object_id)
        elif message.text == "Change Location":
            self.change_location(message, object_id)
        elif message.text == "Manage Photos":
            self.manage_photos(message, object_id)
        elif message.text == "Change Availability Date":
            self.change_availability_date(message, object_id)

        elif message.text == "Back":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.print_object(message, property_object)
        else:
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
            return

    def manage_photos(self, message, object_id):
        property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
        photos = self.db_repo.get_object_photos(property_object)
        if len(photos) == 0:
            self.bot.send_message(
                message.chat.id,
                "No photos for this object, please drag and drop\n "
                "them one by one in the chat",
            )
        else:
            media_group = []
            for photo in photos:
                media_group.append(types.InputMediaPhoto(photo.photo_id))
            self.bot.send_media_group(chat_id=message.chat.id, media=media_group)
        self.bot.send_message(
            message.chat.id,
            "Please, choose what you want to do",
            reply_markup=self.markups.get_pictures_markup(),
        )

        self.bot.register_next_step_handler(
            message, self.process_getting_photos, object_id
        )

    def process_getting_photos(self, message, object_id):
        if message.content_type == "photo":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            if len(property_object.photos) + 1 >= 10:
                self.change_object(message, property_object)
                return
            else:
                self.db_repo.add_photo_to_object(
                    property_object, message.photo[-1].file_id
                )
                self.manage_photos(message, object_id)

        if message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            if message.text == "Delete all":
                self.db_repo.delete_all_object_photos(property_object)
                self.manage_photos(message, object_id)
                return
            elif message.text == "Delete By Order":
                self.get_photo_order(message, object_id)
            elif message.text == "Continue":
                self.change_object(message, object_id)
            else:
                self.manage_photos(message, object_id)

    def get_photo_order(self, message, object_id):
        self.bot.send_message(
            message.chat.id, "Please, send ID of the photo (from 1 to 10)..."
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_photo_order, object_id
        )

    def process_getting_photo_order(self, message, object_id):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)

        if message.text.strip().isnumeric():
            photo_id = int(message.text.strip())
            if self.db_repo.check_if_object_have_photo_by_id(object_id, photo_id):
                self.db_repo.delete_object_photo_by_id(object_id, photo_id)
        self.manage_photos(message, object_id)

    def change_availability_date(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            "Please, specify the date when the object will be available for rent...\n"
            "Send the date in (YYYY.MM.DD) format",
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_availability_date, object_id
        )

    def process_getting_availability_date(self, message, object_id):
        if not message.content_type == "text":
            self.change_object(message, object_id)
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

            self.check_if_availability_date_is_right(
                message, object_id, availability_date
            )
        else:
            self.bot.send_message(
                message.from_user.id, "Wrong date spelling, please try again..."
            )
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
            return

    def check_if_availability_date_is_right(self, message, object_id, date):
        self.bot.send_message(
            message.from_user.id,
            f"The date you specified is "
            f"{date.strftime(' %d %B %Y')}.\n"
            f"Is that true?",
            reply_markup=self.markups.yes_no_markup(),
        )
        id_and_date = {"id": object_id, "date": date}
        self.bot.register_next_step_handler(
            message, self.process_getting_availability_date_response, id_and_date
        )

    def process_getting_availability_date_response(self, message, id_and_date):
        if not message.content_type == "text":
            self.check_if_availability_date_is_right(
                message, id_and_date["id"], id_and_date["date"]
            )
            return

        if message.text == "Yes":
            self.db_repo.change_object_availability_date(
                id_and_date["id"], id_and_date["date"]
            )
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                id_and_date["id"]
            )
            self.change_object(message, property_object)

        elif message.text == "No":
            self.change_availability_date(message, id_and_date["id"])
            return
        else:
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                id_and_date["id"]
            )
            self.change_object(message, property_object)
            return

    def change_location(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            "Please Send New Location Of The Object or "
            "Press Button Bellow To Send Your Current Location)",
            reply_markup=self.markups.get_location_markup(),
        )

        self.bot.register_next_step_handler(
            message, self.process_changing_location, object_id
        )

    def process_changing_location(self, message, object_id):
        if not message.content_type == "location":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
            return
        else:
            location_lat_long = ",".join(
                [str(message.location.latitude), str(message.location.longitude)]
            )
            property_object = self.db_repo.change_object_string_spec(
                object_id, "location", location_lat_long
            )
            self.change_object(message, property_object)

    def change_beach(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            "Please type a new value for Beach",
            reply_markup=self.markups.get_beach_spec_markup(),
        )

        self.bot.register_next_step_handler(
            message, self.process_changing_beach, object_id
        )

    def process_changing_beach(self, message, object_id):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
            return
        beach = ["5 min", "10 min", "15 min", "No Beach Nearby"]
        if message.text in beach:
            self.db_repo.change_object_string_spec(
                object_id, "beach", message.text.lower().capitalize()
            )

        property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
        self.change_object(message, property_object)

    def change_landlord_status(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            "Please type a new value for Landlord Status",
            reply_markup=self.markups.get_landlord_status_markup(),
        )

        self.bot.register_next_step_handler(
            message, self.process_getting_landlord_status, object_id
        )

    def process_getting_landlord_status(self, message, object_id):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
            return
        landlord_statuses = ["Owner", "Agent"]
        if message.text in landlord_statuses:
            self.db_repo.change_object_string_spec(
                object_id, "landlord status", message.text.lower()
            )

        property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
        self.change_object(message, property_object)

    def change_property_type(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            f"Please type a new value for Property Type",
            reply_markup=self.markups.get_property_type_markup(),
        )

        self.bot.register_next_step_handler(
            message, self.process_getting_property_type, object_id
        )

    def process_getting_property_type(self, message, object_id):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.change_object(message, property_object)
            return
        property_type = ["Villa", "Bungalow", "Apartments"]
        if message.text in property_type:
            self.db_repo.change_object_string_spec(
                object_id, "property type", message.text
            )

        property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
        self.change_object(message, property_object)

    def change_string_spec(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            f"""Please type a new value for {message.text.split(' ')[-1]}""",
        )
        id_and_spec = {"id": object_id, "spec": message.text}
        self.bot.register_next_step_handler(
            message, self.process_getting_string_spec, id_and_spec
        )

    def process_getting_string_spec(self, message, id_and_spec):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                id_and_spec["id"]
            )
            self.change_object(message, property_object)
            return

        property_object = self.db_repo.change_object_string_spec(
            id_and_spec["id"], id_and_spec["spec"], message.text
        )
        self.change_object(message, property_object)
        return

    def change_numeric_spec(self, message, object_id):
        self.bot.send_message(
            message.chat.id,
            f"""Please type a new value for {message.text.split(' ')[-1]}""",
        )
        id_and_spec = {"id": object_id, "spec": message.text}
        self.bot.register_next_step_handler(
            message, self.process_getting_numeric_spec, id_and_spec
        )

    def process_getting_numeric_spec(self, message, id_and_spec):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                id_and_spec["id"]
            )
            self.change_object(message, property_object)
            return

        if message.text.isnumeric():
            self.db_repo.change_object_numeric_spec(
                id_and_spec["id"], id_and_spec["spec"], int(message.text)
            )
        else:
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                id_and_spec["id"]
            )
            self.change_object(message, property_object)
            return

        property_object = self.db_repo.get_object_by_id_for_object_menu(
            id_and_spec["id"]
        )
        self.change_object(message, property_object)

    def change_yes_no_spec(self, message, object_id):

        self.bot.send_message(
            message.chat.id,
            f"""Please type a new value for {message.text.split(' ')[-1] 
                                                if 'Change' in message.text else message.text}""",
            reply_markup=self.markups.yes_no_markup(),
        )
        id_and_spec = {"id": object_id, "spec": message.text}
        self.bot.register_next_step_handler(
            message, self.process_getting_yes_no_spec, id_and_spec
        )

    def process_getting_yes_no_spec(self, message, id_and_spec):
        if not message.content_type == "text":
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                id_and_spec["id"]
            )
            self.change_object(message, property_object)
            return
        response = ""
        if message.text == "Yes":
            response = "Yes"
        elif message.text == "No":
            response = "No"
        else:
            property_object = self.db_repo.get_object_by_id_for_object_menu(
                id_and_spec["id"]
            )
            self.change_object(message, property_object)
            return

        spec_keys = {
            "Change Elevator": "elevator",
            "Change Solarium": "solarium",
            "Change Parking": "parking",
            "Central Gas System": "central_gas_system",
            "Solar Panels for Watter Heating": "solar_panels_for_water_heating",
            "Change Pets": "pets",
            "Change Pool": "pool",
        }

        self.db_repo.change_object_yes_no_spec(
            id_and_spec["id"], spec_keys[id_and_spec["spec"]], response
        )
        self.change_object(message, id_and_spec["id"])

    def __generate_message_string_and_media_group_for_object_by_id(self, object_id):
        property_object = self.db_repo.get_object_by_id_for_object_menu(object_id)
        current_message = ""
        object_json = property_object.__data__
        current_message += f"ID: {object_json['fake_id']}\n"
        current_message += f"Service type: {object_json['property_service_type']}\n"
        current_message += f"City: {property_object.related_to_city.city_name}\n"
        current_message += f"Address: {object_json['address']}\n"
        current_message += f"Property type: {object_json['property_type']}\n"
        current_message += f"Bedrooms: {object_json['bedrooms']}\n"
        current_message += f"Bathrooms: {object_json['bathrooms']}\n"
        current_message += f"Floor: {object_json['floor']}\n"
        current_message += f"Beach: {object_json['beach']}\n"
        current_message += (
            f"Elevator: {'Yes' if object_json['elevator'] == True else 'No'}\n"
        )
        current_message += f"Patio:{'Yes' if object_json['patio'] == True else 'No'}\n"
        current_message += (
            f"Solarium:{'Yes' if object_json['solarium'] == True else 'No'}\n"
        )
        current_message += (
            f"Parking:{'Yes' if object_json['parking'] == True else 'No'}\n"
        )
        current_message += f"Pool:{'Yes' if object_json['pool'] == True else 'No'}\n"
        current_message += f"Central Gas System:{'Yes' if object_json['central_gas_system'] == True else 'No'}\n"
        current_message += f"Solar Panels For Water Heating:{'Yes' if object_json['solar_panels_for_water_heating'] == True else 'No'}\n"

        if property_object.__data__["property_service_type"] == "rent":
            rent_attributes = property_object.rent_attributes[0].__data__
            current_message += (
                f"Pets: {'Yes' if rent_attributes['pets'] == True else 'No'}\n"
            )
            current_message += (
                f"Available from: {rent_attributes['availability_date']} \n"
            )
            current_message += f"Price per Day(€): {rent_attributes['per_day_cost']} \n"
            current_message += (
                f"Price per Week(€): {rent_attributes['per_week_cost']} \n"
            )
            current_message += (
                f"Price per Month(€): {rent_attributes['per_month_cost']} \n"
            )
        if property_object.__data__["property_service_type"] == "sale":
            rent_attributes = property_object.sale_attributes[0].__data__
            current_message += f"Price(€): {rent_attributes['price']}\n"

        location = object_json["location_lat_long"].split(",")
        lat, long = float(location[0]), float(location[1])
        current_message += (
            f'<a href="http://www.google.com/maps/place/{lat},{long}">location</a>'
        )

        current_message += "\n\nThis information will not be displayed for user\n"

        landlord = self.db_repo.get_landlord_by_property(property_object)
        current_message += f"Landlord: {landlord['name']}\n"
        current_message += f"Landlord number: {landlord['number']}\n"
        current_message += f"Landlord status: {landlord['status']}\n"

        photos = self.db_repo.get_object_photos(property_object)
        media_group = []
        if not len(photos) == 0:
            for index, photo in enumerate(photos):
                media_group.append(types.InputMediaPhoto(photo.photo_id))

        return current_message, media_group, object_json["property_service_type"]

    # def share_object(self, message, object_id):
    #     self.bot.send_message(message.from_user.id, "Please Choose The Language")
