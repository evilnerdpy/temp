from telegraph import Telegraph
import requests
import os


TOKEN = "6692c1732a16f16148e46bf5655751abb948ecbf151f84b07ecd8e3e1708"
language = {
    "eng": {
        "yes": "Yes",
        "no": "No",
        "address": "Address",
        "city": "City",
        "property type": "Property Type",
        "bungalow": "Bungalow",
        "apartments": "Apartments",
        "villa": "Villa",
        "service type": "Service Type",
        "rent": "Rent",
        "sale": "Buy",
        "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms",
        "floor": "Floor",
        "elevator": "Elevator",
        "patio": "Patio",
        "solarium": "Solarium",
        "parking": "Parking",
        "gas": "Central Gas System",
        "panels": "Solar Panels For Water Heating",
        "pool": "Pool",
        "beach": "Beach",
        "5 min": "5 Minutes By Walk",
        "10 min": "10 Minutes By Walk",
        "15 min": "15 Minutes By Walk",
        "No beach nearby": "No Beach Nearby",
        "location": "Location",
        "price": "Price",
        "per day cost": "Price Per Day",
        "per week cost": "Price Per Week",
        "per month cost": "Price Per Month",
        "not specified": "Not Specified",
        "pets": "Pets",
        "available from": "Available From",
        "call to": "Call To",
    },
    "esp": {
        "yes": "Sí",
        "no": "No",
        "address": "Dirección",
        "city": "Ciudad",
        "property type": "Tipo de propiedad",
        "bungalow": "Bungalow",
        "apartments": "Apartamentos",
        "villa": "Villa",
        "service type": "Tipo de Servicio",
        "rent": "Renta",
        "sale": "Comprar",
        "bedrooms": "Dormitorios",
        "bathrooms": "Baños",
        "floor": "Piso",
        "elevator": "Ascensor",
        "patio": "Patio",
        "solarium": "Solárium",
        "parking": "Estacionamiento",
        "gas": "Sistema Central de Gas",
        "panels": "Paneles Solares para Calentamiento de Agua",
        "pool": "Piscina",
        "beach": "Playa",
        "5 min": "5 minutos",
        "10 min": "10 minutos",
        "15 min": "15 minutos",
        "No beach nearby": "Sin playa cerca",
        "location": "Ubicación",
        "price": "Precio",
        "per day cost": "Precio por día",
        "per week cost": "Precio por semana",
        "per month cost": "Precio por Mes",
        "not specified": "No especificado",
        "pets": "Mascotas",
        "available from": "Disponible desde",
        "call to": "llamar al número",
    },
    "pol": {
        "yes": "Tak",
        "no": "Nie",
        "address": "Adres zamieszkania",
        "city": "Miasto",
        "property type": "Rodzaj własności",
        "bungalow": "Dom parterowy",
        "apartments": "Mieszkanie",
        "villa": "Willa",
        "service type": "Typ usługi",
        "rent": "Wynajem",
        "sale": "Kupić",
        "bedrooms": "Sypialnie",
        "bathrooms": "Łazienki",
        "floor": "Mieszkanie",
        "elevator": "Winda",
        "patio": "Patio",
        "solarium": "Solárium",
        "parking": "Parking",
        "gas": "Сentralny gaz",
        "panels": "Panele słoneczne do podgrzewania wody",
        "pool": "Basen",
        "beach": "Plaża",
        "5 min": "5 minut",
        "10 min": "10 minut",
        "15 min": "15 minut",
        "No beach nearby": "Brak plaży w pobliżu",
        "location": "Lokalizacja",
        "price": "Precio",
        "per day cost": "Cena za dzień",
        "per week cost": "Cena za tydzień",
        "per month cost": "Cena za miesiąc",
        "not specified": "Nieokreślony",
        "pets": "Zwierzęta",
        "available from": "Dostępne od",
        "call to": "Dzwonić do",
    },
    "nor": {
        "yes": "Ja",
        "no": "Ikke",
        "address": "Adresse",
        "city": "By",
        "property type": "Type eierskap",
        "bungalow": "Bungalow",
        "apartments": "Leilighet",
        "villa": "Villa",
        "service type": "Tjenestetype",
        "rent": "Leie",
        "sale": "Å kjøpe",
        "bedrooms": "Soverommene",
        "bathrooms": "bad",
        "floor": "Leilighet",
        "elevator": "Heis",
        "patio": "Patio",
        "solarium": "Solárium",
        "parking": "Parkering",
        "gas": "Sentral gass",
        "panels": "Solcellepaneler for oppvarming av vann",
        "pool": "Basseng",
        "beach": "Strand",
        "5 min": "5 minutter",
        "10 min": "10 minutter",
        "15 min": "15 minutter",
        "No beach nearby": "Ingen strand i nærheten",
        "location": "Plassering",
        "price": "Pris",
        "per day cost": "Pris for dagen",
        "per week cost": "Pris for en uke",
        "per month cost": "Pris per måned",
        "not specified": "Ubestemt",
        "pets": "Dyr",
        "available from": "Tilgjengelig fra",
        "call to": "ring til",
    },
    "swed": {
        "yes": "Ja",
        "no": "Nej",
        "address": "Adress",
        "city": "Stad",
        "property type": "Egenskapstyp",
        "bungalow": "Bungalow",
        "apartments": "Lägenhet",
        "villa": "Villa",
        "service type": "Typ av tjänst",
        "rent": "Hyra",
        "sale": "Att köpa",
        "bedrooms": "Sovrummen",
        "bathrooms": "badrum",
        "floor": "Golv",
        "elevator": "Hiss",
        "patio": "Patio",
        "solarium": "Solárium",
        "parking": "Parkering",
        "gas": "Central gas",
        "panels": "Solpaneler för uppvärmning av vatten",
        "pool": "Slå samman",
        "beach": "Strand",
        "5 min": "5 minuter",
        "10 min": "10 minuter",
        "15 min": "15 minuter",
        "No beach nearby": "Ingen strand i närheten",
        "location": "Plats",
        "price": "Pris",
        "per day cost": "Pris för dagen",
        "per week cost": "Pris för en vecka",
        "per month cost": "Pris per månad",
        "not specified": "Obestämd",
        "pets": "Djur",
        "available from": "Tillgänglig från",
        "call to": "ring til",
    },
    "french": {
        "yes": "Oui",
        "no": "Non",
        "address": "Adresse",
        "city": "Ville",
        "property type": "Type de propriété",
        "bungalow": "Bungalow",
        "apartments": "Appartement",
        "villa": "Villa",
        "service type": "Type de service",
        "rent": "location",
        "sale": "Acheter",
        "bedrooms": "Les chambres à coucher",
        "bathrooms": "Salles de bains",
        "floor": "Sol",
        "elevator": "Ascenseur",
        "patio": "Patio",
        "solarium": "Solárium",
        "parking": "Parking",
        "gas": "Centrale gaz",
        "panels": "Panneaux solaires pour chauffer l'eau",
        "pool": "Plage",
        "beach": "Strand",
        "5 min": "5 minutes",
        "10 min": "10 minutes",
        "15 min": "15 minutes",
        "No beach nearby": "Pas de plage à proximité ",
        "location": "Emplacement",
        "price": "Prix",
        "per day cost": "Tarif à la journée",
        "per week cost": "Prix pour une semaine",
        "per month cost": "Prix par mois",
        "not specified": "Indéfini",
        "pets": "Animaux",
        "available from": "Disponible à partir de",
        "call to": "appeler pour",
    },
    "ger": {
        "yes": "Ja",
        "no": "Nicht",
        "address": "Anschrift",
        "city": "Stadt",
        "property type": "Art der Immobilie",
        "bungalow": "Bungalow",
        "apartments": "Wohnung",
        "villa": "Villa",
        "service type": "Diensttyp",
        "rent": "Mieten",
        "sale": "Kaufen",
        "bedrooms": "Schlafzimmer",
        "bathrooms": "Badezimmer",
        "floor": "Boden",
        "elevator": "Aufzug",
        "patio": "Patio",
        "solarium": "Solárium",
        "parking": "Parkplatz",
        "gas": "Gaswerk",
        "panels": "Sonnenkollektoren zum Erhitzen von Wasser",
        "pool": "Schwimmbad",
        "beach": "Strand",
        "5 min": "5 Minuten",
        "10 min": "10 Minuten",
        "15 min": "15 Minuten",
        "No beach nearby": "Kein Strand in der Nähe",
        "location": "Standort",
        "price": "Preis",
        "per day cost": "Preis pro Tag",
        "per week cost": "Preis für eine Woche",
        "per month cost": "Preis pro Monat",
        "not specified": "Unbestimmt",
        "pets": "Tiere",
        "available from": "Verfügbar ab",
        "call to": "Aufruf",
    },
    "rus": {
        "yes": "Да",
        "no": "Нет",
        "address": "Адрес",
        "city": "Город",
        "property type": "Тип недвижимости",
        "bungalow": "Бунгало",
        "apartments": "Квартира",
        "villa": "Вилла",
        "service type": "Тип услуги",
        "rent": "Аренда",
        "sale": "Продажа",
        "bedrooms": "Спальни",
        "bathrooms": "Ванных комнат",
        "floor": "Этаж",
        "elevator": "Лифт",
        "patio": "Патио",
        "solarium": "Солариум",
        "parking": "Парковка",
        "gas": "Центральный газ",
        "panels": "Солнечные панели для нагрева воды",
        "pool": "Бассейн",
        "beach": "Пляж",
        "5 min": "В 5 минутах ходьбы",
        "10 min": "В 10 минутах ходьбы",
        "15 min": "В 15 минутах ходьбы",
        "No beach nearby": "Нет пляжа по близости",
        "location": "Локация",
        "price": "Цена",
        "per day cost": "Цена за день",
        "per week cost": "Цена за неделю",
        "per month cost": "Цена за месяц",
        "not specified": "Не указана",
        "pets": "Животные",
        "available from": "Доступно с",
        "call to": "Звоните на номер",
    },
}


