import csv
import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_marshmallow import Marshmallow


# https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/
class Base(DeclarativeBase):
    pass


# First create the db object using the SQLAlchemy constructor.
# Pass a subclass of either DeclarativeBase or DeclarativeBaseNoMeta to the constructor.
db = SQLAlchemy(model_class=Base)
# Create a global Flask-Marshmallow object
ma = Marshmallow()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # Generate your own SECRET_KEY using python secrets
        SECRET_KEY="l-tirPCf1S44mWAGoWqWlA",
        # configure the SQLite database, relative to the app instance folder
        SQLALCHEMY_DATABASE_URI="sqlite:///"
        + os.path.join(app.instance_path, "paralympics.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialise Flask with the SQLAlchemy database extension
    db.init_app(app)
    # Initialise Flask-Marshmallow
    ma.init_app(app)

    # Models are defined in the models module, so you must import them before calling create_all, otherwise SQLAlchemy
    # will not know about them.
    from paralympics.models import User, Region, Event

    # Create the tables in the database
    # create_all does not update tables if they are already in the database.
    with app.app_context():
        # Create the database and tables if they don't already exist
        db.create_all()
        # Add the data to the database if not already added
        add_data_from_csv()

        # Register the routes with the app in the context
        from paralympics import paralympics

    return app


def add_data_from_csv():
    """Adds data to the database if it does not already exist."""

    # If there are no regions in the database, then add them
    first_region = db.session.execute(db.select(Region)).first()
    if not first_region:
        print("Start adding region data to the database")
        noc_file = Path(__file__).parent.parent.joinpath("data", "noc_regions.csv")
        with open(noc_file, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                # row[0] is the first column, row[1] is the second column
                r = Region(NOC=row[0], region=row[1], notes=row[2])
                db.session.add(r)
            db.session.commit()

    # If there are no Events, then add them
    first_event = db.session.execute(db.select(Event)).first()
    if not first_event:
        print("Start adding event data to the database")
        event_file = Path(__file__).parent.parent.joinpath(
            "data", "paralympic_events.csv"
        )
        with open(event_file, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                # row[0] is the first column, row[1] is the second column etc
                e = Event(
                    type=row[0],
                    year=row[1],
                    country=row[2],
                    host=row[3],
                    NOC=row[4],
                    start=row[5],
                    end=row[6],
                    duration=row[7] or None,
                    disabilities_included=row[8],
                    countries=row[9] or None,
                    events=row[10] or None,
                    sports=row[11] or None,
                    participants_m=row[12] or None,
                    participants_f=row[13] or None,
                    participants=row[14] or None,
                    highlights=row[15],
                )
                db.session.add(e)
            db.session.commit()


# Import can be here instead (but not at the top of the file) to avoid circular import issues
from paralympics.models import Region, Event, User
