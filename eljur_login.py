from eljur import *

import PyInquirer as pq
import requests as rq
import json


def expired_token():
    # TODO: Token validation
    pass


def add_user():
    with open("users.json", "r") as creds:
        logged_users = json.load(creds)

    sign_in_promt = pq.prompt([
        {
            "type": "input",
            "name": "login",
            "message": "Введите логин:"
        }, {
            "type": "password",
            "name": "password",
            "message": "Введите пароль:"
        }
    ])

    login = sign_in_promt['login']
    password = sign_in_promt['password']

    auth_request = rq.get(
        "https://markbook.eljur.ru/apiv3/auth", params={
            "devkey": DEVKEY,
            "vendor": VENDOR,
            "out_format": "json",
            "login": login,
            "password": password
        }
    ).json()

    auth_response = auth_request["response"]

    if auth_response["error"] is not None or "":
        print("Ошибка входа: " + auth_response["error"])
        exit(auth_response["state"])

    current_student = Student(auth_response['result']['token'], login)

    logged_users[current_student.login] = {
        "login": current_student.login,
        "token": current_student.token,
        "name": current_student.name,
        "grade": current_student.grade,
    }

    with open("users.json", "w") as write_creds:
        json.dump(logged_users, write_creds)

    return current_student


def choose_user():
    with open("users.json", "r") as creds:
        logged_users = json.load(creds)

    eljur_auth_choice = [
        {
            "type": "list",
            "message": "Выберите пользователя:",
            "name": "auth_choice", "default": 1,
            "choices": []
        }
    ]

    for i in logged_users:
        eljur_auth_choice[0]["choices"].append(
            {
                "name": "{0} ({1} класс)".format(logged_users[i]["name"], logged_users[i]["grade"]),
                "value": logged_users[i]
            }
        )

    eljur_auth_choice[0]["choices"].append({"name": "Добавить пользователя", "value": "add_user"})

    answer = pq.prompt(eljur_auth_choice)

    if answer["auth_choice"] == "add_user":
        return add_user()
    else:
        login = answer["auth_choice"]['login']
        token = answer["auth_choice"]['token']

    return Student(token, login)


def eljur_login():
    return choose_user()
