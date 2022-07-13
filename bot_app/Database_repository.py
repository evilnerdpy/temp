try:
    from bot_app.SQL_db_model import (
        City,
        Admin,
        Manager,
        PropertyObjects,
        SalePropertyAttributes,
        RentPropertyAttributes,
        LandLords,
        ObjectPhotos,
        Clients,
        ObjectShares,
        AgencyNumber,
    )
except ModuleNotFoundError:
    from SQL_db_model import (
        City,
        Admin,
        Manager,
        PropertyObjects,
        SalePropertyAttributes,
        RentPropertyAttributes,
        LandLords,
        ObjectPhotos,
        Clients,
        ObjectShares,
        AgencyNumber,
    )

import datetime
import math
import random


class DataBaseRepository:
    @staticmethod
    def get_user_status(username):
        if Admin.get_or_none(username=username) is not None:
            return "admin"
        elif Manager.get_or_none(username=username) is not None:
            return "manager"
        else:
            return "unknown"

    @staticmethod
    def get_all_cities_names():
        cities = City.select().order_by(City.city_name)
        return [city.city_name for city in cities]

    @staticmethod
    def get_city_name_by_index(index):
        cities = City.select().order_by(City.city_name)
        return [city.city_name for city in cities][index]

    @staticmethod
    def save_property_object(current_object):
        city = City.get(city_name=current_object["city"])
        manager = Manager.get(username=current_object["manager"])
        location = ",".join(map(str, current_object["location"]))
        return PropertyObjects.create(
            related_to_city=city,
            related_to_manager=manager,
            time_of_adding=datetime.datetime.now(),
            property_service_type=current_object["service type"],
            property_type=current_object["property"],
            address=current_object["address"],
            bathrooms=current_object["bathrooms"],
            bedrooms=current_object["bedrooms"],
            floor=current_object["floor"],
            beach=current_object["beach"],
            location_lat_long=location,
            is_active_object=True,
            elevator=True if current_object["elevator"] == "Yes" else False,
            patio=True if current_object["patio"] == "Yes" else False,
            pool=True if current_object["pool"] == "Yes" else False,
            solarium=True if current_object["solarium"] == "Yes" else False,
            parking=True if current_object["parking"] == "Yes" else False,
            central_gas_system=True
            if current_object["central gas system"] == "Yes"
            else False,
            solar_panels_for_water_heating=True
            if current_object["solar panels for water heating"] == "Yes"
            else False,
        )

    @staticmethod
    def save_sale_property_attributes(object_record, current_object):
        return SalePropertyAttributes.create(
            related_to_property_object=object_record, price=current_object["price"]
        )

    @staticmethod
    def save_rent_property_attributes(object_record, current_object):
        prices = {
            "per day": "Not Specified",
            "weekly": "Not Specified",
            "monthly": "Not Specified",
        }
        for price in prices.keys():
            try:
                prices[price] = current_object[price]
            except KeyError:
                pass
        pets_allowed = False
        if current_object["pets"].lower() == "Yes":
            pets_allowed = True
        elif current_object["pets"] == "No":
            pass

        return RentPropertyAttributes.create(
            related_to_property_object=object_record,
            per_day_cost=prices["per day"],
            per_week_cost=prices["weekly"],
            per_month_cost=prices["monthly"],
            pets=pets_allowed,
            availability_date=current_object["availability_date"],
        )

    @staticmethod
    def save_landlord(object_record, current_object):
        manager = Manager.get(username=current_object["manager"])

        landlord = current_object["related to landlord"]
        LandLords.create(
            related_to_manager=manager,
            related_to_property=object_record,
            time_of_adding=datetime.datetime.now(),
            name=landlord["name"],
            number=landlord["number"],
            status=landlord["status"],
        )
        if len(current_object["photos"]) > 0:
            for photo_id in current_object["photos"]:
                ObjectPhotos.create(
                    related_to_property_object=object_record, photo_id=photo_id
                )

    def save_current_object(self, current_object):
        object_record = self.save_property_object(current_object)

        if current_object["service type"] == "sale":
            self.save_sale_property_attributes(object_record, current_object)
        elif current_object["service type"] == "rent":
            self.save_rent_property_attributes(object_record, current_object)

        self.save_landlord(object_record, current_object)

        return object_record

    @staticmethod
    def get_city_by_name(name):
        return City.get_or_none(city_name=name)

    @staticmethod
    def get_manager_by_username(username):
        return Manager.get_or_none(username=username)

    @staticmethod
    def get_object_by_manager_and_city(manager, city):
        return PropertyObjects.select().where(
            PropertyObjects.related_to_manager == manager,
            PropertyObjects.related_to_city == city,
            PropertyObjects.is_active_object == True,
        )

    def get_objects_by_location(self, current_object):

        city = self.get_city_by_name(current_object["city"])
        manager = self.get_manager_by_username(current_object["manager"])

        objects = self.get_object_by_manager_and_city(manager, city)
        list_to_send = []
        origin_location = current_object["location"]
        for object in objects:
            object_location = list(
                map(
                    float,
                    object.location_lat_long[0 : len(object.location_lat_long)].split(
                        ","
                    ),
                )
            )
            if self.__check_if_in_radius(
                origin_location, object_location, current_object["radius in kilometers"]
            ):
                list_to_send.append(object)

        return list_to_send

    def get_all_manager_objects(self, current_object, **kwargs):
        if "admin" in kwargs:
            manager = current_object["manager_id"]
            city = current_object["city_id"]
        else:
            manager = self.get_manager_by_username(current_object["manager"])
            city = self.get_city_by_name(current_object["city"])
        return PropertyObjects.select().where(
            PropertyObjects.property_service_type == current_object["service type"],
            PropertyObjects.related_to_city == city,
            PropertyObjects.related_to_manager == manager,
        )

    def find_object_by_id(self, current_object):
        city = self.get_city_by_name(current_object["city"])
        manager = self.get_manager_by_username(current_object["manager"])

        cur_object = PropertyObjects.get_or_none(
            PropertyObjects.related_to_manager == manager,
            PropertyObjects.related_to_city == city,
            PropertyObjects.id == current_object["id"],
            PropertyObjects.is_active_object == True,
        )

        return cur_object

    def find_object_by_fake_id(self, current_object):
        city = self.get_city_by_name(current_object["city"])
        manager = self.get_manager_by_username(current_object["manager"])

        cur_object = PropertyObjects.get_or_none(
            PropertyObjects.related_to_manager == manager,
            PropertyObjects.related_to_city == city,
            PropertyObjects.fake_id == current_object["id"],
            PropertyObjects.is_active_object == True,
        )

        return cur_object

    @staticmethod
    def get_object_by_id_for_object_menu(object_id):
        return PropertyObjects.get_or_none(PropertyObjects.id == object_id)

    @staticmethod
    def get_object_photos(property_obj):
        return property_obj.photos

    @staticmethod
    def get_landlord_by_property(property_obj):
        landlord = LandLords.select().where(
            LandLords.related_to_property == property_obj
        )[0]
        return landlord.__data__

    @staticmethod
    def add_photo_to_object(property_object, photo_id):
        ObjectPhotos.create(
            related_to_property_object=property_object, photo_id=photo_id
        )

    @staticmethod
    def delete_all_object_photos(property_obj):
        photos = property_obj.photos
        [photo.delete_instance() for photo in photos]

    @staticmethod
    def check_if_object_have_photo_by_id(object_id, photo_id):
        property_object = PropertyObjects.get(id=object_id)
        if -1 < photo_id - 1 < len(property_object.photos):
            return True
        return False

    @staticmethod
    def delete_object_photo_by_id(object_id, photo_id):
        property_object = PropertyObjects.get(id=object_id)
        photo = property_object.photos[photo_id - 1]
        photo.delete_instance()

    @staticmethod
    def change_object_yes_no_spec(object_id, spec, value):
        property_object = PropertyObjects.get(PropertyObjects.id == object_id)
        if spec == "elevator":
            property_object.elevator = True if value == "Yes" else False
        elif spec == "solarium":
            property_object.solarium = True if value == "Yes" else False
        elif spec == "parking":
            property_object.parking = True if value == "Yes" else False
        elif spec == "central_gas_system":
            property_object.central_gas_system = True if value == "Yes" else False
        elif spec == "solar_panels_for_water_heating":
            property_object.solar_panels_for_water_heating = (
                True if value == "Yes" else False
            )
        elif spec == "pets":
            rent_attr = property_object.rent_attributes[0]
            rent_attr.pets = True if value == "Yes" else False
            rent_attr.save()

        elif spec == "pool":
            property_object.pool = True if value == "Yes" else False

        property_object.save()

        return True

    @staticmethod
    def change_object_numeric_spec(object_id, spec, value):

        property_object = PropertyObjects.get(PropertyObjects.id == object_id)
        if spec == "Change Bathrooms":
            property_object.bathrooms = value
        elif spec == "Change Bedrooms":
            property_object.bedrooms = value
        elif spec == "Change Floor":
            property_object.floor = value

        property_object.save()
        return True

    @staticmethod
    def change_object_string_spec(object_id, spec, value):
        property_object = PropertyObjects.get(PropertyObjects.id == object_id)

        if spec == "Change Address":
            property_object.address = value
            property_object.save()
        elif spec == "property type":
            property_object.property_type = value
        elif spec == "Change Price Per Day":
            rent_attr = property_object.rent_attributes[0]
            rent_attr.per_day_cost = value
            rent_attr.save()
        elif spec == "Change Price Per Week":
            rent_attr = property_object.rent_attributes[0]
            rent_attr.per_week_cost = value
            rent_attr.save()
        elif spec == "Change Price Per Month":
            rent_attr = property_object.rent_attributes[0]
            rent_attr.per_month_cost = value
            rent_attr.save()
        elif spec == "Change Price":
            sale_attr = property_object.sale_attributes[0]
            sale_attr.price = value
            sale_attr.save()
        elif spec == "Change Landlord Name":
            manager = Manager.get(Manager.id == property_object.related_to_manager)
            landlord = LandLords.get(
                LandLords.related_to_property == property_object,
                LandLords.related_to_manager == manager,
            )
            landlord.name = value
            landlord.save()
        elif spec == "beach":
            property_object.beach = value
            property_object.save()
        elif spec == "Change Landlord Number":
            manager = Manager.get(Manager.id == property_object.related_to_manager)
            landlord = LandLords.get(
                LandLords.related_to_property == property_object,
                LandLords.related_to_manager == manager,
            )
            landlord.number = value
            landlord.save()
        elif spec == "landlord status":
            manager = Manager.get(Manager.id == property_object.related_to_manager)
            landlord = LandLords.get(
                LandLords.related_to_property == property_object,
                LandLords.related_to_manager == manager,
            )
            landlord.status = value
            landlord.save()
        elif spec == "location":
            property_object.location_lat_long = value
            property_object.save()

        return property_object

    @staticmethod
    def change_object_availability_date(object_id, value):
        property_object = PropertyObjects.get(PropertyObjects.id == object_id)
        rent_attr = property_object.rent_attributes[0]
        rent_attr.availability_date = value
        rent_attr.save()

    def add_client_to_database(self, current_client):
        manager = self.get_manager_by_username(current_client["manager"])
        Clients.create(
            name=current_client["name"],
            number=current_client["number"],
            note=current_client["note"],
            related_to_manager=manager,
        )

    def get_manager_clients_name_by_manager_username(self, manager_username):
        manager = self.get_manager_by_username(manager_username)
        return [client.name for client in manager.clients]

    def check_if_client_name_is_under_manager(self, client_name, manager_username):
        manager = self.get_manager_by_username(manager_username)
        return (
            True
            if Clients.get_or_none(
                Clients.name == client_name, Clients.related_to_manager == manager
            )
            is not None
            else False
        )

    def get_client_by_name_and_manager(self, client_name, manager):
        return Clients.get_or_none(
            Clients.name == client_name, Clients.related_to_manager == manager
        )

    @staticmethod
    def get_client_by_id(client_id):
        return Clients.get_or_none(Clients.id == client_id)

    def create_share_object_record(self, client_id, manager_username, object_id):
        manager = self.get_manager_by_username(manager_username)
        client = self.get_client_by_id(client_id)
        property_object = self.get_object_by_id_for_object_menu(object_id)

        ObjectShares.create(
            related_to_manager=manager,
            related_to_property=property_object,
            related_to_client=client,
        )
        return property_object

    @staticmethod
    def add_city(city_name):
        City.create(city_name=city_name, time_of_adding=datetime.datetime.now())

    def get_all_clients_by_manager_username(self, manager_username):
        manager = self.get_manager_by_username(manager_username)
        return Clients.select().where(
            Clients.related_to_manager == manager, Clients.is_active == True
        )

    @staticmethod
    def get_all_active_managers_admin():
        return Manager.select().where(Manager.is_active == True)

    @staticmethod
    def get_all_banned_managers_admin():
        return Manager.select().where(Manager.is_active == False)

    @staticmethod
    def get_manager_by_id(manager_id):
        return Manager.get(id=manager_id)

    @staticmethod
    def add_new_manager(new_manager):
        Manager.create(
            name=new_manager["name"],
            username=new_manager["username"],
            number=new_manager["number"],
        )

    def add_admin_and_manager(self, new_admin):
        self.add_new_manager(new_admin)
        Admin.get_or_create(username=new_admin["username"])

    @staticmethod
    def admin_get_object_by_fake_id(fake_id):
        return PropertyObjects.get_or_none(fake_id=fake_id)

    @staticmethod
    def get_agency_number():
        return AgencyNumber.get(id=1)

    @staticmethod
    def get_all_cities():
        return City.select()

    # TEST
    @staticmethod
    def get_all_objects():
        return PropertyObjects.select().where(PropertyObjects.is_active_object == True)

    @staticmethod
    def get_all_clients():
        return Clients.select().where(Clients.is_active == True)

    @staticmethod
    def get_all_manager_objects_excluding_city(manager_id):
        return ObjectShares.select().where(
            ObjectShares.related_to_manager == manager_id
        )

    @staticmethod
    def __check_if_in_radius(origin_location, location_to_check, radius_km):
        lat = origin_location[0]
        long = origin_location[1]
        meters = radius_km * 1000
        earth_radius_in_km = 6378.137

        coeff = (1 / ((2 * math.pi / 360) * earth_radius_in_km)) / 1000

        blur_factor = meters * coeff

        biggest_lat = lat + blur_factor
        smallest_lat = lat - blur_factor
        biggest_long = long + blur_factor / math.cos(lat * 0.018)
        smallest_long = long - blur_factor / math.cos(lat * 0.018)

        if (
            smallest_lat < location_to_check[0] < biggest_lat
            and smallest_long < location_to_check[1] < biggest_long
        ):
            return True
        return False
