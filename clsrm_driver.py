import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from drive_driver import DriveDriver

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.topics',
    'https://www.googleapis.com/auth/classroom.announcements',
    'https://www.googleapis.com/auth/classroom.rosters.readonly'
]

class ClsrmDriver:
    def __init__(self):
        """Shows basic usage of the Classroom API.
        Prints the names of the first 10 courses the user has access to.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('classroom', 'v1', credentials=creds)

    def getCourses(self):
        return self.service.courses().list().execute()['courses']
    
    def getCourseInfo(self, courseId):
        return self.service.courses().get(id=courseId).execute()

    def listCourseWork(self, courseId):
        return self.service.courses().courseWork().list(courseId=courseId).execute()['courseWork']

    def getCourseWork(self, courseId, id):
        return self.service.courses().courseWork().get(courseId=courseId, id=id).execute()
    
    def createCoursework(self, courseId, courseWork):
        # courseWork format: https://developers.google.com/classroom/reference/rest/v1/courses.courseWork
        request = self.service.courses().courseWork().create(courseId=courseId)
        request.body = json.dumps(courseWork)
        request.body_size = len(request.body)
        request.execute()

    def getStudentSubmissions(self, courseId, courseWorkId):
        return self.service.courses().courseWork().studentSubmissions().list(courseId=courseId, courseWorkId=courseWorkId).execute()['studentSubmissions']

    def addAttachments(self, courseId, courseWorkId, submissionId, attachments):
        # attachments format: https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions#Attachment
        body = {
            "addAttachments": attachments
        }
        request = self.service.courses().courseWork().studentSubmissions().modifyAttachments(courseId=courseId, courseWorkId=courseWorkId, id=submissionId)
        request.body = json.dumps(body)
        request.body_size = len(request.body)
        request.execute()
    
    def getAttachments(self, courseId, courseWorkId, submissionId):
        return self.service.courses().courseWork().studentSubmissions().get(courseId=courseId, courseWorkId=courseWorkId, id=submissionId).execute()['assignmentSubmission']['attachments']

if __name__ == '__main__':
    clsrm = ClsrmDriver()
    drive = DriveDriver()

    url = "https://api.twilio.com/2010-04-01/Accounts/AC2080a2bffe112c85f50b775ea2ec07c5/Messages/MM5f29d20fda765b3ff18c1fb6b761013c/Media/ME60a64794fca78fd9788bc2d5c836c79c"

    # sample addAttachments
    
    courseId = clsrm.getCourses()[1]["id"]
    
    courseWorkId = [cw for cw in clsrm.listCourseWork(courseId) if cw['title'] == "Test Assignment 2"][0]["id"]
    submissionId = clsrm.getStudentSubmissions(courseId, courseWorkId)[0]["id"]
    # attachments = [{
    #     "link": {
    #         "url": "https://www.google.com/",
    #     }
    # }]
    # clsrm.addAttachments(courseId, courseWorkId, submissionId, attachments)
    
    # for looking at structure of what is returned
    with open("out.json", "w") as f:
        f.write(json.dumps(clsrm.getStudentSubmissions(courseId, '57186993887')))
        f.write(json.dumps(clsrm.getAttachments(courseId, courseWorkId, submissionId)))

    # sample createCoursework
    # courseWork = {
    #     "title": "Test Assignment 3",
    #     "workType": "ASSIGNMENT",
    #     "state": "PUBLISHED"
    # }
    # clsrm.createCoursework(courseId, courseWork)



# courseId = [c for c in clsrm.getCourses() if c['name'] == "LA Hacks 2020"][0]["id"]
#     courseWorkId = [cw for cw in clsrm.getCourseWork(courseId) if cw['title'] == "Test Assignment 2"][0]["id"]
#     submissionId = clsrm.getStudentSubmissions(courseId, courseWorkId)[1]["id"]
#     attachments = [{
#         "driveFile": {
#             "id": drive.uploadFromURL("image", url, "image/jpeg")
#         }
#     },
#     {
#         "driveFile": {
#             "id": drive.uploadText("essay", "the brown fox jumped over the lazy dog", "text/plain")
#         }
#     }]
#     clsrm.addAttachments(courseId, courseWorkId, submissionId, attachments)