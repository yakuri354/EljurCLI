import pickle
import os.path
import json
import PyInquirer as pq
import requests as rq
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from EljurSched import devkey
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def google_login():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def eljur_login():
    with open("users.json", "r") as creds:
        logged_users = json.load(creds)
    eljur_auth_choice = [{"type": "list", "message": "Select your username",
                             "name": "auth_choice", "default": 1,
                              "choices": []}]
    eljur_login_input = [{"type": "input", "name": "login", "message":"Enter your login:"}]
    eljur_password_input = [{"type": "password", "name": "password", "message":"Enter your password:"}]
    usernames = list(logged_users.keys())
    for i in range(len(usernames)):
        eljur_auth_choice[0]["choices"].append({"name": usernames[i]})
    eljur_auth_choice[0]["choices"].append({"name": "Add new account"})
    answer = {}
    while not answer.get("auth_choice"):
        answer = pq.prompt(eljur_auth_choice)
    login = answer["auth_choice"]
    if login not in logged_users.keys():
        login = pq.prompt(eljur_login_input)['login']
        password = pq.prompt(eljur_password_input)['password']
        auth_params = {"devkey": devkey, "out_format": "json", "vendor": "markbook", "login": login,
                       "password": password}
        auth_response = rq.get("https://markbook.eljur.ru/apiv3/auth", params=auth_params).json()
        if auth_response["response"]["state"] != 200 or "200":
            print("Error: " + auth_response["response"]["error"])
        token = auth_response['response']['result']['token']
        with open("users.json", "w") as write_creds:
            json.dump({login: token}, write_creds)
        return token
    else:
        token = logged_users[login]
        return token
