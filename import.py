import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))

def main():

    # Open a file using Python's CSV reader.
    f = open("zips.csv")
    reader = csv.reader(f)

    # Iterate over the rows of the opened CSV file.
    for row in reader:

        # Execute database queries, one per row; then print out confirmation.
        db.execute("INSERT INTO locations (Zipcode, City, State, Lat, Long, Population) VALUES (:Zipcode, :City, :State, :Lat, :Long, :Population)",
                    {"Zipcode": row[0], "City": row[1], "State": row[2], "Lat": row[3], "Long": row[4], "Population":row[5]})
        print(row)

    # Technically this is when all of the queries we've made happen!
    db.commit()

if __name__ == "__main__":
    main()

# locations = db.execute("SELECT Zipcode, City, State, Lat, Long, Population FROM locations").fetchall() # execute this SQL command and return all of the results

# users = db.execute("INSERT INTO users (first_name, last_name, password) VALUES ('Artin', 'Bogdanov', 'abcd1234')")

# users = db.execute('SELECT id, first_name, last_name, password').fethall()

# users = db.execute('CREATE TABLE users (id SERIAL PRIMARY KEY, first_name VARCHAR NOT NULL, last_name VARCHAR NOT NULL, password VARCHAR NOT NULL)")

# for location in locations:
#     print(f"{location.zipcode} {location.city} {location.state}") # for every location, print out the locations info

# print(locations)
# print(users)

