class AddClientHandlers:
    def __init__(self, bot, markups, inline_markups, db_repo, command_start):
        self.bot = bot
        self.markups = markups
        self.inline_markups = inline_markups
        self.db_repo = db_repo
        self.command_start = command_start

    def add_client_handler(self, message):
        self.bot.send_message(
            message.chat.id,
            "This menu allow you to create and delete clients",
            reply_markup=self.markups.add_client_handler_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_add_client_handler_response
        )

    def process_add_client_handler_response(self, message):
        if not message.content_type == "text":
            self.add_client_handler(message)
            return
        if message.text == "Add Client":
            self.get_client_name(message)
        elif message.text == "Show All My Clients":
            self.show_clients(message)
        elif message.text == "Back To Main Menu":
            self.command_start(message)
            return

    def show_clients(self, message, **kwargs):
        page = 1
        if "page" in kwargs:
            page = kwargs["page"]

        clients = self.db_repo.get_all_clients_by_manager_username(
            message.from_user.username
        )
        page_count = len(clients) / 5

        if page_count % 1 != 0:
            page_count = int(page_count) + 1
        page_count = int(page_count)
        current_message = "This is your list of the clients:\n\n"
        total_buttons = 0
        for index, client in enumerate(clients[page * 5 - 5 : page * 5]):
            current_message += self.__generate_client_string(index, client)
            total_buttons += 1

        current_message += f"Page {page} / {page_count}"
        page_info = {"page": page, "page_count": page_count}
        self.bot.send_message(
            message.chat.id,
            current_message,
            reply_markup=self.markups.show_clients_markup(total_buttons),
            parse_mode="HTML",
        )
        self.bot.register_next_step_handler(
            message, self.process_showing_client_response, page_info
        )

    @staticmethod
    def __generate_client_string(index, client):
        return (
            f"<b>{index + 1}</b>:Name: {client.name}\nNumber: {client.number}\n"
            f"<b>Note:</b>\n{client.note}\n\n"
        )

    def process_showing_client_response(self, message, page_info):
        if not message.content_type == "text":
            self.add_client_handler(message)
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
                client_id = clients[page_info["page"] * 5 - 5 + index].id
                self.edit_client(message, client_id)
                return
            except:
                pass
        elif (
            message.text == "Next Page"
            and page_info["page"] + 1 <= page_info["page_count"]
        ):
            self.show_clients(message, page=page_info["page"] + 1)
            return
        elif message.text == "Previous Page" and page_info["page"] - 1 > 0:
            self.show_clients(message, page=page_info["page"] - 1)
            return
        elif message.text == "Back":
            self.add_client_handler(message)
            return
        else:
            self.show_clients(message, page=page_info["page"])
            return
        self.show_clients(message, page=page_info["page"])

    def edit_client(self, message, client_id):
        client = self.db_repo.get_client_by_id(client_id)
        current_message = "Client:\n"
        current_message += f"Name: {client.name}\n"
        current_message += f"Number: {client.number}\n"
        current_message += f"Note: {client.note}\n"
        current_message += f"<b>Please, choose what you want to do:</b>"

        self.bot.send_message(
            message.chat.id,
            current_message,
            parse_mode="HTML",
            reply_markup=self.markups.edit_client_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_edit_client, client_id
        )

    def process_edit_client(self, message, client_id):
        if not message.content_type == "text":
            self.add_client_handler(message)
            return

        if message.text == "Edit Name":
            self.edit_client_spec(message, {"id": client_id, "spec": "name"})
        elif message.text == "Edit Number":
            self.edit_client_spec(message, {"id": client_id, "spec": "num"})
        elif message.text == "Edit Note":
            self.edit_client_spec(message, {"id": client_id, "spec": "note"})
        elif message.text == "Back":
            self.add_client_handler(message)
        else:
            self.add_client_handler(message)

    def disable_client(self, message, client_id):
        self.bot.send_message(
            message.chat.id,
            "Are you sure that you want to disable this Client?\n"
            "It will be placed under 'inactive clients' section",
            reply_markup=self.markups.yes_no_markup(),
        )
        self.bot.register_next_step_handler(
            message, self.process_disabling_client, client_id
        )

    def process_disabling_client(self, message, client_id):
        if not message.content_type == "text":
            self.edit_client(message, client_id)
            return
        if message.text == "Yes":
            client = self.db_repo.get_client_by_id(client_id)
            client.is_active = False
            client.save()
            self.add_client_handler(message)
        else:
            self.edit_client(message, client_id)

    def edit_client_spec(self, message, client_spec):
        self.bot.send_message(
            message.chat.id, f"Please, send new Client {client_spec['spec']}"
        )
        self.bot.register_next_step_handler(
            message, self.process_editing_client_name, client_spec
        )

    def process_editing_client_name(self, message, client_spec):
        if not message.content_type == "text":
            self.edit_client(message, client_spec["id"])
            return
        client = self.db_repo.get_client_by_id(client_spec["id"])
        if client_spec["spec"] == "name":
            client.name = message.text
            client.save()
        elif client_spec["spec"] == "num":
            client.number = message.text
            client.save()
        elif client_spec["spec"] == "note":
            client.note = message.text
            client.save()

        self.edit_client(message, client_spec["id"])

    def get_client_name(self, message):
        self.bot.send_message(message.chat.id, "Please, send client name")
        self.bot.register_next_step_handler(message, self.process_getting_client_name)

    def process_getting_client_name(self, message):
        if not message.content_type == "text":
            self.add_client_handler(message)
            return
        current_client = {}
        current_client["name"] = message.text.strip().title()
        self.get_client_number(message, current_client)

    def get_client_number(self, message, current_client):
        self.bot.send_message(message.chat.id, "Please, send client number")
        self.bot.register_next_step_handler(
            message, self.process_getting_client_number, current_client
        )

    def process_getting_client_number(self, message, current_client):
        if not message.content_type == "text":
            self.add_client_handler(message)
            return
        current_client["number"] = message.text.strip()
        self.get_note_about_client(message, current_client)

    def get_note_about_client(self, message, current_client):
        self.bot.send_message(
            message.chat.id,
            "Please, write down a note about the client, \n"
            "<b>Only you and manager will see this note.</b>  \n\n"
            "It will help you to differentiate all the clients in the future.",
            parse_mode="HTML",
        )

        self.bot.register_next_step_handler(
            message, self.process_getting_client_note, current_client
        )

    def process_getting_client_note(self, message, current_client):
        if not message.content_type == "text":
            self.add_client_handler(message)
        else:
            current_client["note"] = message.text
            self.__add_client_to_database(message, current_client)
            self.add_client_handler(message)

    def __add_client_to_database(self, message, current_client):
        manager_username = message.from_user.username
        current_client["manager"] = manager_username
        self.db_repo.add_client_to_database(current_client)

        self.bot.send_message(message.chat.id, "Client has been added")
