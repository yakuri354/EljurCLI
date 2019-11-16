from ics import Calendar, Event
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

    os.chdir(os.path.expanduser("~") + "/Documents/")

    with open(path, 'w') as calendar_file:
        calendar_file.writelines(lessons_calendar)


def export_curriculum(schedule, path):
    curriculums_calendar = Calendar()

    for day in schedule["days"]:
        day = schedule["days"][day]
        if day.get("items_extday") is not None:
            for curriculum in day["items_extday"]:
                curriculum_event = Event()

                curriculum_event.name = curriculum["name"]
                curriculum_event.begin, curriculum_event.end = convert_to_ics(day["name"],
                                                                              curriculum["starttime"] + "_" +
                                                                              curriculum["endtime"])

                curriculums_calendar.events.add(curriculum_event)

            os.chdir(os.path.expanduser("~") + "/Documents/")

            with open(path, 'w') as calendar_file:
                calendar_file.writelines(curriculums_calendar)
