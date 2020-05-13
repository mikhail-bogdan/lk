from flask import Flask
from flask import render_template

from requests import get, post
from json import loads
from time import localtime

from config import CFG


app = Flask(__name__, static_folder='static')

@app.route('/')
def mainPage():
    data = {'_username' : "st43026", '_password' :"UH7phwwsx7"}
    r = get("https://pro.guap.ru/user/login")
    cookies = r.cookies
    r = post("https://pro.guap.ru/user/login_check", data=data, cookies=cookies)
    cookies = r.history[0].cookies.get_dict()
    cookies.update(r.history[2].cookies.get_dict())
    data = {'iduser' : "17398"}
    r = post("https://pro.guap.ru/get-student-tasksdictionaries/", data=data, cookies=cookies)
    data = loads(r.text)['tasks']
    
    output = ""
    output += ""
    for d in data:
        if d['harddeadline'] == None or d['reportRequired'] == "0": continue
        time = localtime()
        year, mon, day = time.tm_year, time.tm_mon, time.tm_mday
        date = d['harddeadline'].split('-')
        if int(date[0]) < year or int(date[1]) < mon or int(date[2]) < day: continue
        output += '<div style="border-colords;border-color: red;border-style: solid;border-width: thin; padding: 0.4%;"><div style="width: 30%; display: inline-block">'
        output += d['subject_name']
        output += '</div><div style="width: 30%; display: inline-block">'
        output += d['name']
        output += '</div><div style="width: 30%; display:inline-block">'
        output += str(d['harddeadline'])
        output += '</div></div>\n'
    return output
    
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
