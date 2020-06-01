from flask import Flask
from flask import render_template

from requests import get, post
from json import loads
from time import localtime, sleep
from datetime import datetime, timedelta
from threading import Thread
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from config import CFG

global data
global prev_time
global log_file

log_file = open("log.txt", mode='w')

prev_time = datetime.now()

app = Flask(__name__, static_folder='static')

months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
          'декабря']


@app.route('/')
def mainPage():
    global data  # '<meta name="viewport" content="width=device-width, initial-scale=1">' \

    output = '<head>' \
             '<title>Задания с дедлайнами</title>' \
             '<meta charset="utf-8">' \
             '<link rel="icon" type="image/png" href="/static/favicon.png" sizes="48x48">' \
             '<link rel="stylesheet" type="text/css" href="/static/styles.css">' \
             '<script src="/static/functions.js"></script>' \
             '</head>' \
             '<body><div class="task">' \
             '<div class="name"><big><b>Название предмета</b></big></div>' \
             '<div class="subject"><big><b>Название задания</b></big></div>' \
             '<div class="deadline"><big><b>Дедлайн</b></big></div>' \
             '</div>'

    for d in data:
        output += '<div class="inner-task">' \
                  '<div class="name">'
        output += d['subject_name']
        output += '</div><div class="subject">'
        output += d['name']
        output += '</div><div class="deadline">'
        output += str(d['day']) + " " + months[d['month'] - 1]
        output += '</div><div class="but" onclick="onClick(this)">' \
                  '<i>Показать описание</i>' \
                  '</div><div class="additional">'
        if d['hash'] is not None:
            output += '<a href="https://pro.guap.ru/get-task/' + str(d['hash']) + '">Доп. материалы</a>'
        else:
            output += 'Нет'
        output += '</div><div class= "desc" style="display: none"><b>Описание задания: </b>'
        output += d['description']
        output += '</div></div>\n'
    output += '</body>'
    return output


def mysort(data):
    out = []
    i = 0
    while i < len(data):  ## Задача об удалении нескольких элементов не решается циклом for each!
        d = data[i]
        if d['harddeadline'] is None or d['reportRequired'] == "0":
            data.remove(d)
        else:
            time = localtime()
            year, mon, day = time.tm_year, time.tm_mon, time.tm_mday
            date = d['harddeadline'].split('-')
            # print(date[0] + " " + str(year) + " " + date[1] + " " + str(mon) + "  " + date[2] + " " + str(day) + d['name'])
            if int(date[0]) < year:
                data.remove(d)
            elif int(date[0]) == year and int(date[1]) < mon:
                data.remove(d)
            elif int(date[0]) == year and int(date[1]) == mon and int(date[2]) < day:
                data.remove(d)
            else:
                tmp = {}
                tmp['id'] = d['id']
                tmp['reportRequired'] = d['reportRequired']
                tmp['year'] = int(date[0])
                tmp['month'] = int(date[1])
                tmp['day'] = int(date[2])
                tmp['subject_name'] = d['subject_name']
                tmp['name'] = d['name']
                tmp['hash'] = d['hash']
                tmp['description'] = "Без описания"
                out.append(tmp)
                i += 1

    for i in range(len(out)):
        for j in range(len(out)):
            if j > i:
                if out[i]['year'] > out[j]['year']:
                    myswap(out, i, j)
                else:
                    if out[i]['year'] == out[j]['year'] and out[i]['month'] > out[j]['month']:
                        myswap(out, i, j)
                    else:
                        if out[i]['year'] == out[j]['year'] and out[i]['month'] == out[j]['month'] and out[i]['day'] > \
                                out[j]['day']:
                            myswap(out, i, j)
    return out


def myswap(data, i, j):
    tmp = data[i]
    data[i] = data[j]
    data[j] = tmp


