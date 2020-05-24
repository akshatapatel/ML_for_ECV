from flask import Flask, render_template 
# from flask.ext.cors import CORS, cross_origin
from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app)

@app.route("/")
@cross_origin(origin='*',headers=['Content-Type','Authorization'])

def home():
    return  render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True,host="127.0.0.1")
