"""
This is the API test file.
Here I wrote a bare-bones Flask web-API that only has the single "/log" endpoint.
It only accepts POST requests, where it expects to receive JSON data
that is compatible with the dataset.

It is also highly like that I will re-name the file.
"""

#imports:
#//>>
from typing import Dict, Union

# API stuff:
from flask import Flask, request

# helper function for saving to csv:
from helper import save_to_file

#//<<

app: Flask = Flask(__name__)

CSV_FILE: str = "user_data.csv"

@app.route("/")
def index() -> str:
    return "<h1>Hi there!</h1>"

@app.route("/log", methods=["POST"])
def log_data():
    #//>>
    """puts user data into dataset

    This function puts all the prior data from the user into the dataset.
    The incoming payload MUST be in the JSON-format.
    If everything goes according to plan, we send code 204 back.
    """

    # in case the data is not JSON:
    if not request.is_json:
        return "content must be sent in JSON-format", 400

    # save the data in the file
    data: Dict[str, Union[str, float]] = request.get_json()
    save_to_file(payload=data, path=CSV_FILE)

    return "", 204
    #//<<

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
