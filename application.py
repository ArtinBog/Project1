import os
import requests, json

from flask import Flask, session, request, render_template
from flask import render_template #renders Jinja2 template engine
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

weather = requests.get("https://api.darksky.net/forecast/048b7e9f41c99b0e06b1c0181d74ad7b/42.37,-71.11").json()
print(json.dumps(weather["currently"], indent = 2))

# Check for for environment viriable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/locations", methods=["GET","POST"])
def locations():

    """Lists all locations."""
    # Get all of the locations in the database, send them to our index.html template.
    locations = db.execute("SELECT * FROM locations").fetchall()
    print(locations)
    return render_template("locations.html", locations=locations)

@app.route("/location", methods=["POST"])
def location():

    """More Info."""

    # Get form information.
    name = request.form.get("name") #Alex

    # Make sure that the zipcode is a number (in case of a weird error).
    try:
        zipcode = int(request.form.get("locations"))
    except ValueError:
        return render_template("error.html", message="Invalid ZIP code.")

    # Make sure zipcode exists.
    if db.execute("SELECT * FROM locations WHERE id = :id", {"id": location_id}).rowcount == 0:
        return render_template("error.html", message="No such location.")

    # All done booking!
    db.commit()
    return render_template("/locations.html")

@app.route('/locations/<int:zipcode>')
def locations(zipcode):

    """Lists details about a certain zipcode."""
    # Make sure the ZIP code exist in our database.
    location = db.execute("SELECT * FROM locations WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()
    if location is None:
        return render_template("error.html", message="No such location.")

    # Get all users on checked in that location, send them to our location.html template.
    users = db.execute("SELECT name FROM users WHERE location_id = :location_id",
                            {"zipcode": zipcode}).fetchall()
    return render_template("/zipcode.html", zipcode=zipcode, users=users)

if __name__ == '__main__':
    app.run(debug=True)
