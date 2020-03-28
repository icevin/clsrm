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
    current_status = session.get('clsrm_status', '/')
    # TODO: move away from using one cookie and use more cookies
    

    current_class = session.get('clsrm_class', '')
    current_type = session.get('clsrm_type', '')
    current_id = session.get('clsrm_sel_id', '')
    given_opens = session.get('clsrm_options','')

    # TODO: Keep track of what IDs the options I give correspond to


    # Set up output vars
    out_status_text = ''
    out_content_text = ''
    out_options = []

    new_status = '/'

    # TODO: Verify/identify number

    from_number = request.form['From']
    from_text = request.form['Body']
    from_n_media = request.from['NumMedia']

    if from_n_media:
        print("got media")
        # get media ID and get media object, if we are expecting media
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

    session['clsrm_status']=new_status
    
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
