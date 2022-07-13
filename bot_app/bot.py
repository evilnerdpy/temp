import telebot

from markups import Markups
from add_object_handlers import AddObjectHandlers
from find_object import FindObject
from object_menu_handlers import ObjectMenuHandlers
from Database_repository import DataBaseRepository
from add_client_handlers import AddClientHandlers
from inline_markups import InlineMarkups
from telegraph_uploader import TelegraphUploader
from admin import Admin


TOKEN = "5323509649:AAH8yeXP-7DrV01-7B-Hnr9jlj0cgnLNBGQ"


bot = telebot.TeleBot(TOKEN)


print("bot is online")
markups = Markups()
db_repo = DataBaseRepository()
telegraph_uploader = TelegraphUploader(bot, TOKEN)
inline_markups = InlineMarkups()


@bot.message_handler(commands=["start", "help"])
def command_start(message):
    if db_repo.get_user_status(message.from_user.username) in ["admin", "manager"]:
        bot.send_message(
            message.chat.id,
            f"Hello, {message.from_user.username}!",
            reply_markup=markups.get_command_start_markup(
                db_repo.get_user_status(message.from_user.username)
            ),
            parse_mode="HTML",
        )


@bot.message_handler(regexp="Add Object")
def add_object(message):
    if db_repo.get_user_status(message.from_user.username) in ["admin", "manager"]:
        add_object_handlers.get_service_type(message)


@bot.message_handler(regexp="Find Object")
def find_object(message):
    if db_repo.get_user_status(message.from_user.username) in ["admin", "manager"]:
        find_object_handlers.get_service_type(message)


@bot.message_handler(regexp="Add Client")
def add_client(message):
    if db_repo.get_user_status(message.from_user.username) in ["admin", "manager"]:
        add_client_handlers.add_client_handler(message)


@bot.message_handler(regexp="ADMIN PANEL")
def admin(message):
    if db_repo.get_user_status(message.from_user.username) == "admin":
        admin_panel.admin_panel(message)


@bot.callback_query_handler(func=lambda x: True)
def callback_handler(call):
    if "choose_city_" in call.data:
        add_object_handlers.get_city_callback_handler(call)
    elif "find_object_city_" in call.data:
        find_object_handlers.get_city_callback_handler(call)
    elif "show_all_objects_" in call.data:
        find_object_handlers.show_all_objects_callback_handler(call)


# INIT MENUS


admin_panel = Admin(bot, markups, inline_markups, db_repo, command_start)


add_object_handlers = AddObjectHandlers(
    bot, markups, inline_markups, db_repo, command_start
)

find_object_handlers = FindObject(bot, markups, inline_markups, db_repo, command_start)

object_menu_handlers = ObjectMenuHandlers(
    bot, markups, inline_markups, db_repo, telegraph_uploader, command_start
)

property_object_menu_handler = object_menu_handlers.get_property_object_menu_handlers()

find_object_handlers.set_property_object_menu_handler(property_object_menu_handler)

add_client_handlers = AddClientHandlers(
    bot, markups, inline_markups, db_repo, command_start
)

bot.polling(none_stop=True, interval=0)

#
# def run():
#     try:
#         bot.polling(none_stop=True, interval=0)
#     except Exception as e:
#         bot.send_message(249599924, str(e))
#
#
# if __name__ == "__main__":
#     while True:
#         run()
