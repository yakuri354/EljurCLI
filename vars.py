from colored import fg, stylize, attr

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

greeting = stylize("""
    ╭────────────────────────────────────────────────────────────────╮
    │ Добро пожаловать в                                             │
    │             _____ _  _             ____ _     ___              │
    │            | ____| |(_)_   _ _ __ / ___| |   |_ _|             │
    │            |  _| | || | | | | '__| |   | |    | |              │
    │            | |___| || | |_| | |  | |___| |___ | |              │
    │            |_____|_|/ |\__,_|_|   \____|_____|___|             │
    │                   |__/                                         │
    │ вер. 0.1                                                       │
    ╰────────────────────────────────────────────────────────────────╯

""", fg("magenta"), attr("bold"))

API_URL = "https://markbook.eljur.ru/apiv3/"
DEVKEY = "9235e26e80ac2c509c48fe62db23642c"
VENDOR = "markbook"

lessons = []

time_style = fg("green") + attr("bold")
room_style = fg("yellow") + attr("bold")
day_of_week_style = fg("orange_1") + attr("bold")

non_academ_style = fg("cyan")

separator_style = fg("medium_purple_1") + attr("bold")
separator = stylize("::", separator_style)

# Yakuri354 - Для обозначения времени окон
# Butukay - Я бы назвал это костылём
# yakuri354 ~> ну я согласен, но а как ещё окна отображать

lessons_time = {1: "08:30:00_09:10:00", 2: "09:30:00_10:10:00", 3: "10:20:00_11:00:00", 4: "11:10:00_11:50:00",
                5: "12:00:00_12:40:00", 6: "13:30:00_14:10:00", 7: "14:20:00_15:00:00", 8: "15:10:00_15:50:00",
                9: "16:20:00_17:00:00", 10: "17:10:00_17:50:00", 11: "18:00:00_18:40:00"}