def getTasksData():
    global data
    user_data = {'_username': "st43026", '_password': "UH7phwwsx7"}
    r = get("https://pro.guap.ru/user/login")
    cookies = r.cookies
    r = post("https://pro.guap.ru/user/login_check", data=user_data, cookies=cookies)
    cookies = r.history[0].cookies.get_dict()
    cookies.update(r.history[2].cookies.get_dict())
    request_data = {'iduser': "17398"}
    r = post("https://pro.guap.ru/get-student-tasksdictionaries/", data=request_data, cookies=cookies)
    data = loads(r.text)
    data = mysort(data['tasks'])

    request_data = {'task_id': ""}
    for d in data:
        request_data['task_id'] = d['id']
        r = post("https://pro.guap.ru/get-student-task/" + d['id'], data=request_data, cookies=cookies)
        r_data = loads(r.text)['task'][0]
        if r_data['description'] != "":
            d['description'] = r_data['description']


class GetTasksDataThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            getTasksData()
            now = datetime.now()
            now_date = localtime(now.timestamp())
            global prev_time
            time = now - prev_time
            global log_file
            log_file.write("METHOD CALL: GetTasksData  " + str(now_date.tm_mday) + "d " + str(
                now_date.tm_hour) + "h  Delta: " + str(time.seconds // 60) + "m " + str(time.seconds % 60) + "s\n")
            log_file.flush()
            prev_time = now
            sleep(600)


vk_bot_key = "3d1ddcc235deef2ef79ec09e6bebbfa2d2342711838ccac4a02b6f62895b2d79558af020684138d503514"


class VkBotThread(Thread):
    def __init__(self, vk_bot_key):
        Thread.__init__(self)
        self.vk_session = vk_api.VkApi(token=vk_bot_key)
        self.api = self.vk_session.get_api()
        self.longPoll = VkBotLongPoll(self.vk_session, 195828373)

    def run(self):
        try:
            global data
            for event in self.longPoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    # print(event.obj.text)

                    if event.obj.text == "Описание":
                        if "payload" in event.obj:
                            for d in data:
                                if d['id'] == event.obj.payload:
                                    message = "Предмет: " + d['subject_name'] + "\nНазвание задания: " + d[
                                        'name'] + "\nДедлайн: "
                                    message += str(d['day']) + " " + months[d['month'] - 1]
                                    message += "\nОписание: " + d['description']

                                    self.api.messages.send(user_id=event.obj.from_id, random_id=get_random_id(),
                                                           message=message)
                            continue

                    if event.obj.text != "Узнать дедлайны":
                        keyboard = VkKeyboard()
                        keyboard.add_button('Узнать дедлайны', color=VkKeyboardColor.PRIMARY)
                        keyboard.add_openlink_button('Web версия', "http://lifeiscode.ru")
                        self.api.messages.send(user_id=event.obj.from_id, random_id=get_random_id(),
                                               message="Бот, который подскажет дедлайны по заданиям в личном кабинете",
                                               keyboard=keyboard.get_keyboard())
                        continue

                    # print('Новое сообщение:')
                    # print('Для меня от: ', end='')
                    # print(event.obj.from_id)
                    # print('Текст:', event.obj.text)
                    # print()

                    for d in data:
                        keyboard = VkKeyboard(one_time=False, inline=True)
                        keyboard.add_button("Описание", VkKeyboardColor.PRIMARY, d['id'])

                        message = "Предмет: " + d['subject_name'] + "\nНазвание задания: " + d['name'] + "\nДедлайн: "
                        message += str(d['day']) + " " + months[d['month'] - 1]

                        self.api.messages.send(user_id=event.obj.from_id, random_id=get_random_id(),
                                               message=message, keyboard=keyboard.get_keyboard())
        except BaseException as e:
            log_file.write(str(e) + "\n")
            log_file.write(str(e.__class__) + "\n")
            log_file.flush()
            log_file.close()
            exit(0)


def create_threads():
    VkBotThread(vk_bot_key).start()
    GetTasksDataThread().start()


create_threads()

app.secret_key = CFG['secret_key']
app.run(host='0.0.0.0', port=CFG['port'], debug=CFG['debug'])
