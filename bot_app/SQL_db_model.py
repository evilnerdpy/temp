from peewee import *
import datetime

db = PostgresqlDatabase(
    "real_estate",
    user="dev",
    password="markdev",
    port=5432,
    host="localhost",
)


class DatabaseModel(Model):
    class Meta:
        database = db


class City(DatabaseModel):
    city_name = CharField()
    date_of_adding = DateTimeField(default=datetime.datetime.now())


class Admin(DatabaseModel):
    username = CharField()


class Manager(DatabaseModel):
    username = CharField()
    name = CharField()
    number = CharField()
    allowed_to_use_personal_number = BooleanField(default=False)
    date_of_adding = DateTimeField(default=datetime.datetime.now())
    is_active = BooleanField(default=True)


class PropertyObjects(DatabaseModel):
    related_to_city = ForeignKeyField(City, backref="objects", on_delete="CASCADE")
    related_to_manager = ForeignKeyField(
        Manager, backref="objects", on_delete="CASCADE"
    )
    time_of_adding = DateTimeField(default=datetime.datetime.now())
    property_service_type = CharField()
    address = CharField()
    property_type = CharField()
    bathrooms = IntegerField()
    bedrooms = IntegerField()
    floor = IntegerField()
    elevator = BooleanField()
    patio = BooleanField()
    solarium = BooleanField()
    parking = BooleanField()
    pool = BooleanField()
    fake_id = CharField(null=True)
    central_gas_system = BooleanField()
    solar_panels_for_water_heating = BooleanField()
    beach = CharField()
    location_lat_long = CharField()
    is_active_object = BooleanField(default=False)


class RentPropertyAttributes(DatabaseModel):
    related_to_property_object = ForeignKeyField(
        PropertyObjects, backref="rent_attributes", on_delete="CASCADE"
    )
    per_day_cost = CharField(default="Not Specified")
    per_week_cost = CharField(default="Not Specified")
    per_month_cost = CharField(default="Not Specified")
    pets = BooleanField(default=False)
    availability_date = DateTimeField(default=datetime.datetime.now())


class SalePropertyAttributes(DatabaseModel):
    related_to_property_object = ForeignKeyField(
        PropertyObjects, backref="sale_attributes", on_delete="CASCADE"
    )
    price = CharField()


class LandLords(DatabaseModel):
    related_to_manager = ForeignKeyField(
        Manager, backref="clients", on_delete="CASCADE"
    )
    related_to_property = ForeignKeyField(
        PropertyObjects, backref="property", on_delete="CASCADE"
    )
    time_of_adding = DateTimeField(default=datetime.datetime.now())
    name = CharField()
    number = CharField()
    status = CharField()


class ObjectPhotos(DatabaseModel):
    related_to_property_object = ForeignKeyField(
        PropertyObjects, backref="photos", on_delete="CASCADE"
    )
    photo_id = CharField()


class Clients(DatabaseModel):
    related_to_manager = ForeignKeyField(
        Manager, backref="clients", on_delete="CASCADE"
    )
    time_of_adding = DateTimeField(default=datetime.datetime.now())
    name = CharField()
    number = CharField()
    note = CharField()
    is_active = BooleanField(default=True)


class ObjectShares(DatabaseModel):
    related_to_client = ForeignKeyField(Clients, backref="client", on_delete="CASCADE")
    related_to_property = ForeignKeyField(
        PropertyObjects, backref="property", on_delete="CASCADE"
    )
    related_to_manager = ForeignKeyField(
        Manager, backref="manager", on_delete="CASCADE"
    )
    time_of_adding = DateTimeField(default=datetime.datetime.now())


class AgencyNumber(DatabaseModel):
    number = CharField()


if __name__ == "__main__":

    db.create_tables(
        [
            City,
            Admin,
            Manager,
            PropertyObjects,
            RentPropertyAttributes,
            SalePropertyAttributes,
            LandLords,
            ObjectPhotos,
            Clients,
            ObjectShares,
            AgencyNumber,
        ]
    )

    # Manager.create(username="Innocentius", number="+998900431958", name="Mark")
    # Admin.create(username="Innocentius")
