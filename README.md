# clsrm - LA Hacks 2020
Google Classroom via SMS

To setup ngrok tunnel & update phone number:
```
twilio phone-numbers:update "+XXXXXXXXXX" --sms-url="http://localhost:5000/sms"
```

To run flask server:
```
python3 server.py
```
