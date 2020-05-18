from flask import Flask
from flask import render_template

from requests import get, post
from json import loads
from time import localtime
from threading import Timer

from config import CFG

global data

app = Flask(__name__, static_folder='static')

months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

@app.route('/')
def mainPage():
    global data ##'<meta name="viewport" content="width=device-width, initial-scale=1">' \

    output = '<head>' \
             '<title>Задания с дедлайнами</title>' \
             '<meta charset="utf-8">' \
             '<link rel="icon" type="image/png" href="/static/favicon.png" sizes="48x48">' \
             '<link rel="stylesheet" type="text/css" href="/static/styles.css">' \
             '<script src="/static/functions.js"></script>' \
             '</head>'\
             '<div class="task">' \
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
    return output

def mysort(data):
    out = []
    i = 0
    while i < len(data):
        d = data[i]
        if d['harddeadline'] is None or d['reportRequired'] == "0":
            data.remove(d)
        else:
            time = localtime()
            year, mon, day = time.tm_year, time.tm_mon, time.tm_mday
            date = d['harddeadline'].split('-')
            if int(date[0]) < year or int(date[1]) < mon or int(date[2]) < day:
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
                    if out[i]['month'] > out[j]['month']:
                        myswap(out, i, j)
                    else:
                        if out[i]['day'] > out[j]['day']:
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

Timer(60, getTasksData).start()

print("Loading...")
getTasksData()
print("Loaded!")


app.secret_key = CFG['secret_key']
app.run(host='0.0.0.0', port=CFG['port'], debug=CFG['debug'])

##data = {'_username' : "st43026", '_password' :"UH7phwwsx7"}
##r = get("https://pro.guap.ru/user/login")
##cookies = r.cookies
##r = post("https://pro.guap.ru/user/login_check", data=data, cookies=cookies)
##cookies = r.history[0].cookies.get_dict()
##cookies.update(r.history[2].cookies.get_dict())
##data = {'iduser' : "17398"}
##r = post("https://pro.guap.ru/get-student-tasksdictionaries/", data=data, cookies=cookies)
##data = loads(r.text)['tasks']
##
