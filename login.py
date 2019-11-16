from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from colored import fg, stylize
from yaspin import yaspin
import PyInquirer as pq

import requests as rq
from vars import *
import os.path
import pickle
import json

# Объект ученика
class Student:
    def __init__(self, id=None, name=None, grade=None, token=None, login=None):
        self.id = id
        self.token = token
        self.login = login
        self.name = name
        self.grade = grade
        

    def __str__(self):
        info = get_student_info(self.token, extended=True)
            
        info['gender'] = "Муж." if info["gender"] == "male" else "Жен."
        info['login'] = self.login

        text = """
    Имя: {name}
    Класс: {grade}
    Город: {city}
    Школа: {school}
    Пол: {gender}
    Логин: {login}
    Эл. Почта: {email}
        """.format(
            name = info['fullname'],
            grade = info["grade"],
            city = info["city"],
            school = info["school"], 
            gender = info["gender"], 
            login = info["login"],
            email = info['email']
        )
        
        return text

    def get_schedule(self, date=None, silent=False):
        if not silent:
            load_spinner = yaspin(text="Загрузка...")
            load_spinner.text = "[Получение дневника из журнала...]"
        else:
            load_spinner = None
        diary = rq.get(
            API_URL + "getschedule",
            params={
                "devkey": DEVKEY,
                "vendor": VENDOR,
                "out_format": "json",
                "student": self.id,
                "auth_token": self.token,
                "days": "20191118-20191124",
                "rings": "true"
            }
        ).json()['response']

        if diary["error"] is not None:
            if not silent:
                load_spinner.text = ""
                load_spinner.fail(stylize("Ошибка получения расписания: " + diary["error"], fg("red")))
            raise LookupError(diary["error"])

        schedule = diary['result']['students'][str(self.id)]
        if not silent:
            load_spinner.text = ""
            load_spinner.ok(stylize("[Расписание успешно получено!] ", fg("green")))
        return schedule


def google_login():
    google_spinner = yaspin(text="Вход в google...")
    google_spinner.start()
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            google_spinner.text = "[Ожидание ответа Google OAuth...]"
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    google_spinner.text = ""
    google_spinner.ok("Вход в Google выполнен успешно")
    service = build('calendar', 'v3', credentials=creds)

    return service


# Классический вход в элжур (получение токена и объекта)
def eljur_login():
    with open("users.json", "r") as creds:
        logged_users = json.load(creds)

    eljur_auth_choice = [{
        "type": "list",
        "message": "Выберите пользователя:",
        "name": "auth_choice", "default": 1,
        "choices": []
    }]

    current_student = Student()

    for i in logged_users:
        eljur_auth_choice[0]["choices"].append({"name": logged_users[i]["name"],
                                                "value": logged_users[i]["login"]})

    eljur_auth_choice[0]["choices"].append(
        {"name": "Добавить пользователя"})

    answer = {}

    while not answer.get("auth_choice"):
        answer = pq.prompt(eljur_auth_choice)

    login = answer["auth_choice"]
    if login not in logged_users.keys():
        login = pq.prompt([{
            "type": "input",
            "name": "login",
            "message": "Введите логин:"
        }])['login']
        password = pq.prompt([{
            "type": "password",
            "name": "password",
            "message": "Введите пароль:"
        }])['password']
        auth_response = rq.get(
            "https://markbook.eljur.ru/apiv3/auth", params={
                "devkey": DEVKEY,
                "out_format": "json",
                "vendor": VENDOR,
                "login": login,
                "password": password}).json()

        if auth_response["response"]["error"] is not None or "":
            print("Ошибка входа: " + auth_response["response"]["error"])
            exit(auth_response["response"]["state"])
        current_student.login = login
        current_student.token = auth_response['response']['result']['token']
        current_student.id, current_student.name, current_student.grade = get_student_info(current_student.token)
        logged_users[current_student.login] = {"name": current_student.name,
                                               "id": current_student.id,
                                               "grade": current_student.grade,
                                               "login": current_student.login,
                                               "token": current_student.token}

        with open("users.json", "w") as write_creds:
            json.dump(logged_users, write_creds)

        return current_student
    else:
        current_student.login = login
        current_student.token = logged_users[login]["token"]
        current_student.id, current_student.name, current_student.grade = get_student_info(current_student.token)
        logged_users[current_student.login] = {"name": current_student.name,
                                               "id": current_student.id,
                                               "grade": current_student.grade,
                                               "login": current_student.login,
                                               "token": current_student.token}
        return current_student


# Получение информации об ученике через запрос getrules
def get_student_info(token, extended=False):
    rules_params = {
        "DEVKEY": DEVKEY, 
        "vendor": VENDOR,
        "out_format": "json",
        "auth_token": token,
    }

    user_info = rq.get("https://markbook.eljur.ru/apiv3/getrules", params=rules_params).json()["response"]
    if user_info["error"] is not None or "":
        print("Ошибка при получении информации об ученике: " + user_info["error"])
        raise LookupError(user_info["error"])
    # student = list(students.values())[0]    students = user_info["result"]["relations"]["students"]
    student_id = user_info["result"]["name"]
    name = user_info["result"]["relations"]["students"][student_id]["title"]
    grade = user_info["result"]["relations"]["students"][student_id]["class"]
    if not extended:
        return student_id, name, grade
    else:
        city = user_info["result"]["city"]
        email = user_info["result"]["email"]
        fullname = user_info["result"]["title"]
        gender = user_info["result"]["gender"]
        school = user_info["result"]["relations"]["schools"][0]["title"]
        return {
                "student_id": student_id,
                "fullname": fullname,
                "grade": grade,
                "city": city,
                "email": email,
                "gender": gender,
                "school": school
                }