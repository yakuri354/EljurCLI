from login import eljur_login

import PyInquirer as pq
from vars import *

version = "0.4beta"


# Глобальные переменные хранятся в файле vars.py
# А вот это ^ тут нам не надо 

# Класс для хранения и перевода урока в событие гугла
class LessonEvent:
    def __init__(self, date, time, name, room=None, topic=None, time_zone="Europe/Moscow"):
        self.name = name
        if topic:
            self.topic = topic
        if room:
            self.room = room
        if time_zone == "Europe/Moscow":
            self.time_zone = "+03:00"
        self.date = date
        self.start_time, self.end_time = time.split("_")

    def __date_to_google_format(self):
        self.date.replace("-", "")
        self.date += "T"

    def start_google_format(self):
        self.__date_to_google_format()
        return self.date + self.start_time + self.time_zone

    def end_google_format(self):
        self.__date_to_google_format()
        return self.date + self.end_time + self.time_zone


def output_time(time):
    start, end = time.split("_")
    start = start[:5]
    end = end[:5]
    return start + "-" + end


# Получение календаря из гугла
# calendar = service.calendars().get(calendarId=primary_calendar_id).execute()
# events = service.events().list(calendarId=primary_calendar_id).execute()


# TODO: Переписать вывод расписания
def list_schedule(schedule=None, student=None, include_non_academ=None):
    if not include_non_academ:
        include_non_academ = pq.prompt(
            {
                "type": "confirm",
                "name": "non_academ_prompt",
                "message": "Хотите включить в расписание внеакадем?"
            })["non_academ_prompt"]
            
    if student and not schedule:
        schedule = student.get_schedule(silent=False)
    elif not student and schedule:
        raise NotImplementedError("Either schedule or student must be provided")
    for d in schedule["days"]:
        d = schedule["days"][d]
        current_schedule = d
        print(stylize("\n" + d["title"] + " \n", day_of_week_style))
        for i in range(len(current_schedule["items"]) + 1):
            if i == 0:
                continue
            # Вывод окна
            if not current_schedule["items"].get(str(i)):
                print("     {0} {1} Окно!".format(stylize(output_time(lessons_time[i]),
                                                          time_style), separator))
                continue
            i = current_schedule["items"][str(i)]
            # Вывод уроков с учетом кабинета
            if i["room"] is not None or "":
                print("     {0} {1} {2} в кабинете {3}".format(
                    stylize(output_time(i["starttime"] +
                                        "_" + i["endtime"]),
                            time_style), separator, i["name"],
                    stylize(i["room"], room_style)))
                # print(Lesson_Event(today, time_sort[int(i["sort"])]).start_google_format())
            else:
                print("     {0} {1} {2}".format(stylize(output_time(i["starttime"] +
                                                                    "_" + i["endtime"]),
                                                        time_style), separator, i["name"]))

        # Вывод внеакадема
        if current_schedule.get("items_extday") and include_non_academ:
            print(stylize("\n Внеакадем:\n", non_academ_style))

            for v in range(len(current_schedule["items_extday"])):
                v = current_schedule["items_extday"][v]
                print("     {0} {1} {2}".format(stylize(output_time(v["starttime"] + "_" + v["endtime"]),
                                                        time_style), separator, v["name"]))
        elif include_non_academ:
            print(stylize("\n Внеакадем отсутствует", non_academ_style))


def menu(current_student):
    main_menu = {
        "type": "list",
        "name": "main_menu",
        "message": "Меню:",
        "choices": [
            {
                "name": "Показать расписание",
                "value": "schedule"
            },
            {
                "name": "Экспорт расписания",
                "value": "export"
            },
            {
                "name": "Информация об ученике",
                "value": "info"
            },
            {
                "name": "Выход",
                "value": "exit"
            }
        ]
    }

    print("")
    answer = pq.prompt(main_menu)["main_menu"]
    
    if answer == "exit":
        exit()
    elif answer == "schedule":
        list_schedule(student=current_student)
        menu(current_student)
    elif answer == "info":
        # TODO: Написать нормальный вывод инфы об ученике
        print(current_student)
        menu(current_student)
    elif answer == "export":
        # TODO: Сделать экспорт календаря
        print("Уже скоро!")
        menu(current_student)


def main():
    print(greeting)
    current_student = eljur_login()
    menu(current_student)


if __name__ == "__main__":
    main()
