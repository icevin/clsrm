from flask import Flask, request, session
from twilio.twiml.messaging_response import (
    MessagingResponse,
    Message,
    Body,
    Media
)

SECRET_KEY = 'LAHACKS2020'
app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def parser():
    # TODO: Verify/identify number

    from_number = request.form['From']
    from_text = request.form['Body']
    from_n_media = request.from['NumMedia']
    
    out_text = []

    if from_n_media:
        print("got media")
        out_text.append("got media")
        # get media ID and get media object, if we are expecting media

    # Start our response
    resp=MessagingResponse()

    # Add a message
    resp.message(out_text)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
