Web Programming with Python and JavaScript
# Project1: Rainy Day
Student: Artin Bogdanov

This project cover e2e full-stack development, including: 

Login
Search
API (call external API and build your own) 
DB 

The requirement was to use following technologies: 

Python
Flask & jinja
PostgeSQL (Heroku) 
HTML/CSS (Bootstrap) 

and use Dark Sky Weather Data. 

Structure: 

The project includes following docs: 

-Static #all custom styling will be stored. Static is conventional name for the Flask application
   -Style.css #custome css file which includes all customizations that will overlay Bootrap styles which are linked in        layout.html
   
-Templates #that's where all HTML files are stored. 
   -Error.html
   -Index.html
   -Layout.html #the default template for all pages. 
   -Login.html
   -SignUp.html
   -Search.html
   -Location.html
   -Success.html

application.py #the main python application which manages the entire app. 
import.py #imports from zips.csv to our database.  
requirements.txt # list of required technologies
zip.csv 
README.md #the file you are reading now :) 
