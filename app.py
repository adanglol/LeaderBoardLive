# System level imports
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

# Using the Auth0 Python SDK to handle authentication in a Flask app
# flask pymongo for mongodb
from authlib.integrations.flask_client import OAuth
from flask_pymongo import pymongo

# Flask as well as env from dotenv to load our environment variables
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

# import our forms.py file
from forms import LeaderBoardForm

# Load environment variables from .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Flask configuration
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Mongo configuration and connecting with our database
mongo = pymongo(app, uri=env.get("MONGO_URI"))

# Auth0 configuration
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# --------------------------------------------------------------------------------------------- #
# Routes - where we define the endpoints of our application 
# --------------------------------------------------------------------------------------------- #

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

# to add user to our db in MongoDB
@app.route("/adduser")
def adduser():
    # if they are logged in
    if session:
        # Add a user to our database
        users = mongo.db.user_data
        users.insert_one(session.get('user'))
        return "User added to MongoDB"
    else:
        return "No user logged in"

# define new route for our leaderboard
@app.route("/addleaderboard", methods=["GET", "POST"])
def addleaderboard():
    # adding LeaderBoardForm
    form = LeaderBoardForm()
    # if the form is submitted
    if form.is_submitted():
        # get data from the form
        data = request.form 
        # making new collection in our database for leaderboards
        leaderboards = mongo.db.leaderboard
        # inserting our data name from the form into our leaderboards collection
        leaderboards.insert_one({"name": data.get("name")})
    # render our template passing in our form
    return render_template("addleaderboard.html", form=form)





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 5000))
