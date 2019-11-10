from googleapiclient.discovery import build
from login import google_login, eljur_login
from colored import fg, stylize, attr
import requests as rq
import datetime

primary_calendar_id = "yakuri2006@gmail.com"
eljur_calendar_id = "6sorgqebejho8m0cpof065eja8@group.calendar.google.com"
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
devkey = "9235e26e80ac2c509c48fe62db23642c"
apiurl = "https://markbook.eljur.ru/apiv3/"
include_non_academ = "true"
student_id = "6461"
today = datetime.datetime.now().__str__()[:10]
print(today)
lessons = []
time_style = fg("green") + attr("bold")
separator_style = fg("medium_purple_1") + attr("bold")
nonacadem_style = fg("red")
separator = stylize("::", separator_style)

token = eljur_login()
# creds = google_login()


rules_params = {"devkey": devkey, "out_format": "json",
                "auth_token": token, "vendor": "markbook"}

time_sort = {10: "08:30:00_09:10:00", 20: "09:30:00_10:10:00", 30: "10:20:00_11:00:00", 40: "11:10:00_11:50:00",
             50: "12:00:00_12:40:00", 60: "13:30:00_14:10:00", 70: "14:20:00_15:00:00", 80: "15:10:00_15:50:00",
             90: "16:20:00_17:00:00", 100: "17:10:00_17:50:00", 110: "18:00:00_18:40:00"}


class Lesson_Event:
    def __init__(self, date, time, TZ="Europe/Moscow"):
        self.tz = "+03:00"
        self.date = date
        self.starttime, self.endtime = time.split("_")

    def __date_to_google_format(self):
        self.date.replace("-", "")
        self.date += "T"

    def start_google_format(self):
        self.__date_to_google_format()
        return self.date + self.starttime + self.tz

    def end_google_format(self):
        self.__date_to_google_format()
        return self.date + self.endtime + self.tz


class Student:
    def __init__(self):
        pass


def output_time(time):
    start, end = time.split("_")
    start = start[:5]
    end = end[:5]
    return start + "-" + end

response = rq.get(apiurl + "getrules", params=rules_params)["response"]
result = response["result"]

# service = build('calendar', 'v3', credentials=creds)
# calendar = service.calendars().get(calendarId=primary_calendar_id).execute()
# events = service.events().list(calendarId=primary_calendar_id).execute()

diary_params = {"student": student_id, "days": "20191104-20191109", "rings": include_non_academ,
                "devkey": devkey, "out_format": "json",
                "auth_token": token, "vendor": "markbook"}

diary = rq.get(apiurl + "getschedule", params=diary_params).json()['response']
if diary["error"] is not None:
    print("Error: " + diary["error"])
    raise ValueError
schedule = diary['result']['students'][str(student_id)]
for d in schedule["days"]:
    d = schedule["days"][d]
    current_schedule = d
    print("\n" + d["title"] + " \n")
    for i in range(len(current_schedule["items"]) + 1):
        if i == 0:
            continue
        if not current_schedule["items"].get(str(i)):
            print("     {0} {1} Окно!".format(stylize(output_time(time_sort[i * 10]), time_style), separator))
            continue
        i = current_schedule["items"][str(i)]
        if not i.get("starttime"):
            if i["room"] != "":
                print("     {0} {1} {2} в кабинете {3}".format(
                    stylize(output_time(time_sort[int(i["sort"])]), time_style), separator, i["name"], i["room"]))
                # print(Lesson_Event(today, time_sort[int(i["sort"])]).start_google_format())
            else:
                print("     {0} {1} {2}".format(stylize(output_time(time_sort[int(i["sort"])]), time_style), separator,
                                                i["name"]))
        else:
            if i["room"] != "":
                print("     {0} {1} {2} в кабинете {3}".format(
                    stylize(output_time(i["starttime"] + "_" + i["endtime"]), time_style), separator, i["name"],
                    i["room"]))
                # print(Lesson_Event(today, time_sort[int(i["sort"])]).start_google_format())
            else:
                print("     {0} {1} {2}".format(stylize(output_time(i["starttime"] + "_" + i["endtime"]), time_style),
                                                separator, i["name"]))
    if current_schedule.get("items_extday"):
        print(stylize("\n Внеакадем:\n", nonacadem_style))
        for v in range(len(current_schedule["items_extday"])):
            v = current_schedule["items_extday"][v]
            print("     {0} {1} {2}".format(stylize(output_time(v["starttime"] + "_" + v["endtime"]), time_style),
                                            separator, v["name"]))
    else:
        print(stylize("\n Внеакадем отсутствует", nonacadem_style))
