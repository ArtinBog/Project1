import os
import requests, json

from flask import Flask, session, request, render_template, redirect, g, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
    if not session.get("logged_in"):
        return render_template('login.html')

    return render_template("index.html")

@app.before_request
def before_request():
    g.user = None
    if session.get("username"):
        g.user = db.execute("SELECT * FROM users WHERE username = :username", {"username": session["username"]}).fetchone()
        session["user_id"] = g.user.id
        db.commit()
        print(session["user_id"])
        # user_id = session["user_id"]

@app.route("/locations")
def locations():
    if not session.get('logged_in'):
        return render_template('login.html')

    locations = db.execute("SELECT * FROM locations").fetchall()
    db.commit()
    return render_template("locations.html", my_string="Love ya'll", numbers=[1, 2, 3, 4, 10, 8], locations=locations)

@app.route("/error")
def error():
    # if not session.get('logged_in'):
    #     return render_template('login.html')

    return render_template("error.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if not session.get('logged_in'):
        return render_template('login.html')

    if g.user:
        # Get form information.
        search_entry = request.form["search_entry"] #Some zip info

        # Make sure that the zip id is a number (in case of a weird error).
        try:
            zipcode_entry = int(search_entry)
            location = db.execute("SELECT * FROM locations WHERE CAST(zipcode as varchar(20)) LIKE '%"+str(zipcode_entry)+"%'").fetchall()

        except ValueError:
            city_entry = search_entry
            location = db.execute("SELECT * FROM locations WHERE LOWER(city) LIKE LOWER('%"+city_entry+"%')").fetchall()

            db.commit()

        if len(location) < 1:
            return(render_template("search.html", message="There's no result for your query " + search_entry))


        print(search_entry)
        # if zipcode is None:
        #     return render_template("error.html", message="No such zipcode.")

        return render_template("search.html", search_entry=search_entry, search=location)

    return render_template("error.html", message="you can't access this page because your are not logged in")

# This is the main function which pushes things to location.html
# location, weather_data, zipcode, ischecked, check_in, comment_entry
# In order to communicate with HTML I must push things to location
# Location can communicate to comment() and check_in() only through HTML
@app.route("/location/<int:zipcode>", methods=["GET", "POST"])
def location(zipcode): #this function communicates with the HTML

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    location = db.execute("SELECT * FROM locations WHERE zipcode = :zipcode", {"zipcode": zipcode}).fetchone()
    loc = str(location.lat) + "," + str(location.long)
    weather = requests.get("https://api.darksky.net/forecast/048b7e9f41c99b0e06b1c0181d74ad7b/" + loc).json()
    weather_data = json.dumps(weather["currently"], indent = 2)

    user_id = session.get('user_id')

    comment_entry = db.execute("SELECT * FROM comments").fetchall()
    comment_in_location = db.execute("SELECT * FROM comments WHERE location_id = :location_id", {"location_id": location.id}).fetchall()

    check_in = db.execute("SELECT count(*) FROM check_in WHERE location_id = :location_id and user_id = :user_id",
    {"location_id":location.id, "user_id":session.get("user_id")}).scalar()

    if check_in > 0:
        ischecked = True
    else:
        ischecked = False

    db.commit()
    return render_template('location.html', location=location, weather_data=weather_data, zipcode_entry=zipcode, ischecked=ischecked,
    check_in=check_in, comment_in_location = comment_in_location)

# This sub function which serves location()
# It just stores data requested from HTML to SQL
# This function doesn't communicate anything to HTML just to location()
# Input / parameters are coming from HTML (locatino.html)
@app.route('/check_in/<int:location_id>/<int:zipcode>', methods=["GET"])
def check_in(location_id, zipcode):

    user_id = session.get('user_id') #I could use session['user_id'], but using function instead of list id is more secured.

    db.execute("INSERT INTO check_in (user_id, location_id) VALUES (:user_id, :location_id)", {"user_id": user_id, "location_id": location_id})
    db.commit()

    return redirect(url_for('location', zipcode=zipcode)) #indicator that this is subfunction

# This sub function returns to location function, but doens't communicate to it.
# It just stores data requested from HTML to SQL
# This function doesn't communicate anything to HTML just to location()
# Input / parameters are coming from HTML (locatino.html)

@app.route('/comment/<int:location_id>/<int:zipcode>', methods=["GET", "POST"]) #POST used for input forms #GET for hyporlinks / no forms.
def comment(location_id, zipcode):

    comment_entry = request.form['comment_entry']
    user_id = session.get('user_id')


    db.execute("INSERT INTO comments (location_id, user_id, comment) VALUES (:location_id, :user_id, :comment)",
    {"location_id": location_id, "user_id": user_id, "comment": comment_entry})

    db.commit()

    return redirect(url_for('location', zipcode=zipcode)) #indicator that this is subfunction

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        session.pop("user", None)

        # this variables will provided from signup.html
        name = request.form["name"]
        emailaddress = request.form["emailaddress"]

        username = request.form["username"]
        password = request.form["password"]

        if db.execute("SELECT * FROM users WHERE emailaddress = :emailaddress", {"emailaddress": emailaddress}).rowcount > 0:
            return render_template("error.html", message="Your email address is already attached to another account")

        db.execute("INSERT INTO users (name, emailaddress, username, password) VALUES (:name, :emailaddress, :username, :password)",
                {"name": name, "emailaddress": emailaddress, "username": username, "password": password})

        db.commit()
        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        session.pop("user", None)

        username = str(request.form["username"])
        password = str(request.form["password"])

        users = db.execute("SELECT * FROM users").fetchall()

        if db.execute("SELECT username, password FROM users WHERE username = :username and password = :password", {"username": username, "password": password}).rowcount > 0:
            session.clear()
            session["logged_in"] = True
            session["username"] = username

            db.commit()
            return redirect(url_for("index"))

    return render_template("login.html")
        # return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return render_template("index.html")

@app.route('/api/<int:zipcode>', methods=["GET"])
def api(zipcode):

    location = db.execute("SELECT * FROM locations WHERE zipcode =:zipcode", {"zipcode": zipcode}).fetchone()
    check_ins = db.execute("SELECT count(*) FROM check_in WHERE location_id = :location_id", {"location_id": location.id}).scalar()
    data = {
    "place_name": location.city,
    "state": location.state,
    "latitude": str(location.lat),
    "longitude": str(location.long),
    "zip": str(location.zipcode),
    "population": location.population,
    "check_ins": str(check_ins)
    }

    return(jsonify(data))

if __name__ == '__main__':
    app.run(debug=True)
