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

    # Get status from cookie
    current_status = session.get('status', '/')

    # TODO: Keep track of what IDs the options I give correspond to


    # status syntax:
    # /ccccc/aaaaa/<state>
    # ccccc = class id
    # aaaaa = post or assignment
    # <state

    # Set up output vars
    out_status_text = ''
    out_content_text = ''
    out_options = []

    new_status = '/'

    # TODO: Verify/identify number

    from_number = request.form['From']
    from_text = request.form['Body']


    path = current_status.split('/')

    if 0:
        print("false")
    elif from_text.isdigit():
        new_status = current_status + from_text + '/'
        out_status_text += 'Up one level'
    elif str.lower(from_text) == 'home' or current_status == '/':
        new_status = '/'
        out_status_text = 'Home'
        out_content_text = ''
        # Add classes options: out_options.append('')
        for n in range(1, 4):
            test = str(n) + ') ' + 'Option ' + str(n)
            out_options.append(test)
    else:
        new_status=current_status

    session['status']=new_status
    
    out_options_text="\n".join(option for option in out_options)
    
    out_text='{}:\n{}\nOptions:\n{}' \
        .format(out_status_text, out_content_text, out_options_text)

    # Start our response
    resp=MessagingResponse()

    # Add a message
    resp.message(out_text)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
