import json
import datetime
import calendar
import time
from flask import Flask, request, session
from twilio.twiml.messaging_response import (
    MessagingResponse,
    Message,
    Body,
    Media
)
from clsrm_driver import ClsrmDriver
from drive_driver import DriveDriver

SECRET_KEY = 'LAHACKS2020'
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/sms', methods=['GET', 'POST'])
def parser():

    # Get status from cookie

    current_class = session.get('clsrm_class', '')

    current_sel_type = session.get('clsrm_sel_type', '')
    current_sel_id = session.get('clsrm_sel_id', '')

    clsrm_choice_type = session.get('clsrm_choice_type', '')
    last_options = session.get('clsrm_options', '')

    # Set up output vars
    out_status_text = ''
    out_content_text = ''
    out_options_explainer = ''
    out_options = []
    given_options = {}

    # TODO: Verify/identify number
    from_number = request.form['From']

    from_text = request.form['Body']
    from_n_media = request.form['NumMedia']

    clsrm = ClsrmDriver()
    drive = DriveDriver()

    if last_options and not from_text.lower() == 'home':
        prev_options = json.loads(last_options)
        if clsrm_choice_type == 'ATTACH_IMG':
            class_info = clsrm.getCourseInfo(current_class)
            out_status_text += '\n' + class_info['name']
            out_content_text = class_info['descriptionHeading']
        
            if from_n_media == '1':
                clsrm_sel_id = session['clsrm_sel_id']
                course_work = clsrm.getCourseWork(current_class, clsrm_sel_id)
                submission = clsrm.getStudentSubmissions(
                    current_class, clsrm_sel_id)[0]

                url = request.form['MediaUrl0']

                attachments = [{
                "driveFile": {
                    "id": drive.uploadFromURL('clsrmImage' + datetime.datetime.fromtimestamp(calendar.timegm(time.gmtime())).isoformat(), url, 'image/jpeg')
                    }
                }]
                clsrm.addAttachments(current_class, course_work['id'], submission['id'], attachments)
                
                out_status_text = 'Submitted image to ' + course_work['title'] + ':\n'
                out_status_text += from_text
            if int(from_n_media) > 1:
                out_status_text = 'Error: You can only send one picture at a time.'
            out_content_text += '\nReturning to ' + class_info['name']

            out_options.append('1) List Announcements')
            given_options['1'] = 'class_list_statusan'
            out_options.append('2) List Coursework')
            given_options['2'] = 'class_list_cw'
            out_options.append('3) View Class Info')
            given_options['3'] = 'class_info'
            session['clsrm_options'] = json.dumps(given_options)
            session['clsrm_choice_type'] = 'class_options'
            session['clsrm_class'] = current_class
        elif clsrm_choice_type == 'ATTACH_TEXT':
            print('attach_text')
            if from_text.upper() != 'back':
                clsrm_sel_id = session['clsrm_sel_id']
                course_work = clsrm.getCourseWork(current_class, clsrm_sel_id)
                class_info = clsrm.getCourseInfo(current_class)
                submission = clsrm.getStudentSubmissions(
                    current_class, clsrm_sel_id)[0]

                attachments = [{
                "driveFile": {
                    "id": drive.uploadText('clsrmSubmission' + datetime.datetime.fromtimestamp(calendar.timegm(time.gmtime())).isoformat(), from_text, 'text/plain')
                    }
                }]
                clsrm.addAttachments(current_class, course_work['id'], submission['id'], attachments)
                
                out_status_text = 'Submitted text to ' + course_work['title'] + ':\n'
                out_status_text += from_text
            
            
            
            out_content_text += '\nReturning to ' + class_info['name']
            class_info = clsrm.getCourseInfo(current_class)
            out_status_text += '\n' + class_info['name']
            out_content_text = class_info['descriptionHeading']

            out_options.append('1) List Announcements')
            given_options['1'] = 'class_list_statusan'
            out_options.append('2) List Coursework')
            given_options['2'] = 'class_list_cw'
            out_options.append('3) View Class Info')
            given_options['3'] = 'class_info'
            session['clsrm_options'] = json.dumps(given_options)
            session['clsrm_choice_type'] = 'class_options'
            session['clsrm_class'] = current_class
        elif clsrm_choice_type == 'ATTACH_VOICE':
            print('attach_voice')
        elif not from_text.isdigit() or from_text not in prev_options:
            out_status_text = 'Type only a digit to select an option, or HOME to return home' 
        else:
            if clsrm_choice_type == 'class':
                current_class = prev_options[from_text]

                class_info = clsrm.getCourseInfo(current_class)
                print(current_class)
                out_status_text = class_info['name']
                out_content_text = class_info['descriptionHeading']

                out_options.append('1) List Announcements')
                given_options['1'] = 'class_list_statusan'
                out_options.append('2) List Coursework')
                given_options['2'] = 'class_list_cw'
                out_options.append('3) View Class Info')
                given_options['3'] = 'class_info'
                session['clsrm_options'] = json.dumps(given_options)
                session['clsrm_choice_type'] = 'class_options'
                session['clsrm_class'] = current_class
            if clsrm_choice_type == 'class_options':
                choice_text = prev_options[from_text]
                class_info = clsrm.getCourseInfo(current_class)
                out_status_text = class_info['name']
                if choice_text == 'class_list_an':
                    print("list announcements")
                if choice_text == 'class_list_cw':
                    course_works = clsrm.listCourseWork(current_class)
                    out_options_explainer = 'Course Work:'
                    for num, work in enumerate(course_works, start=1):
                        if work['state'] == 'PUBLISHED':
                            option = str(num) + ') ' + work['title']
                            out_options.append(option)
                            given_options[str(num)] = work['id']
                    session['clsrm_choice_type'] = 'class_list_cw'
                    session['clsrm_options'] = json.dumps(given_options)
                if choice_text == 'class_info':
                    out_status_text = class_info['name']
                    out_content_text = ''
                    for field in ['Section', 'Room', 'Description']:
                        if field.lower() in class_info:
                            out_content_text += field + ': ' + \
                                class_info[field.lower()] + '\n'

                    out_options.append('1) List Announcements')
                    given_options['1'] = 'class_list_an'

                    out_options.append('2) List Coursework')
                    given_options['2'] = 'class_list_cw'

                    out_options.append('3) View Class Info')
                    given_options['3'] = 'class_info'

                    session['clsrm_options'] = json.dumps(given_options)
            if clsrm_choice_type == 'class_list_cw':
                clsrm_sel_id = prev_options[from_text]

                course_work = clsrm.getCourseWork(current_class, clsrm_sel_id)
                class_info = clsrm.getCourseInfo(current_class)

                out_status_text = class_info['name'] + \
                    ': ' + course_work['title']
                if 'description' in course_work:
                    out_content_text += course_work['description'] + '\n'

                # TODO: if you have a submission...
                # if 'dueDate' in course_work:  todo: due date

                submission = clsrm.getStudentSubmissions(
                    current_class, clsrm_sel_id)[0]

                state = submission['state']

                counter = 0

                out_options_explainer = 'Options:'
                if 'attachments' in submission['assignmentSubmission']:
                    out_options.append('1) View Attachments')
                    given_options['1'] = 'cw_list_attach'
                    counter += 1

                print(json.dumps(submission))

                if state == 'NEW' or state == 'CREATED' or state == 'RECLAIMED_BY_STUDENT':
                    out_options.append(str(counter + 1) + ') Add Attachments')
                    given_options[str(counter + 1)] = 'cw_add_attach'
                    out_options.append(str(counter + 2) + ') Turn in')
                    given_options[str(counter + 2)] = 'cw_turnin'
                    counter += 2

                out_options.append(str(counter + 1) + ') Back')
                given_options[str(counter + 1)] = 'cw_back'

                session['clsrm_options'] = json.dumps(given_options)
                session['clsrm_choice_type'] = 'cw_options'
                session['clsrm_sel_type'] = 'cw'
                session['clsrm_sel_id'] = clsrm_sel_id
            if clsrm_choice_type == 'cw_options':
                choice_text = prev_options[from_text]
                clsrm_sel_id = session['clsrm_sel_id']
                course_work = clsrm.getCourseWork(current_class, clsrm_sel_id)
                class_info = clsrm.getCourseInfo(current_class)
                submission = clsrm.getStudentSubmissions(
                    current_class, clsrm_sel_id)[0]
                if choice_text == 'cw_list_attach':
                    print('list_attach')
                    attachments = clsrm.getAttachments(
                        current_class, clsrm_sel_id, submission['id'])
                    out_options_explainer = 'Attachments:'
                    print(json.dumps(attachments))
                    out_status_text = course_work['title'] + ' Attachments: '
                    out_content_text = ''
                    for num, attach in enumerate(attachments, start=1):
                        if 'link' in attach:
                            out_content_text += str(num) + '- Link: ' + \
                                                    attach['link']['title'] + '\n'
                            given_options[str(num)] = clsrm_sel_id
                        if 'driveFile' in attach:
                            out_content_text += str(num) + '- File: ' + \
                                                    attach['driveFile']['title'] + '\n'

                    submission = clsrm.getStudentSubmissions(
                        current_class, clsrm_sel_id)[0]

                    state = submission['state']

                    counter = 0

                    out_options_explainer = 'Options:'
                    if 'attachments' in submission['assignmentSubmission']:
                        out_options.append('1) View Attachments')
                        given_options['1'] = 'cw_list_attach'
                        counter += 1

                    if state == 'NEW' or state == 'CREATED' or state == 'RECLAIMED_BY_STUDENT':
                        out_options.append(
                            str(counter + 1) + ') Add Attachments')
                        given_options[str(counter + 1)] = 'cw_add_attach'
                        out_options.append(str(counter + 2) + ') Turn in')
                        given_options[str(counter + 2)] = 'cw_turnin'
                        counter += 2

                    out_options.append(str(counter + 1) + ') Back')
                    given_options[str(counter + 1)] = 'cw_back'

                    session['clsrm_options'] = json.dumps(given_options)
                    session['clsrm_choice_type'] = 'cw_options'
                    session['clsrm_sel_type'] = 'cw'
                    session['clsrm_sel_id'] = clsrm_sel_id
                if choice_text == 'cw_add_attach':

                    out_status_text = course_work['title']
                    out_options_explainer = 'Add Attachment Type:'

                    out_options.append('1) Add Text')
                    given_options['1'] = 'attach_text'
                    out_options.append('2) Dictate Text')
                    given_options['2'] = 'attach_voice'
                    out_options.append('3) Add Picture')
                    given_options['3'] = 'attach_image'
                    out_options.append('4) Back')
                    given_options['4'] = 'attach_back'
                    session['clsrm_options'] = json.dumps(given_options)
                    session['clsrm_choice_type'] = 'attach_options'
                    session['clsrm_class'] = current_class
                    session['clsrm_sel_id'] = clsrm_sel_id

                if choice_text == 'cw_turnin':
                    out_status_text = course_work['title'] + ' Submitted!'

                    class_info = clsrm.getCourseInfo(current_class)
                    out_content_text = class_info['name'] + \
                        '\n' + class_info['descriptionHeading']

                    out_options.append('1) List Announcements')
                    given_options['1'] = 'class_list_statusan'
                    out_options.append('2) List Coursework')
                    given_options['2'] = 'class_list_cw'
                    out_options.append('3) View Class Info')
                    given_options['3'] = 'class_info'
                    session['clsrm_options'] = json.dumps(given_options)
                    session['clsrm_choice_type'] = 'class_options'
                    session['clsrm_class'] = current_class
                if choice_text == 'cw_back':
                    class_info = clsrm.getCourseInfo(current_class)
                    out_status_text = class_info['name']
                    out_content_text = class_info['descriptionHeading']

                    out_options.append('1) List Announcements')
                    given_options['1'] = 'class_list_statusan'
                    out_options.append('2) List Coursework')
                    given_options['2'] = 'class_list_cw'
                    out_options.append('3) View Class Info')
                    given_options['3'] = 'class_info'
                    session['clsrm_options'] = json.dumps(given_options)
                    session['clsrm_choice_type'] = 'class_options'
                    session['clsrm_class'] = current_class

            if clsrm_choice_type == 'attach_options':
                choice_text = prev_options[from_text]
                clsrm_sel_id = session['clsrm_sel_id']
                course_work = clsrm.getCourseWork(current_class, clsrm_sel_id)
                class_info = clsrm.getCourseInfo(current_class)
                submission = clsrm.getStudentSubmissions(
                    current_class, clsrm_sel_id)[0]

                if choice_text == 'attach_text':
                    print('attach text')
                    out_status_text = 'Attach text to ' + course_work['title'] + ':'
                    out_content_text = 'The next message you send will be attached to your assignment.\nSend \'BACK\' to cancel.'
                    session['clsrm_choice_type'] = 'ATTACH_TEXT'
                if choice_text == 'attach_voice':
                    print('attach voice')
                if choice_text == 'attach_image':
                    print('attach image')
                    out_status_text = 'Attach an image to ' + course_work['title'] + ':'
                    out_content_text = 'The next image you send will be attached to your assignment.\nSend any text to cancel.'
                    session['clsrm_choice_type'] = 'ATTACH_IMG'
                if choice_text == 'attach_back':
                    class_info = clsrm.getCourseInfo(current_class)
                    out_status_text = class_info['name']
                    out_content_text = class_info['descriptionHeading']

                    out_options.append('1) List Announcements')
                    given_options['1'] = 'class_list_statusan'
                    out_options.append('2) List Coursework')
                    given_options['2'] = 'class_list_cw'
                    out_options.append('3) View Class Info')
                    given_options['3'] = 'class_info'
                    session['clsrm_options'] = json.dumps(given_options)
                    session['clsrm_choice_type'] = 'class_options'
                    session['clsrm_class'] = current_class
            session['clsrm_class']= current_class
        

    elif from_text.lower() == 'home':
        out_status_text += 'HOME'
        out_content_text= ''
        out_options_explainer= 'Select a class:'
        courses_list= clsrm.getCourses()
        for num, course in enumerate(courses_list, start=1):
            option= str(num) + ') ' + course['name']
            if 'section' in course:
                option += ' (' + course['section'] + ')'
            out_options.append(option)
            given_options[str(num)]= course['id']
        session['clsrm_options']= json.dumps(given_options)
        session['clsrm_choice_type']= 'class'
        session['clsrm_class']= ''
        session['clsrm_sel_type']= ''
        session['clsrm_sel_id']= ''

    out_options_text= "\n".join(option for option in out_options)

    out_text= out_status_text.rstrip() + '\n'
    if out_content_text:
        out_text += out_content_text.rstrip() + '\n'
    if out_options_explainer:
        out_text += out_options_explainer.rstrip() + '\n'
    out_text += (out_options_text)

    # Start our response
    resp= MessagingResponse()

    # Add a message
    resp.message(out_text)

    print(str(resp))
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
