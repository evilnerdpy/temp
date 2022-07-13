from telebot import types


class InlineMarkups:
    @staticmethod
    def add_object_cities_inline_markup(list_len):
        inline_markup = []
        fist_line = []
        second_line = []
        for item in range(list_len):
            if item > 4:
                second_line.append(
                    types.InlineKeyboardButton(
                        text=f"{item+1}", callback_data=f"choose_city_city_{item}"
                    )
                )
                continue
            fist_line.append(
                types.InlineKeyboardButton(
                    text=f"{item+1}", callback_data=f"choose_city_city_{item}"
                )
            )

        third_line = []
        fourth_line = []
        fourth_line.append(
            types.InlineKeyboardButton(
                text="Add City", callback_data=f"choose_city_city_add"
            )
        )
        third_line.append(
            types.InlineKeyboardButton(
                text="Prev", callback_data=f"choose_city_city_prev"
            )
        )
        third_line.append(
            types.InlineKeyboardButton(
                text="Next", callback_data=f"choose_city_city_next"
            )
        )
        inline_markup.append(fist_line)
        inline_markup.append(second_line)
        inline_markup.append(third_line)
        inline_markup.append(fourth_line)
        return types.InlineKeyboardMarkup(inline_markup)

    @staticmethod
    def find_object_cities_inline_markup(list_len):
        inline_markup = []
        fist_line = []
        second_line = []
        for item in range(list_len):
            if item > 4:
                second_line.append(
                    types.InlineKeyboardButton(
                        text=f"{item + 1}", callback_data=f"find_object_city_{item}"
                    )
                )
                continue
            fist_line.append(
                types.InlineKeyboardButton(
                    text=f"{item + 1}", callback_data=f"find_object_city_{item}"
                )
            )

        third_line = []
        third_line.append(
            types.InlineKeyboardButton(
                text="Prev", callback_data=f"find_object_city_prev"
            )
        )
        third_line.append(
            types.InlineKeyboardButton(
                text="Next", callback_data=f"find_object_city_next"
            )
        )
        inline_markup.append(fist_line)
        inline_markup.append(second_line)
        inline_markup.append(third_line)
        return types.InlineKeyboardMarkup(inline_markup)

    @staticmethod
    def show_all_objects_inline_markup(list_len):
        inline_markup = []
        fist_line = []
        second_line = []
        for item in range(list_len):
            if item > 4:
                second_line.append(
                    types.InlineKeyboardButton(
                        text=f"{item + 1}", callback_data=f"show_all_objects_{item}"
                    )
                )
                continue
            fist_line.append(
                types.InlineKeyboardButton(
                    text=f"{item + 1}", callback_data=f"show_all_objects_{item}"
                )
            )

        third_line = []
        third_line.append(
            types.InlineKeyboardButton(
                text="Prev", callback_data=f"show_all_objects_prev"
            )
        )
        third_line.append(
            types.InlineKeyboardButton(
                text="Next", callback_data=f"show_all_objects_next"
            )
        )
        inline_markup.append(fist_line)
        inline_markup.append(second_line)
        inline_markup.append(third_line)
        return types.InlineKeyboardMarkup(inline_markup)