class TelegraphUploader:
    def __init__(self, bot, token):
        self.telegraph_builder = Telegraph(TOKEN)
        self.bot = bot
        self.token = token

    def upload_property_object(self, prop_object, lang, agency_number):

        content = f"""
                    <b>ID: {prop_object.fake_id}</b> <br>
                    <b>{language[lang]["service type"]}: {
                        language[lang][prop_object.property_service_type.lower()]
                    }</b> <br>

                    <b>{language[lang]["property type"]}: {
                    language[lang][prop_object.property_type]
                    }</b> <br>

                    <b>{language[lang]["city"]}: {prop_object.related_to_city.city_name}</b> <br>

                    <b>{language[lang]["address"]}: {prop_object.address}</b> <br>

                    <b>{language[lang]["bedrooms"]}: {prop_object.bedrooms}</b> <br>

                    <b>{language[lang]["bathrooms"]}: {prop_object.bathrooms}</b> <br>

                    <b>{language[lang]["floor"]}: {prop_object.floor}</b> <br>"""

        content += (
            f""" <b>{language[lang]["elevator"]}: {
                        language[lang]["yes"] if prop_object.elevator == True else language[lang]["no"]
                    }</b> <br>"""
            if prop_object.elevator is True
            else ""
        )

        content += (
            f"""  <b>{language[lang]["pool"]}: {
                        language[lang]["yes"]
                    }</b> <br>"""
            if prop_object.pool is True
            else ""
        )

        content += (
            f"""<b>{language[lang]["patio"]}: {
                        language[lang]["yes"]
                    }</b> <br>"""
            if prop_object.patio is True
            else ""
        )

        content += (
            f"""<b>{language[lang]["solarium"]}: {
                        language[lang]["yes"]
                    }</b> <br> """
            if prop_object.solarium is True
            else ""
        )

        content += (
            f"""<b>{language[lang]["parking"]}: {
                        language[lang]["yes"] 
                    }</b> <br>"""
            if prop_object.parking is True
            else ""
        )

        content += (
            f"""<b>{language[lang]["gas"]}: {
                        language[lang]["yes"]
                    }</b> <br>"""
            if prop_object.central_gas_system is True
            else ""
        )

        content += (
            f"""<b>{language[lang]["panels"]}: {
                        language[lang]["yes"]}
                        </b> <br>"""
            if prop_object.solar_panels_for_water_heating is True
            else ""
        )

        content += f"""<b>{language[lang]["beach"]}: {language[lang][prop_object.beach]}</b> <br>
                    """

        if prop_object.property_service_type == "rent":
            rent_attributes = prop_object.rent_attributes[0]

            content += f"""
                        <b>{language[lang]["available from"]}</b>:
                        {rent_attributes.availability_date.strftime("%m/%d/%Y")}<br>
                        """

            content += (
                f"""<b>{language[lang]["pets"]}:{language[lang]["yes"] 
            }</b><br>"""
                if rent_attributes.pets is True
                else ""
            )

            content += f"""<b>{language[lang]["per day cost"]}: {
            language[lang]["not specified"] if rent_attributes.per_day_cost == "Not Specified" else 
            " €" + rent_attributes.per_day_cost + "💶"
            }</b> <br>"""

            content += f"""<b>{language[lang]["per week cost"]}:{
            language[lang]["not specified"] if rent_attributes.per_week_cost == "Not Specified" else
            " €" + rent_attributes.per_week_cost + "💶"
            }</b> <br>"""

            content += f"""<b>{language[lang]["per month cost"]}: 
            {language[lang]["not specified"] if rent_attributes.per_month_cost == "Not Specified" else
            " €" + rent_attributes.per_month_cost + "💶"
            }</b> <br>"""
        elif prop_object.property_service_type == "sale":
            sale_attributes = prop_object.sale_attributes[0]
            content += (
                f'<b>{language[lang]["price"]}: €{sale_attributes.price}💶</b> <br>'
            )

        lat, long = prop_object.location_lat_long.split(",")

        content += (
            f'<a href = "http://www.google.com/maps/place/{lat},{long}" > {language[lang]["location"]} </a>'
            f"<br><br>"
        )

        manager = prop_object.related_to_manager
        if manager.allowed_to_use_personal_number:
            content += f'{language[lang]["call to"]}:{manager.number}<br><br>'
        else:
            content += f'{language[lang]["call to"]}:{agency_number.number}<br><br>'

        photo_ids = [photo.photo_id for photo in prop_object.photos]
        photo_paths = [self.bot.get_file(photo).file_path for photo in photo_ids]
        downloaded_photos = [self.bot.download_file(photo) for photo in photo_paths]
        cwd = os.getcwd()
        uploaded_jsons = []
        for index, photo in enumerate(downloaded_photos):
            ext = photo_paths[index].split(".")[-1]
            name = prop_object.related_to_manager.username + str(index) + "." + ext
            path = os.path.join(cwd, "temp", name)
            with open(str(path), "wb") as new_photo:
                new_photo.write(photo)
            json = self.__upload_image_telegraph(path)
            os.remove(path)
            uploaded_jsons.append(json)

        for json in uploaded_jsons:
            content += "<br> <img src='{}'/>".format(json)

        article = self.telegraph_builder.create_page(
            f"Alex Real Estate {prop_object.fake_id}", html_content=content
        )
        return article["url"]

    @staticmethod
    def __upload_image_telegraph(path_image):
        with open(path_image, "rb") as f:
            proxies = {"http": "proxy.server:3128"}
            result_requests = requests.post(
                "https://telegra.ph/upload",
                files={"file": ("file", f, "image/jpg")},
                proxies=proxies,
            ).json()[0]["src"]
            return result_requests
