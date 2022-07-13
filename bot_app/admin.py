from report_generator import ReportGenerator
from telebot import types


class Admin:
    def __init__(self, bot, markups, inline_markups, db_repo, command_start):
        self.bot = bot
        self.markups = markups
        self.inline_markups = inline_markups
        self.db_repo = db_repo
        self.command_start = command_start

    def admin_panel(self, message):
        self.bot.send_message(
            message.chat.id,
            f"Greetings, {message.from_user.username}!\n"
            f"You entered an admin panel.\n"
            f"Please, choose what you want to do",
            reply_markup=self.markups.admin_panel_markup(),
        )
        self.bot.register_next_step_handler(message, self.process_admin_panel_response)

    def process_admin_panel_response(self, message):
        if not message.content_type == "text":
            self.admin_panel(message)
            return
        if message.text == "Moderate Managers":
            self.moderate_managers(message)
        elif message.text == "Generate last 7 days report":
            report_generator = ReportGenerator(self.bot, self.db_repo)
            report_generator.generate_report(message)
            self.admin_panel(message)
        elif message.text == "Quick Access to Object by Id":
            self.quick_asses(message)
        elif message.text == "Add Admin":
            self.add_admin(message)
        elif message.text == "Restore access to manager":
            self.choose_objects(message, "banned manager")
        elif message.text == "Change Agency Number":
            self.change_agency_number(message)
        elif message.text == "Back":
            self.command_start(message)
        else:
            self.admin_panel(message)

    def quick_asses(self, message):
        self.bot.send_message(message.chat.id, "Please , send ID of the Object")
        self.bot.register_next_step_handler(message, self.process_quick_access)

    def process_quick_access(self, message):
        if not message.content_type == "text":
            self.admin_panel(message)
        object_is_exist = False
        obj = object
        try:
            obj = self.db_repo.admin_get_object_by_fake_id(message.text.strip())
            if obj is not None:
                object_is_exist = True
        except:
            pass

        if object_is_exist:
            self.print_manager_product(message, obj.id, show_manager=True)
        else:
            self.bot.send_message(
                message.chat.id, f"No object with ID {message.text.strip()}"
            )
            self.admin_panel(message)

    def change_agency_number(self, message):
        self.bot.send_message(message.chat.id, "Please, sens a new agency number")
        self.bot.register_next_step_handler(
            message, self.process_changing_agency_number
        )

    def process_changing_agency_number(self, message):
        if not message.content_type == "text":
            self.admin_panel(message)
            return
        else:
            number = self.db_repo.get_agency_number()
            number.number = message.text.strip()
            number.save()
            self.admin_panel(message)

    def restore_access_to_managers(self, message, manager_id):
        manager = self.db_repo.get_manager_by_id(manager_id)

        current_message = (
            f"Name: {manager.name}\n"
            f"Number: {manager.number}\n"
            f"Username: {manager.username}\n"
            f"Are you sure to restore access to this manager?"
        )

        self.bot.send_message(
            message.chat.id, current_message, reply_markup=self.markups.yes_no_markup()
        )
        self.bot.register_next_step_handler(
            message, self.process_restoring_access_to_banned_manager, manager_id
        )

    def process_restoring_access_to_banned_manager(self, message, manager_id):
        if not message.content_type == "text":
            self.admin_panel(message)
            return

        if message.text == "Yes":
            manager = self.db_repo.get_manager_by_id(manager_id)
            manager.is_active = True
            manager.save()
            self.bot.send_message(
                message.from_user.id,
                f"Manager {manager.name} has gained the access to system",
            )

        self.admin_panel(message)

    def add_admin(self, message):
        self.bot.send_message(message.chat.id, "Please , send name of new admin...")
        self.bot.register_next_step_handler(message, self.get_new_admin_name)

    def get_new_admin_name(self, message):
        if not message.content_type == "text":
            self.admin_panel(message)
            return
        else:
            new_admin = {"name": message.text.strip()}
            self.get_new_admin_number(message, new_admin)

    def get_new_admin_number(self, message, new_admin):
        self.bot.send_message(message.chat.id, "Please , send number of new admin...")
        self.bot.register_next_step_handler(
            message, self.process_getting_new_admin_number, new_admin
        )

    def process_getting_new_admin_number(self, message, new_admin):
        if not message.content_type == "text":
            self.admin_panel(message)
            return
        else:
            new_admin["number"] = message.text.strip()
            self.get_new_admin_username(message, new_admin)

    def get_new_admin_username(self, message, new_admin):
        self.bot.send_message(message.chat.id, "Please , send username of new admin...")
        self.bot.register_next_step_handler(
            message, self.process_getting_new_admin_username, new_admin
        )

    def process_getting_new_admin_username(self, message, new_admin):
        if not message.content_type == "text":
            self.admin_panel(message)
            return
        else:
            if "@" in message.text:
                new_admin["username"] = message.text[1 : len(message.text)].strip()
                self.ask_if_to_add_new_admin(message, new_admin)
            else:
                new_admin["username"] = message.text.strip()
                self.ask_if_to_add_new_admin(message, new_admin)

    def ask_if_to_add_new_admin(self, message, new_admin):
        self.bot.send_message(
            message.chat.id,
            "‼️ BE CAREFUL️ ‼️️\n"
            "in terms of security, there is no way to delete existing admin\n"
            "Are you really sure to add new admin?",
            reply_markup=self.markups.yes_no_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_adding_new_admin_answer, new_admin
        )

    def process_adding_new_admin_answer(self, message, new_admin):
        if not message.content_type == "text":
            self.bot.send_message(
                message.chat.id, "wrong answer, redirecting back to admin panel"
            )
            self.admin_panel(message)
            return

        if message.text == "Yes":
            self.db_repo.add_admin_and_manager(new_admin)
            self.bot.send_message(
                message.chat.id, f"admin {new_admin['name']} was added"
            )

        self.admin_panel(message)

    def moderate_managers(self, message):
        self.bot.send_message(
            message.chat.id,
            "This section allows you to moderate managers.\n"
            "Please, choose what you want to do...",
            reply_markup=self.markups.moderate_managers_markup(),
        )
        self.bot.register_next_step_handler(message, self.process_moderating_managers)

    def process_moderating_managers(self, message):
        if not message.content_type == "text":
            self.moderate_managers(message)
            return

        if message.text == "Add New Manager":
            self.add_manager(message)
        elif message.text == "Find and Moderate Manager":
            self.choose_objects(message, "manager")
        elif message.text == "Back":
            self.admin_panel(message)
            return
        else:
            self.moderate_managers(message)
            return

    def choose_objects(self, message, look_for, **kwargs):
        print("gotcha")
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]
        current_message = ""
        objects_to_work = []

        if look_for == "manager":
            objects_to_work = self.db_repo.get_all_active_managers_admin()

            current_message = "This is your list of the managers:\n\n"


        if look_for == "banned manager":
            objects_to_work = self.db_repo.get_all_banned_managers_admin()
            current_message = "This is your list of the banned managers:\n\n"

        page_count = len(objects_to_work) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1
        page_count = int(page_count)

        total_buttons = 0
        for index, client in enumerate(objects_to_work[page * 5 - 5 : page * 5]):
            current_message += self.__generate_objects_to_work_string(
                index, client, look_for
            )
            total_buttons += 1

        page_info = {"page": page, "page_count": page_count, "look_for": look_for}

        current_message += f"Page {page} / {page_count}"

        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.admin_list_of_objects_markup(
                total_buttons, look_for
            ),
            parse_mode="HTML",
        )
        self.bot.register_next_step_handler(
            message, self.process_showing_objects_response, page_info
        )

    @staticmethod
    def __generate_objects_to_work_string(index, obj, look_for):
        if look_for == "manager":
            return (
                f"<b>{index + 1}</b>:Name: {obj.name}\nNumber: {obj.number}\n"
                f"<b>Username:</b>\n@{obj.username}\n\n"
            )

        if look_for == "banned manager":
            return (
                f"<b>{index + 1}</b>:Name: {obj.name}\nNumber: {obj.number}\n"
                f"<b>Username:</b>\n@{obj.username}\n\n"
            )

        if look_for == "city":
            return f"<b>{index + 1}: {obj.city_name}</b>\n\n"

        if look_for == "property":
            return (
                f"<b>{index + 1}</b>. <b>ID</b>: {obj.fake_id}\n"
                f"<b>Address</b>: {obj.address}\n"
                f"<b>Property Type</b>: {obj.property_type}\n"
                f"<b>Bedrooms</b>: {obj.bedrooms}\n\n"
            )

        if look_for == "client":
            return (
                f"<b>{index +1}</b>. Name :{obj.name}\n"
                f"Number {obj.number}\n"
                f"Note: {obj.note}\n\n"
            )

    def process_showing_objects_response(self, message, page_info):
        if not message.content_type == "text":
            self.admin_panel(message)
            return

        if page_info["look_for"].title() + " №" in message.text:
            index = (
                int(message.text[message.text.index("№") + 1 : len(message.text)]) - 1
            )
            try:
                if page_info["look_for"] == "manager":
                    managers = self.db_repo.get_all_active_managers_admin()
                    manager_id = managers[page_info["page"] * 5 - 5 + index].id

                    self.moderate_particular_manager(message, manager_id)
                    return
                if page_info["look_for"] == "banned manager":
                    banned = self.db_repo.get_all_banned_managers_admin()
                    manager_id = banned[page_info["page"] * 5 - 5 + index].id
                    self.restore_access_to_managers(message, manager_id)
                    return
            except:
                pass

        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            self.choose_objects(
                message, page_info["look_for"], page=page_info["page"] + 1
            )
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            self.choose_objects(
                message, page_info["look_for"], page=page_info["page"] - 1
            )
            return
        elif message.text == "Back":
            self.admin_panel(message)
            return
        else:
            self.choose_objects(message, page_info["look_for"], page=page_info["page"])
            return
        self.choose_objects(message, page_info["look_for"], page=page_info["page"])

    def moderate_particular_manager(self, message, manager_id):
        manager = self.db_repo.get_manager_by_id(manager_id)
        current_message = "Current Manager is:\n"
        current_message += (
            f"Name:{manager.name}\n"
            f"Number: {manager.number}\n"
            f"Username: {manager.username}\n"
        )
        current_message += "Please, choose what you want to do..."
        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.moderate_manager_markup(),
        )

        self.bot.register_next_step_handler(
            message, self.process_moderating_particular_manager, manager_id
        )

    def process_moderating_particular_manager(self, message, manager_id):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, manager_id)

        if message.text == "View Objects":
            self.show_cities_to_choose(message, manager_id)
        elif message.text == "Edit Manager":
            self.edit_particular_manager(message, manager_id)
        elif message.text == "View Clients":
            self.view_manager_clients(message, manager_id)
        elif message.text == "Allow to use his personal number":
            self.allow_manager_to_use_his_personal_number(message, manager_id)
        elif message.text == "Restrict access to the system":
            self.restrict_access_to_the_manager(message, manager_id)
        elif message.text == "Back":
            self.moderate_managers(message)

        else:
            self.moderate_managers(message)

    def view_manager_clients(self, message, manager_id, **kwargs):
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]

        clients = self.db_repo.get_all_clients_by_manager_username(
            self.db_repo.get_manager_by_id(manager_id).username
        )

        current_message = "Please Choose the Cleint...\n\n"

        page_count = len(clients) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1
        page_count = int(page_count)

        total_buttons = 0
        for index, client in enumerate(clients[page * 5 - 5 : page * 5]):
            current_message += self.__generate_objects_to_work_string(
                index, client, "client"
            )
            total_buttons += 1

        current_message += f"Page {page} / {page_count}"

        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.admin_list_of_objects_markup(
                total_buttons, "client"
            ),
            parse_mode="HTML",
        )
        page_info = {"page": page, "page_count": page_count, "manager_id": manager_id}
        self.bot.register_next_step_handler(
            message, self.process_showing_the_clients_to_choose, page_info
        )

    def process_showing_the_clients_to_choose(self, message, page_info):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, page_info["manager_id"])
            return

        if "Client №" in message.text:
            index = (
                int(message.text[message.text.index("№") + 1 : len(message.text)]) - 1
            )
            client = self.db_repo.get_all_clients_by_manager_username(
                self.db_repo.get_manager_by_id(page_info["manager_id"]).username
            )
            client_id = client[page_info["page"] * 5 - 5 + index].id
            self.show_manager_client(
                message, {"client_id": client_id, "manager_id": page_info["manager_id"]}
            )

        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            self.view_manager_clients(
                message, page_info["manager_id"], page=page_info["page"] + 1
            )
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            self.view_manager_clients(
                message, page_info["manager_id"], page=page_info["page"] - 1
            )
            return
        elif message.text == "Back":
            self.moderate_particular_manager(message, page_info["manager_id"])
            return
        else:
            self.view_manager_clients(
                message, page_info["manager_id"], page=page_info["page"]
            )

    def show_manager_client(self, message, manager_and_client):
        client = self.db_repo.get_client_by_id(manager_and_client["client_id"])

        current_message = (
            f"Client Name : {client.name}\n"
            f"Number: {client.number}\n"
            f"Note: {client.note}\n\n"
            f"What you want to do?"
        )
        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.admin_client_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_showing_client_of_the_manager, manager_and_client
        )

    def process_showing_client_of_the_manager(self, message, manager_and_client):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, manager_and_client["manager_id"])
            return

        if message.text == "Redirect This Client to Other Manager":
            self.show_managers_to_redirect_the_client(message, manager_and_client)
        elif message.text == "Back":
            self.moderate_particular_manager(message, manager_and_client["manager_id"])
        else:
            self.moderate_particular_manager(message, manager_and_client["manager_id"])

    def show_managers_to_redirect_the_client(
        self, message, manager_and_client, **kwargs
    ):
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]

        managers = self.db_repo.get_all_active_managers_admin()
        current_message = "This is your list of the managers:\n\n"

        page_count = len(managers) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1
        page_count = int(page_count)

        total_buttons = 0
        for index, client in enumerate(managers[page * 5 - 5 : page * 5]):
            current_message += self.__generate_objects_to_work_string(
                index, client, "manager"
            )
            total_buttons += 1

        current_message += f"Page {page} / {page_count}"

        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.admin_list_of_objects_markup(
                total_buttons, "manager"
            ),
            parse_mode="HTML",
        )
        page_info = {
            "page": page,
            "page_count": page_count,
            "manager_and_client": manager_and_client,
        }
        self.bot.register_next_step_handler(
            message, self.process_showing_managers_to_redirect_the_client, page_info
        )

    def process_showing_managers_to_redirect_the_client(self, message, page_info):
        if not message.content_type == "text":
            self.moderate_particular_manager(
                message, page_info["manager_and_client"]["manager_id"]
            )
            return

        if "Manager №" in message.text:
            index = (
                int(message.text[message.text.index("№") + 1 : len(message.text)]) - 1
            )
            managers = self.db_repo.get_all_active_managers_admin()
            manager_id = managers[page_info["page"] * 5 - 5 + index].id
            self.redirect_client_to_manager(
                message, page_info["manager_and_client"]["client_id"], manager_id
            )

        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            self.show_managers_to_redirect_the_client(
                message,
                page_info["manager_and_client"]["manager_id"],
                page=page_info["page"] + 1,
            )
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            self.show_managers_to_redirect_the_client(
                message,
                page_info["manager_and_client"]["manager_id"],
                page=page_info["page"] - 1,
            )
            return
        elif message.text == "Back":
            self.moderate_particular_manager(message, page_info["manager_id"])
            return
        else:
            self.show_managers_to_redirect_the_client(
                message,
                page_info["manager_and_client"]["manager_id"],
                page=page_info["page"],
            )

    def redirect_client_to_manager(self, message, client_id, manager_to_redirect_id):
        client = self.db_repo.get_client_by_id(client_id)
        current_manager = client.related_to_manager
        client.related_to_manager = manager_to_redirect_id
        manager_to_redirect = self.db_repo.get_manager_by_id(manager_to_redirect_id)
        client.save()
        self.bot.send_message(
            message.chat.id,
            f"Client {client.name} was redirected to manager {manager_to_redirect.name}",
        )
        self.moderate_particular_manager(message, current_manager)

    def show_cities_to_choose(self, message, manager_id, **kwargs):
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]
        cities = self.db_repo.get_all_cities()

        current_message = "Please Choose the city...\n\n"

        page_count = len(cities) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1
        page_count = int(page_count)

        total_buttons = 0
        for index, client in enumerate(cities[page * 5 - 5 : page * 5]):
            current_message += self.__generate_objects_to_work_string(
                index, client, "city"
            )
            total_buttons += 1

        current_message += f"Page {page} / {page_count}"

        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.admin_list_of_objects_markup(
                total_buttons, "city"
            ),
            parse_mode="HTML",
        )
        page_info = {"page": page, "page_count": page_count, "manager_id": manager_id}
        self.bot.register_next_step_handler(
            message, self.process_showing_the_cities_to_choose, page_info
        )

    def process_showing_the_cities_to_choose(self, message, page_info):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, page_info["manager_id"])
            return

        if "City №" in message.text:
            index = (
                int(message.text[message.text.index("№") + 1 : len(message.text)]) - 1
            )
            cities = self.db_repo.get_all_cities()
            city_id = cities[page_info["page"] * 5 - 5 + index].id
            self.get_service_type(
                message, {"city_id": city_id, "manager_id": page_info["manager_id"]}
            )

        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            self.show_cities_to_choose(
                message, page_info["manager_id"], page=page_info["page"] + 1
            )
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            self.show_cities_to_choose(
                message, page_info["manager_id"], page=page_info["page"] - 1
            )
            return
        elif message.text == "Back":
            self.moderate_particular_manager(message, page_info["manager_id"])
            return
        else:
            self.show_cities_to_choose(
                message, page_info["manager_id"], page=page_info["page"]
            )

    def get_service_type(self, message, current_filters):
        self.bot.send_message(
            message.chat.id,
            "Please , choose service type...",
            reply_markup=self.markups.get_service_type_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_service_type, current_filters
        )

    def process_getting_service_type(self, message, current_filters):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, current_filters["manager_id"])
            return

        if message.text == "Rent":
            current_filters["service type"] = "rent"
            self.show_property_objects_to_choose(message, current_filters)
        elif message.text == "Sale":
            current_filters["service type"] = "sale"
            self.show_property_objects_to_choose(message, current_filters)
        else:
            self.moderate_particular_manager(message, current_filters["manager_id"])

    def show_property_objects_to_choose(self, message, current_filters, **kwargs):
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]
        properties = self.db_repo.get_all_manager_objects(current_filters, admin=True)

        if len(properties) == 0:
            self.moderate_particular_manager(message, current_filters["manager_id"])
            return

        current_message = "Please Choose the the object...\n\n"

        page_count = len(properties) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1
        page_count = int(page_count)

        total_buttons = 0
        for index, client in enumerate(properties[page * 5 - 5 : page * 5]):
            current_message += self.__generate_objects_to_work_string(
                index, client, "property"
            )
            total_buttons += 1

        current_message += f"Page {page} / {page_count}"

        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.admin_list_of_objects_markup(
                total_buttons, "property"
            ),
            parse_mode="HTML",
        )
        page_info = {
            "page": page,
            "page_count": page_count,
            "current_filters": current_filters,
        }
        self.bot.register_next_step_handler(
            message, self.process_showing_objects_to_choose, page_info
        )

    def process_showing_objects_to_choose(self, message, page_info):
        if "Property №" in message.text:
            index = (
                int(message.text[message.text.index("№") + 1 : len(message.text)]) - 1
            )
            properties = self.db_repo.get_all_manager_objects(
                page_info["current_filters"], admin=True
            )
            product_id = properties[page_info["page"] * 5 - 5 + index].id

            self.print_manager_product(message, product_id)

        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            self.show_property_objects_to_choose(
                message, page_info["current_filters"], page=page_info["page"] + 1
            )
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            self.show_property_objects_to_choose(
                message, page_info["current_filters"], page=page_info["page"] - 1
            )
            return
        elif message.text == "Back":
            self.moderate_particular_manager(
                message, page_info["current_filters"]["manager_id"]
            )
            return
        else:
            self.show_property_objects_to_choose(
                message, page_info["current_filters"], page=page_info["page"]
            )

    def print_manager_product(self, message, product_id, **kwargs):
        object_to_print = self.db_repo.get_object_by_id_for_object_menu(product_id)
        object_json = object_to_print.__data__
        (
            current_message,
            media_group,
            __,
        ) = self.__generate_message_string_and_media_group_for_object_by_id(product_id)

        if "show_manager" in kwargs:
            current_message += f"\n\nManager username: @{self.db_repo.get_manager_by_id(object_to_print.related_to_manager_id).username}"
        if len(object_to_print.photos) > 0:
            self.bot.send_media_group(chat_id=message.chat.id, media=media_group)
        self.bot.send_message(
            message.chat.id,
            current_message,
            parse_mode="HTML",
            reply_markup=self.markups.admin_object_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_showing_manager_object, object_json["id"]
        )

    def process_showing_manager_object(self, message, object_id):
        if not message.content_type == "text":
            obj = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.edit_particular_manager(message, obj.related_to_manager.id)
            return

        if message.text == "Back":
            obj = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.edit_particular_manager(message, obj.related_to_manager.id)
            return
        elif message.text == "Redirect This Object to Other Manager":
            self.redirect_object_to_other_manager(message, object_id)
        else:
            obj = self.db_repo.get_object_by_id_for_object_menu(object_id)
            self.edit_particular_manager(message, obj.related_to_manager.id)

    def redirect_object_to_other_manager(self, message, object_id, **kwargs):
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]
        managers = self.db_repo.get_all_active_managers_admin()

        if len(managers) == 0:
            self.moderate_particular_manager(message, object_id)
            return

        current_message = (
            "Please Choose the the manager you want to redirect the object...\n\n"
        )

        page_count = len(managers) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1
        page_count = int(page_count)

        total_buttons = 0
        for index, client in enumerate(managers[page * 5 - 5 : page * 5]):
            current_message += self.__generate_objects_to_work_string(
                index, client, "manager"
            )
            total_buttons += 1

        current_message += f"Page {page} / {page_count}"

        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.admin_list_of_objects_markup(
                total_buttons, "manager"
            ),
            parse_mode="HTML",
        )
        page_info = {
            "page": page,
            "page_count": page_count,
            "object_id": object_id,
        }
        self.bot.register_next_step_handler(
            message, self.process_showing_redirecting_object, page_info
        )

    def process_showing_redirecting_object(self, message, page_info):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, page_info["manager_id"])
            return

        if "Manager №" in message.text:
            index = (
                int(message.text[message.text.index("№") + 1 : len(message.text)]) - 1
            )
            managers = self.db_repo.get_all_active_managers_admin()
            manager_to_redirect_id = managers[page_info["page"] * 5 - 5 + index].id
            self.redirect_object_to_manager(
                message, page_info["object_id"], manager_to_redirect_id, one_time=True
            )

        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            manager = self.db_repo.get_object_by_id_for_object_menu(
                page_info["object_id"]
            ).related_to_manager
            self.redirect_object_to_other_manager(
                message, manager, page=page_info["page"] + 1
            )
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            manager = self.db_repo.get_object_by_id_for_object_menu(
                page_info["object_id"]
            ).related_to_manager
            self.redirect_object_to_other_manager(
                message, manager, page=page_info["page"] - 1
            )
            return
        elif message.text == "Back":
            manager = self.db_repo.get_object_by_id_for_object_menu(
                page_info["object_id"]
            ).related_to_manager
            self.redirect_object_to_other_manager(message, manager)
            return
        else:
            manager = self.db_repo.get_object_by_id_for_object_menu(
                page_info["object_id"]
            ).related_to_manager
            self.redirect_object_to_other_manager(message, manager)

    def redirect_object_to_manager(
        self, message, object_id, manager_to_redirect, **kwargs
    ):
        obj = self.db_repo.get_object_by_id_for_object_menu(object_id)
        current_manager = obj.related_to_manager.name
        obj.related_to_manager = manager_to_redirect
        obj.save()
        if "one_time" in kwargs:
            self.bot.send_message(
                message.chat.id,
                f"{obj.fake_id} was redirected from {current_manager} to "
                f"{self.db_repo.get_manager_by_id(manager_to_redirect).name }",
            )
            self.moderate_particular_manager(message, obj.related_to_manager)

    def allow_manager_to_use_his_personal_number(self, message, manager_id):
        self.bot.send_message(
            message.chat.id,
            "Allow this manager to use his/her personal number\n"
            "while sharing the object link?",
            reply_markup=self.markups.yes_no_markup(),
        )
        self.bot.register_next_step_handler(
            message,
            self.process_allowing_manager_to_use_his_personal_number,
            manager_id,
        )

    def process_allowing_manager_to_use_his_personal_number(self, message, manager_id):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, manager_id)
            return

        if message.text == "Yes":
            manager = self.db_repo.get_manager_by_id(manager_id)
            manager.allowed_to_use_personal_number = True
            manager.save()
            self.bot.send_message(
                message.chat.id,
                f"Manager {manager.name} "
                f"is now allowed to use his/her personal number.",
            )

        self.moderate_particular_manager(message, manager_id)

    def edit_particular_manager(self, message, manager_id):
        manager = self.db_repo.get_manager_by_id(manager_id)
        current_message = (
            f"Manager specs are:\n"
            f"Name: {manager.name}\n"
            f"Number: {manager.number}\n"
            f"Username: {manager.username}\n"
        )
        current_message += "Please, choose what you want to change..."
        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.edit_particular_manager_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_editing_particular_manager, manager_id
        )

    def process_editing_particular_manager(self, message, manager_id):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, manager_id)
            return

        if message.text == "Edit Name":
            specs = {"id": manager_id, "spec": "name"}
            self.edit_spec_of_particular_manager(message, specs)
        elif message.text == "Edit Number":
            specs = {"id": manager_id, "spec": "number"}
            self.edit_spec_of_particular_manager(message, specs)
        elif message.text == "Edit Username":
            specs = {"id": manager_id, "spec": "username"}
            self.edit_spec_of_particular_manager(message, specs)
        elif message.text == "Back":
            self.moderate_particular_manager(message, manager_id)
        else:
            self.moderate_particular_manager(message, manager_id)

    def edit_spec_of_particular_manager(self, message, specs):
        spec = specs["spec"]
        self.bot.send_message(
            message.chat.id, f"Please enter new " + str(spec) + " for this manager"
        )
        self.bot.register_next_step_handler(
            message, self.process_editing_spec_of_particular_manager, specs
        )

    def process_editing_spec_of_particular_manager(self, message, specs):
        if not message.content_type == "text":
            self.moderate_particular_manager(message, specs["manager_id"])
            return

        if specs["spec"] == "name":
            spec_id = specs["id"]
            manager = self.db_repo.get_manager_by_id(spec_id)
            manager.name = message.text.strip()
            manager.save()
        elif specs["spec"] == "number":
            spec_id = specs["id"]
            manager = self.db_repo.get_manager_by_id(spec_id)
            manager.number = message.text.strip()
            manager.save()
        elif specs["spec"] == "username":
            spec_id = specs["id"]
            manager = self.db_repo.get_manager_by_id(spec_id)
            manager.username = message.text.strip()
            manager.save()

        self.edit_particular_manager(message, specs["id"])

    def restrict_access_to_the_manager(self, message, manager_id):
        self.bot.send_message(
            message.chat.id,
            f"Are yoy sure you want to restrict access to this manager?",
            reply_markup=self.markups.yes_no_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_restricting_access_to_manager, manager_id
        )

    def process_restricting_access_to_manager(self, message, manager_id):
        manager = self.db_repo.get_manager_by_id(manager_id)
        manager.is_active = False
        manager.save()

        self.bot.send_message(
            message.chat.id,
            f"Manager {manager.name} was restricted to use this system.",
        )
        self.moderate_managers(message)

    def add_manager(self, message):
        self.bot.send_message(message.chat.id, "Please, send name of a new Manager...")
        self.bot.register_next_step_handler(
            message, self.process_getting_new_manager_name
        )

    def process_getting_new_manager_name(self, message):
        if not message.content_type == "text":
            self.moderate_managers(message)
            return
        else:
            new_manager = {"name": message.text.strip().title()}
            self.get_new_manager_number(message, new_manager)

    def get_new_manager_number(self, message, new_manager):
        self.bot.send_message(
            message.chat.id,
            "Please, send number of a new Manager...",
        )
        self.bot.register_next_step_handler(
            message, self.process_getting_new_manager_number, new_manager
        )

    def process_getting_new_manager_number(self, message, new_manager):
        if not message.content_type == "text":
            self.moderate_managers(message)
            return
        else:
            new_manager["number"] = message.text.strip().title()
            self.get_new_manager_username(message, new_manager)

    def get_new_manager_username(self, message, new_manager):
        self.bot.send_message(
            message.chat.id,
            "Please , specify new Manager Username."
            "To find a telegram username, open his profile by clicking his/her "
            "picture in a private chat or group."
            "Please note that the username is not set automatically when "
            "creating a telegram account. To set it, you need to go"
            " through the settings in the 'edit profile' section."
            "After you add the username, the system will automatically "
            "grant access to the manager and he does not need to go through registration.",
        )

        self.bot.register_next_step_handler(
            message, self.process_getting_new_manager_username, new_manager
        )

    def process_getting_new_manager_username(self, message, new_manager):
        if not message.content_type == "text":
            self.moderate_managers(message)
            return
        else:
            if "@" in message.text:
                new_manager["username"] = message.text[1 : len(message.text)].strip()
                self.ask_to_add_username(message, new_manager)
            else:
                new_manager["username"] = message.text.strip()
                self.ask_to_add_username(message, new_manager)

    def ask_to_add_username(self, message, new_manager):
        self.bot.send_message(
            message.chat.id,
            f"You entered the following specifications:\n"
            f"Name: {new_manager['name']}\n"
            f"Number: {new_manager['number']}\n"
            f"username: {new_manager['username']}\n"
            f"Add this Manager",
            reply_markup=self.markups.yes_no_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.add_new_manager_to_database, new_manager
        )

    def add_new_manager_to_database(self, message, new_manager):
        if not message.content_type == "text":
            self.moderate_managers(message)
            return

        if message.text == "Yes":
            self.db_repo.add_new_manager(new_manager)
            self.bot.send_message(
                message.chat.id, f"Manager {new_manager['name']} was added"
            )
            self.moderate_managers(message)
        else:
            self.moderate_managers(message)

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
