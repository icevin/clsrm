# clsrm - GClassroom via SMS
See [LA Hacks 2020](https://devpost.com/software/clsrm-google-classroom-via-sms) submission
  - Google Cloud 1st Place: Best Hack Using Google Cloud
  - Facebook Best Collaboration Hack

## Inspiration
Across the country, COVID-19 is causing school districts to move online. But there are 4 million households with school aged children in the United States *without* home internet [1]. In a class of 25, that averages out to around 2 children. Without funding to buy Chromebooks and mobile hotspots, poorer school districts are forced to choose between cancelling classes completely and leaving their most disadvantaged students even further behind. The inequalities prevalent through our society are being exacerbated. 

One of the most popular ways school districts are moving online is through Google Classroom, a service that allows teachers to remotely assign homework, administer exams, provide feedback and grades, and interact with students. Our goal is ambitious: to solve the online learning problem by bringing Google Classroom to everyone, regardless whether or not they have home internet.

## What it does

Put simply, clsrm is a way to use Google Classroom without Internet. That means students without data plans and students with flip phones can participate in Google Classroom just like their internet-connected peers. We rely on older, more readily available technologies like SMS, MMS, and voice calls to access and use Google Classroom. Students can use SMS to navigate menus, view assignments, and submit shorter assignments. For longer, more complicated assignments, students can dictate with a voice call, or send photos using MMS. Because the images from flip phones are often very poor quality, we use document stitching algorithms to combine multiple pictures into one, increasing the effective resolution and making the image readable.

## How we built it

The following tools made clrsm possible:
* G Suite Classroom API, for obvious reasons
* G Suite Drive API, to upload text and media as submissions in Google Classroom
* Twilio Programmable SMS and Programmable Voice, to interact with the student
* Google Cloud Speech-To-Text API, for dictation service
* OpenCV, for document stitching
* Flask, for hosting our server

Architecturally, clsrm stands as an intermediary between students and Google Classroom. Teachers first add clsrm as a co-teacher for their classes, giving clsrm administrative privileges. Students enrolled through clsrm submit their assignments through SMS, MMS, or voice, and clsrm can then process them and upload them to Google Classroom on their behalf.

## Challenges we ran into

One challenging part of the project was coming up with and implementing feasible ways to circumvent the innate limitations of basic phones. It wasn't long after we started that we realized relying solely on SMS would make for an excruciating experience. That's when we came with the ideas of dictation through voice call and superresolution through image stitching. Of the two, image stitching turned out to be more difficult to implement, since neither of us were very familiar with OpenCV at the start.

## Accomplishments that we're proud of

We're proud to have created something that can potentially benefit a large number of people. In previous hackathons, we've both created cool tools and apps that are interesting and useful, but nothing comparable in impact to clsrm. Regardless of whether we win or not, this project is a success for us.

## What we learned

This was our first time using Twilio, even though we've seen Twilio sponsor many hackathons before. SMS always seemed like kind of a boring thing to us before, but as we continued developing this project, we began to finally understand the kinds of impact Twilio can have. Realizing that it's wrong to dismiss certain APIs as more useful than others, the most important thing we learned was to keep an open mind, because an open mind can lead to unexpected success.

## What's next for clsrm - Classroom via SMS
In the future, we'd like to create an voice-only interface that brings Google Classroom to students who only have a home phone without SMS as well. We didn't have time to implement this, but Twilio would certainly make this possible. As algorithms for image processing improve as well, using new tools in machine learning, we'd like to incorporate these algorithms to further extend the usability of the poor quality cameras on flip phones. 

## References
[1] https://www.theguardian.com/commentisfree/2020/mar/23/us-students-are-being-asked-to-work-remotely-but-22-of-homes-dont-have-internet

To setup ngrok tunnel & update phone number:
```
twilio phone-numbers:update "+XXXXXXXXXX" --sms-url="http://localhost:5000/sms"
```

To run flask server:
```
python3 server.py
```
