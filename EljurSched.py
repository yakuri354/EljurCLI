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


def time_from_sched(lesson):
    time_str = stylize(output_time(lesson["starttime"] +
                                        "_" + lesson["endtime"]),
                                            time_style)
    return time_str


# Получение календаря из гугла
# calendar = service.calendars().get(calendarId=primary_calendar_id).execute()
# events = service.events().list(calendarId=primary_calendar_id).execute()


# TODO: Переписать вывод расписания
def list_schedule(schedule, include_non_academ=None):
    if include_non_academ ==  None:
        include_non_academ = pq.prompt(
            {
                "type": "confirm",
                "name": "non_academ_prompt",
                "message": "Хотите включить в расписание внеакадем?"
            }
        )["non_academ_prompt"]
    for day in schedule["days"]:
        day = schedule["days"][day]
        lessons = day["items"]

        last_lesson = max(map(int, list( day["items"].keys())))
        print("\n" + day["title"] + ":\n")
        for lesson in range(1, last_lesson + 1):
            lesson = str(lesson)
            if lessons.get(lesson) == None:
                print("\t{time} {sep} Окно!".format(
                    time = stylize(output_time(lessons_time[lesson]), time_style),
                    sep = separator))
            else:
                if lessons[lesson].get("room"):
                    print("\t{time} {sep} {lesson_name} в кабинете {room}".format(
                                time = time_from_sched(lessons[lesson]),
                                sep = separator,
                                lesson_name = lessons[lesson]["name"],
                                room = stylize(lessons[lesson]["room"], room_style)
                            )
                        )
                else:
                    print("\t{time} {sep} {lesson_name}".format(
                            time = time_from_sched(lessons[lesson]),
                            sep = separator,
                            lesson_name = lessons[lesson]["name"],
                        )
                    )
        if include_non_academ:
            if day.get("items_extday"):
                print(stylize("\n Внеакадем: \n", non_academ_style))
                for curriculum in day["items_extday"]:
                    print("\t{time} {sep} {name}".format(
                        time = time_from_sched(curriculum),
                        sep =  separator, 
                        name = curriculum["name"])
                    )
            else:
                print(stylize("\n Внеакадем отсутствует\n", non_academ_style))
    

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
        list_schedule(current_student.get_schedule())
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
