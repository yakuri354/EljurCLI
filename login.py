import pickle
import os.path
import json
import PyInquirer as pq
import inquirer
import requests as rq
from yaspin import yaspin
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
devkey = "9235e26e80ac2c509c48fe62db23642c"


def google_login():
    google_spinner = yaspin(text="Вход в google...")
    google_spinner
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

def login(*args):
    print(args)
    with open("users.json", "r") as creds:
        logged_users = json.load(creds)

    # Choose user
    questions = [
        inquirer.List(
            'account',
            message="Веберете пользователя?",
            choices=list(logged_users.keys()) + ["Добавить пользователя"]
        )
    ]

    answers = inquirer.prompt(questions)

    if answers['account'] == "Добавить пользователя":
        questions = [
            inquirer.Text('login', message="Логин"),
            inquirer.Password('password', message="Пароль")
        ]

        new_user = inquirer.prompt(questions)
        auth_response = rq.get(
            "https://markbook.eljur.ru/apiv3/auth",
            params={
                "devkey": devkey,
                "vendor": "markbook",
                "out_format": "json",
                "login": new_user['login'],
                "password": new_user['password']
            }).json()

        token = auth_response['response']['result']['token']

        with open("users.json", "w") as users:
            json.dump(users, {new_user['login']: token})

        return token

    token = logged_users[answers['account']]

    return token

def eljur_login():

    with open("users.json", "r") as creds:
        logged_users = json.load(creds)

    eljur_auth_choice = [{
        "type": "list",
        "message": "Выберите пользователя:",
        "name": "auth_choice", "default": 1,
        "choices": []
    }]
    eljur_login_input = [{
        "type": "input",
        "name": "login",
        "message":"Введите логин:"
    }]
    eljur_password_input = [{
        "type": "password",
        "name": "password",
        "message":"Введите пароль:"
    }]
    usernames = list(logged_users.keys())

    for i in range(len(usernames)):
        eljur_auth_choice[0]["choices"].append({"name": usernames[i]})

    eljur_auth_choice[0]["choices"].append(
        {"name": "Добавить пользователя"})

    answer = {}

    while not answer.get("auth_choice"):
        answer = pq.prompt(eljur_auth_choice)
    
    login = answer["auth_choice"]

    if login not in logged_users.keys():
        login = pq.prompt(eljur_login_input)['login']
        password = pq.prompt(eljur_password_input)['password']
        auth_params = {
        "devkey": devkey,
        "out_format": "json",
        "vendor": "markbook",
        "login": login,
        "password": password
        }
        auth_response = rq.get("https://markbook.eljur.ru/apiv3/auth", params=auth_params).json()

        if auth_response["response"]["error"] is not None:
            print("Error: " + auth_response["response"]["error"])
        
        token = auth_response['response']['result']['token']
        logged_users[login] = token

        with open("users.json", "w") as write_creds:
            json.dump(logged_users, write_creds)
        return token
    else:
        token = logged_users[login]
        return token
