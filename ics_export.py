# coding=utf-8

from ics import Calendar, Event
import PyInquirer as pq
import os

from eljur import *


def convert_to_ics(eljur_date, eljur_time):
    # "20190909", "08:30:00_09:10:00" to '2019-09-09 08:30:00', '2019-09-09 09:10:00'

    year = eljur_date[:4]
    month = eljur_date[4:6]
    day = eljur_date[6:]

    start_eljur_time, end_eljur_time = eljur_time.split("_")

    start_eljur_time, end_eljur_time = start_eljur_time.split(":"), end_eljur_time.split(":")

    start_time = "{year}-{month}-{day} {hour}:{min}:{sec}".format(year=year, month=month, day=day,
                                                                  hour=start_eljur_time[0], min=start_eljur_time[1],
                                                                  sec=start_eljur_time[2])
    end_time = "{year}-{month}-{day} {hour}:{min}:{sec}".format(year=year, month=month, day=day, hour=end_eljur_time[0],
                                                                min=end_eljur_time[1],
                                                                sec=end_eljur_time[2])

    return start_time, end_time


def export_lessons(schedule, path):
    lessons_calendar = Calendar()

    for day in schedule["days"]:
        day = schedule["days"][day]

        lessons = day["items"]

        for lesson in lessons:
            lesson_event = Event()
            lesson_event.name = lessons[lesson].get("name")
            lesson_event.location = lessons[lesson].get("room")

            lesson_event.begin, lesson_event.end = convert_to_ics(day["name"], lessons_time[lesson])

            lessons_calendar.events.add(lesson_event)

    os.chdir(path)

    str_calendar = str(lessons_calendar)
    str_calendar = str_calendar.replace("00Z", "00")

    with open("exported_lessons.ics", 'w') as calendar_file:
        calendar_file.writelines(str_calendar)


def export_curriculum(schedule, path):
    curriculum_calendar = Calendar()

    for day in schedule["days"]:
        day = schedule["days"][day]
        if day.get("items_extday") is not None:
            for curriculum in day["items_extday"]:
                curriculum_event = Event()

                curriculum_event.name = curriculum["name"]
                curriculum_event.begin, curriculum_event.end = convert_to_ics(day["name"],
                                                                              curriculum["starttime"] + "_" +
                                                                              curriculum["endtime"])

                curriculum_calendar.events.add(curriculum_event)

            os.chdir(path)

            str_calendar = str(curriculum_calendar)
            str_calendar = str_calendar.replace("00Z", "00")

            with open("exported_curriculum.ics", 'w') as calendar_file:
                calendar_file.writelines(str_calendar)


def export_schedule(schedule):
    answers = pq.prompt(
        [
            {
                'type': 'checkbox',
                'message': "Файлы для эккспорта: ",
                'name': 'files_to_export',
                'choices': [
                    {
                        'name': 'Уроки',
                        'value': "exported_lessons.ics"
                    },
                    {
                        'name': 'Внеакадемы',
                        'value': 'exported_curriculum.ics'
                    }
                ]
            }
        ]
    )

    path_prompt = [
        {
            'type': 'input',
            'name': 'path',
            'message': 'Куда вы хотие экспортировать (Введите полный путь)',
            'default': os.path.expanduser('~') + '/Documents/'
        }
    ]

    files = answers['files_to_export']

    if len(answers['files_to_export']) == 1:

        confirmed = pq.prompt(
            {
                "type": "confirm",
                "name": "confirmed",
                "message": "Будет экспортирован 1 файл: {0}. Продолжть?".format(files[0])
            }
        )["confirmed"]

        if not confirmed:
            return "Экспорт отменён"

        answers['path'] = pq.prompt(path_prompt)['path']

        if files == ['exported_lessons.ics']:
            export_lessons(schedule, answers['path'])

        elif files == ['exported_curriculum.ics']:
            export_curriculum(schedule, answers['path'])

    elif len(answers['files_to_export']) == 2:
        confirmed = pq.prompt(
            {
                "type": "confirm",
                "name": "confirmed",
                "message": "Будет экспортированно 2 файла: {0}, {1}. Продолжть?".format(files[0], files[1])
            }
        )["confirmed"]

        if not confirmed:
            return "Экспорт отменён"

        answers['path'] = pq.prompt(path_prompt)['path']

        export_lessons(schedule, answers['path'])
        export_curriculum(schedule, answers['path'])

    else:
        return "Экспорт отменён"

    return "Файлы успешно экспортированны"
