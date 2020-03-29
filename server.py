import json
from flask import Flask, request, session
from twilio.twiml.messaging_response import (
    MessagingResponse,
    Message,
    Body,
    Media
)
from clsrm_driver import ClsrmDriver

SECRET_KEY = 'LAHACKS2020'
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/sms', methods=['GET', 'POST'])
def parser():

    # Get status from cookie
    current_status = session.get('clsrm_status', '/')

    current_class = session.get('clsrm_class', '')
    
    current_selection_type = session.get('clsrm_sel_type', '')
    current_id = session.get('clsrm_sel_id', '')
    
    choice_type = session.get('clsrm_choice_type', '')
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

    if last_options and not from_text.lower() == 'home':
        prev_options = json.loads(last_options)
        if not from_text.isdigit() or from_text not in prev_options:
            out_status_text = 'Type only a digit to select an option, or HOME to return home'
        else:
            if choice_type == 'class':
                current_class = prev_options[from_text]
                
                current_status = '/c'     
                
                class_info = clsrm.getCourseInfo(current_class)
                print(current_class)
                out_status_text = class_info['name']
                out_content_text = class_info['descriptionHeading']
                
                out_options.append('1) List Announcements')
                given_options['1'] = 'class_list_an'
                out_options.append('2) List Coursework')
                given_options['2'] = 'class_list_cw'
                out_options.append('3) View Class Info')
                given_options['3'] = 'class_info'
                session['clsrm_options'] = json.dumps(given_options)
                session['clsrm_choice_type'] = 'class_options' 
                session['clsrm_class'] = current_class
            if choice_type == 'class_options':
                choice_text = prev_options[from_text]
                class_info = clsrm.getCourseInfo(current_class)
                out_status_text = class_info['name']
                if choice_text == 'class_list_an':
                    print("list announcements")
                if choice_text == 'class_list_cw':
                    course_works = clsrm.listCourseWork(current_class)
                    out_options_explainer = 'Course Work:'
                    for num, work in enumerate(course_works, start = 1):
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
                            out_content_text += field + ': ' + class_info[field.lower()] + '\n'

                    out_options.append('1) List Announcements')
                    given_options['1'] = 'class_list_an'
                    out_options.append('2) List Coursework')
                    given_options['2'] = 'class_list_cw'
                    out_options.append('3) View Class Info')
                    given_options['3'] = 'class_info'
                    session['clsrm_options'] = json.dumps(given_options)
            if choice_type == 'class_list_cw':
                clsrm_sel_id = prev_options[from_text]

                course_work = clsrm.getCourseWork(current_class, clsrm_sel_id)
                class_info = clsrm.getCourseInfo(current_class)

                out_status_text = class_info['name'] + ': ' + course_work['title']
                if 'description' in course_work:
                    out_content_text += course_work['description'] + '\n'
                # if 'dueDate' in course_work:  todo: due date
                    
                session['clsrm_sel_type'] = 'cw'
                session['clsrm_sel_id'] = clsrm_sel_id
                    
                    
            session['clsrm_class'] = current_class
                
                
    elif current_status == '/' or from_text.lower() == 'home':
        new_status = '/'
        out_status_text += 'HOME'
        out_content_text = ''
        out_options_explainer = 'Select a class:'
        courses_list = clsrm.getCourses()
        for num, course in enumerate(courses_list, start=1):
            option = str(num) + ') ' + course['name']
            if 'section' in course:
                option += ' (' + course['section'] + ')'
            out_options.append(option)
            given_options[str(num)] = course['id']
        session['clsrm_options'] = json.dumps(given_options)
        session['clsrm_choice_type'] = 'class'
        session['clsrm_status'] = 'choice'
        session['clsrm_class'] = ''
        session['clsrm_sel_type'] = ''
        session['clsrm_sel_id'] = ''    



    

    out_options_text = "\n".join(option for option in out_options)

    out_text = out_status_text.rstrip() + '\n'
    if out_content_text:
        out_text += out_content_text.rstrip() + '\n'
    if out_options_explainer:
        out_text += out_options_explainer.rstrip() + '\n'
    out_text += (out_options_text)

    # Start our response
    resp = MessagingResponse()

    # Add a message
    resp.message(out_text)

    print(str(resp))
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
