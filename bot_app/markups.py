from telebot import types


class Markups:
    @staticmethod
    def get_command_start_markup(status):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_add_object = types.KeyboardButton("Add Object")
        button_add_client = types.KeyboardButton("Add Client")
        button_find_object = types.KeyboardButton("Find Object")

        markup.row(button_add_object, button_add_client)
        markup.add(button_find_object)
        if status == "admin":
            markup.add(types.KeyboardButton("ADMIN PANEL"))
        return markup

    @staticmethod
    def get_service_type_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_rent = types.KeyboardButton("Rent")
        button_sale = types.KeyboardButton("Sale")

        markup.row(button_rent, button_sale)

        return markup

    @staticmethod
    def get_property_type_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_villa = types.KeyboardButton("Villa")
        button_bung = types.KeyboardButton("Bungalow")
        button_app = types.KeyboardButton("Apartments")
        button_back = types.KeyboardButton("Back To Main Menu")

        markup.row(button_villa, button_bung)
        markup.add(button_app)
        markup.add(button_back)

        return markup

    @staticmethod
    def get_additional_specs_markup(is_rent):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_bathrooms = types.KeyboardButton("Bathrooms")
        button_bedrooms = types.KeyboardButton("Bedrooms")
        button_floor = types.KeyboardButton("Floor")
        button_elevator = types.KeyboardButton("Elevator")
        button_beach = types.KeyboardButton("Beach")
        button_patio = types.KeyboardButton("Patio")
        button_solarium = types.KeyboardButton("Solarium")
        button_parking = types.KeyboardButton("Parking")
        button_pool = types.KeyboardButton("Pool")
        button_gas = types.KeyboardButton("Central Gas System")
        button_heat = types.KeyboardButton("Solar Panels For Water Heating")

        markup.row(button_bathrooms, button_bedrooms)
        markup.row(button_floor, button_elevator)
        markup.row(button_beach, button_patio)
        markup.row(button_solarium, button_parking)
        markup.row(button_pool, button_gas)
        markup.row(button_heat)

        if is_rent:
            button_pets = types.KeyboardButton("Pets")
            markup.add(button_pets)

        button_continue = types.KeyboardButton("Continue")
        button_back = types.KeyboardButton("Back To Main Menu")

        markup.add(button_continue)
        markup.add(button_back)

        return markup

    @staticmethod
    def yes_no_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_yes = types.KeyboardButton("Yes")
        button_no = types.KeyboardButton("No")

        markup.row(button_no, button_yes)

        return markup

    @staticmethod
    def get_beach_spec_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_five = types.KeyboardButton("5 min")
        button_ten = types.KeyboardButton("10 min")
        button_fifteen = types.KeyboardButton("15 min")
        button_no_beach = types.KeyboardButton("No Beach Nearby")

        markup.row(button_five, button_ten, button_fifteen)
        markup.add(button_no_beach)

        return markup

    @staticmethod
    def get_rent_price_markup(is_specified):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_per_day = types.KeyboardButton("Per Day")
        button_weekly = types.KeyboardButton("Weekly")
        button_monthly = types.KeyboardButton("Monthly")

        markup.row(button_per_day, button_weekly)
        markup.add(button_monthly)

        if is_specified:
            button_continue = types.KeyboardButton("Continue")
            markup.add(button_continue)

        return markup

    @staticmethod
    def get_landlord_status_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_owner = types.KeyboardButton("Owner")
        button_agent = types.KeyboardButton("Agent")

        markup.row(button_agent, button_owner)

        return markup

    @staticmethod
    def get_pictures_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_delete_by_order = types.KeyboardButton("Delete By Order")
        button_delete_all = types.KeyboardButton("Delete all")
        button_continue = types.KeyboardButton("Continue")

        markup.add(button_delete_by_order)
        markup.add(button_delete_all)
        markup.add(button_continue)

        return markup

    @staticmethod
    def get_location_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(
            types.KeyboardButton("Send my current Location", request_location=True)
        )
        return markup

    @staticmethod
    def show_record_before_uploading_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_add_object = types.KeyboardButton("ADD OBJECT")
        button_back = types.KeyboardButton("Back to Main Menu")

        markup.add(button_add_object)
        markup.add(button_back)

        return markup

    @staticmethod
    def chose_additional_filters():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_find_by_location = types.KeyboardButton("Find by Location")
        button_find_by_id = types.KeyboardButton("Find By Id")
        button_show_all = types.KeyboardButton("Show All My Objects")

        markup.row(button_find_by_location, button_find_by_id)
        markup.add(button_show_all)

        return markup

    @staticmethod
    def show_object_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_change_object = types.KeyboardButton("Change Object")
        button_share_object = types.KeyboardButton("Share Object")
        # button_mark_as_closed = types.KeyboardButton("Mark As Sold")
        button_back_to_main_menu = types.KeyboardButton("Back To Main Menu")

        markup.add(button_change_object)
        markup.row(button_share_object)
        markup.add(button_back_to_main_menu)

        return markup

    @staticmethod
    def edit_object_markup(service_type):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        button_address = types.KeyboardButton("Change Address")
        button_prop = types.KeyboardButton("Change Property Type")
        button_bathrooms = types.KeyboardButton("Change Bathrooms")
        button_bedrooms = types.KeyboardButton("Change Bedrooms")
        button_floor = types.KeyboardButton("Change Floor")
        button_elevator = types.KeyboardButton("Change Elevator")
        button_solarium = types.KeyboardButton("Change Solarium")
        button_parking = types.KeyboardButton("Change Parking")
        button_pool = types.KeyboardButton("Change Pool")
        button_beach = types.KeyboardButton("Change Beach")
        button_location = types.KeyboardButton("Change Location")
        button_gas = types.KeyboardButton("Central Gas System")
        button_panels = types.KeyboardButton("Solar Panels for Watter Heating")
        button_landlord_name = types.KeyboardButton("Change Landlord Name")
        button_landlord_num = types.KeyboardButton("Change Landlord Number")
        button_landlord_status = types.KeyboardButton("Change Landlord Status")

        button_photos = types.KeyboardButton("Manage Photos")

        button_back = types.KeyboardButton("Back")

        markup.row(button_address, button_prop)
        markup.row(button_bathrooms, button_bedrooms)
        markup.row(button_floor, button_elevator)
        markup.row(button_solarium, button_parking)
        markup.row(button_beach, button_gas)
        markup.add(button_pool)
        if service_type == "rent":
            button_pets = types.KeyboardButton("Change Pets")
            button_price_day = types.KeyboardButton("Change Price Per Day")
            button_price_week = types.KeyboardButton("Change Price Per Week")
            button_price_month = types.KeyboardButton("Change Price Per Month")
            button_date = types.KeyboardButton("Change Availability Date")
            markup.add(button_pets)
            markup.add(button_price_day)
            markup.add(button_price_week)
            markup.add(button_price_month)
            markup.add(button_date)
        elif service_type == "sale":
            button_price = types.KeyboardButton("Change Price")
            markup.add(button_price)

        markup.row(button_beach, button_gas)

        markup.row(button_panels, button_location)
        markup.row(button_landlord_name, button_landlord_num, button_landlord_status)
        markup.add(button_photos)
        markup.add(button_back)

        return markup

    @staticmethod
    def add_client_handler_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button_add = types.KeyboardButton("Add Client")
        button_show_all = types.KeyboardButton("Show All My Clients")
        button_back = types.KeyboardButton("Back To Main Menu")

        markup.row(button_add, button_show_all)
        markup.row(button_back)
        return markup

    @staticmethod
    def share_object_client_markup(clients):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for client in clients:
            current_btn = types.KeyboardButton(client)
            markup.add(current_btn)
        markup.add(types.KeyboardButton("Back"))
        return markup

    @staticmethod
    def share_object_language_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button_eng = types.KeyboardButton("English")
        button_esp = types.KeyboardButton("Español")
        button_pol = types.KeyboardButton("Polish")
        button_nor = types.KeyboardButton("Norwegian")
        button_swed = types.KeyboardButton("Swedish")
        button_french = types.KeyboardButton("French")
        button_ger = types.KeyboardButton("German")
        button_rus = types.KeyboardButton("Russian")
        button_back = types.KeyboardButton("Back")

        markup.row(button_eng, button_esp)
        markup.row(button_pol, button_nor)
        markup.row(button_swed, button_french)
        markup.row(button_ger, button_rus)
        markup.add(button_back)

        return markup

    @staticmethod
    def show_clients_markup(total_buttons):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for index in range(total_buttons):
            btn_next = types.KeyboardButton("Client № " + str(index + 1))
            markup.add(btn_next)

        btn_next = types.KeyboardButton("Next Page")
        btn_prev = types.KeyboardButton("Previous Page")
        markup.row(btn_prev, btn_next)

        button_back = types.KeyboardButton("Back")
        markup.row(button_back)

        return markup

    @staticmethod
    def admin_list_of_objects_markup(total_buttons, objects_name):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for index in range(total_buttons):
            btn_next = types.KeyboardButton(
                f"{objects_name.title()} № " + str(index + 1)
            )
            markup.add(btn_next)

        btn_next = types.KeyboardButton("Next Page")
        btn_prev = types.KeyboardButton("Previous Page")
        markup.row(btn_prev, btn_next)

        button_back = types.KeyboardButton("Back")
        markup.row(button_back)

        return markup

    @staticmethod
    def edit_client_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn_name = types.KeyboardButton("Edit Name")
        btn_num = types.KeyboardButton("Edit Number")
        btn_note = types.KeyboardButton("Edit Note")
        btn_back = types.KeyboardButton("Back")

        markup.row(btn_name, btn_num)
        markup.row(btn_note)
        markup.add(btn_back)

        return markup

    @staticmethod
    def admin_panel_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn_managers = types.KeyboardButton("Moderate Managers")
        btn_report = types.KeyboardButton("Generate last 7 days report")
        btn_quick = types.KeyboardButton("Quick Access to Object by Id")
        btn_admins = types.KeyboardButton("Add Admin")
        btn_number = types.KeyboardButton("Change Agency Number")
        btn_activate = types.KeyboardButton("Restore access to manager")
        btn_back = types.KeyboardButton("Back")

        markup.add(btn_managers)
        markup.add(btn_report)
        markup.add(btn_quick)
        markup.add(btn_admins)
        markup.add(btn_number)
        markup.add(btn_activate)
        markup.add(btn_back)

        return markup

    @staticmethod
    def moderate_managers_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn_add_manager = types.KeyboardButton("Add New Manager")
        btn_choose_manager = types.KeyboardButton("Find and Moderate Manager")
        btn_back = types.KeyboardButton("Back")

        markup.add(btn_add_manager)
        markup.add(btn_choose_manager)

        markup.add(btn_back)

        return markup

    @staticmethod
    def moderate_manager_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn_view_obj = types.KeyboardButton("View Objects")
        btn_edit = types.KeyboardButton("Edit Manager")
        btn_view_clients = types.KeyboardButton("View Clients")
        btn_allow = types.KeyboardButton("Allow to use his personal number")
        btn_restrict = types.KeyboardButton("Restrict access to the system")

        btn_back = types.KeyboardButton("Back")

        markup.add(btn_edit)
        markup.add(btn_view_obj)
        markup.add(btn_view_clients)
        markup.add(btn_allow)
        markup.add(btn_restrict)
        markup.add(btn_back)
        return markup

    @staticmethod
    def edit_particular_manager_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        btn_edit_name = types.KeyboardButton("Edit Name")
        btn_edit_number = types.KeyboardButton("Edit Number")
        btn_edit_username = types.KeyboardButton("Edit Username")
        btn_back = types.KeyboardButton("Back")

        markup.add(btn_edit_name)
        markup.add(btn_edit_number)
        markup.add(btn_edit_username)
        markup.add(btn_back)

        return markup

    @staticmethod
    def admin_object_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        btn_redirect = types.KeyboardButton("Redirect This Object to Other Manager")
        btn_back = types.KeyboardButton("Back")

        markup.add(btn_redirect)
        markup.add(btn_back)

        return markup

    @staticmethod
    def admin_client_markup():
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        btn_redirect = types.KeyboardButton("Redirect This Client to Other Manager")
        btn_back = types.KeyboardButton("Back")

        markup.add(btn_redirect)
        markup.add(btn_back)

        return markup
