# Import necessary libraries
import os
import json
import requests
from flask import Flask, request, Response

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

api_token = os.environ["API_TOKEN"]
channel_id = os.environ["CHANNEL_ID"]

# Initialize Flask app
app = Flask(__name__)

#
# You don't need to make changes to anything above this line
#


@app.route('/events', methods=['GET'])
def events_handler():

    request_body_json = request.get_json()

    if "challenge" in request_body_json:
        # Respond to the challenge
        return Response(request_body_json["challenge"]), 200
    else:
        # Store details about the user
        evt = request_body_json["event"]
        user_id = evt["user"]["id"]
        user_name = evt["user"]["real_name_normalized"]
        status_text = evt["user"]["profile"]["status_text"]
        status_emoji = evt["user"]["profile"]["status_emoji"]

        # If no full name set, use the username instead
        if user_name == "":
            user_name = evt["user"]["name"]

        # Build the message payload
        build_message(user_id, user_name, status_text, status_emoji)

    # Return a 200 to the event request
    return Response(status=200)


# Build the message payload
def build_message(user_id, user_name, status_text, status_emoji):

    if len(status_text) > 0:
        # If their status contains some text
        message = [{
            "pretext": user_name + " updated their status:",
            "text": status_emoji + " *" + status_text + "*"
        }]
    else:
        # If their status is empty
        message = [{
            "pretext": user_name + " cleared their status",
        }]

    post_update(message)

    return


# Post the actual message to a channel
def post_update(attachments):
    data = {
        "token": api_token,
        "channel": channel_id,
        "text": json.dumps(attachments, separators=(',', ':')),
        "pretty": True
    }
    try:
        r = requests.post("https://slack.com/api/chat.postmessage", data=data)
        r.raise_for_status()

        # log Slack API responses
        print(r.json())

    except requests.exceptions.HTTPError as err:
        # If there's an HTTP error, log the error message
        print(err)

    return
