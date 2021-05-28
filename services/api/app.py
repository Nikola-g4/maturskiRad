# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from random import randint, choice, shuffle
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True
socketio = SocketIO(app, cors_allowed_origins = '*')

listaTema = ['stolica','lampa','gitara','balon','crkva','golub','kaktus','zmaj','paprika','violina','grabulja', 'zvono', 'truba', 'tastatura', 'ruka', 'prozor', 'konj', 'raskrsnica', 'osmeh', 'zmija']
sobaIndeks = {} #{idSobe: indeks}
sobaRunda = {} #{idSobe: brojRunde}
sidPoeni = {} #{idSoketa: nedodeljeniPoeni}
poSobama = {} #{idSobe: [idSoketa, idSoketa...]}
poSid = {} #{idSoketa: [imeIgraca, brojPoena, brojSobe]}
curReadyOf = {} #{idSobe: [brojSpremnih, brojIgraca]}
helper = True

def proveriOdgovor(poruka, soba):
    if listaTema[sobaIndeks[soba]] == poruka.lower():
        return True
    return False

def igraciUSobi(roomID, ukljucujuciSebe, socketID=0):
    pom1 = poSobama[roomID]
    pom2 = []
    for i in pom1:
        if ukljucujuciSebe or i != socketID:
            pom2.append([poSid[i][0], poSid[i][1]])
    return pom2

def izdvojCrtaca(roomId, IdCrtaca, karakter):
    pom1 = poSobama[roomId]
    pom2 = []
    for i in pom1:
        if i==IdCrtaca:
            pom2.append([karakter + poSid[i][0], poSid[i][1]])
        else:
            pom2.append([poSid[i][0], poSid[i][1]])
    return pom2

def najbolji(roomId):
    maks = 0
    igrac = ''
    for i in poSobama[roomId]:
        if poSid[i][1] > maks:
            maks = poSid[i][1]
            igrac = i
    return igrac

@socketio.on('addMe')
def newUser(l):
    poSid[request.sid] = [l[0], 0, l[1]]
    if not l[1] in poSobama:        
        poSobama[l[1]] = [request.sid]
        curReadyOf[l[1]] = [0, 1]
    else:
        poSobama[l[1]].append(request.sid)
        curReadyOf[l[1]][1] += 1
    join_room(l[1])
    pom = igraciUSobi(l[1], True)
    sidPoeni[request.sid] = 0
    emit('newPlayer', pom, to=l[1])

@socketio.on('disconnect')
def delUser():
    pom1 = poSid[request.sid][2] #idSobe
    pom2 = igraciUSobi(pom1, False, request.sid)
    poSobama[pom1].remove(request.sid)
    poSid.pop(request.sid)
    curReadyOf[pom1][1] -= 1
    #TODO: Slucaj ako izadje igrac koji je bio spreman
    if len(poSobama[pom1]) == 0:
        sobaIndeks.pop(pom1)
        sobaRunda.pop(pom1)
        curReadyOf.pop(pom1)
        poSobama.pop(pom1)
    emit('newPlayer', pom2, to=pom1)

@socketio.on('coordinates')
def hello(p):
    if helper == True:
        emit('coordinates', p, to=poSid[request.sid][2], include_self=False)

@socketio.on('begin')
def begin(p):
    emit('begin', p, to=poSid[request.sid][2], include_self=False)

@socketio.on('end')
def end():
    helper = False

@socketio.on('beginconfirm')
def confirmation():
    helper = True

@socketio.on('switchColor')
def color(col):
    emit('switchColor', col, to=poSid[request.sid][2], include_self=False)

@socketio.on('clear')
def clear():
    emit('clear', to=poSid[request.sid][2])

@socketio.on('message')
def message(msg):
    pom1 = poSid[request.sid][2] #idSobe
    pom2 = poSid[request.sid][0] #imeIgraca
    if curReadyOf[pom1][0] == curReadyOf[pom1][1] and proveriOdgovor(msg, pom1) and request.sid != poSobama[pom1][sobaIndeks[pom1] % len(poSobama[pom1])]:
        sidPoeni[request.sid] += 150
        emit('sendMessage', [pom2, 'je pogodio!'], to=pom1)
    else:
        emit('sendMessage', [pom2, msg], to=pom1)


@socketio.on('readyUp')
def ready():
    pom1 = poSid[request.sid][2] #idSobe
    curReadyOf[pom1][0] += 1
    if curReadyOf[pom1][0] == curReadyOf[pom1][1] and len(poSobama[pom1]) > 1:
        pom2 = randint(0, len(listaTema) - 1)
        crtac = pom2 % len(poSobama[pom1])
        pom3 = poSobama[pom1][crtac]
        emit('newPlayer', izdvojCrtaca(pom1, pom3, '🖌'), to=pom1)
        sobaIndeks[pom1] = pom2
        sobaRunda[pom1] = 1
        emit('eReady', listaTema[pom2], room=pom3)


def dodeliPoene(soba, idCrtaca):
    pom = 0
    for i in poSobama[soba]:
        if sidPoeni[i] > 0:
            pom += 1
        poSid[i][1] += sidPoeni[i]
        sidPoeni[i] = 0
    poSid[idCrtaca][1] += pom * 95
    



@socketio.on('roundEnded')
def roundEnded():    
    pom1 = poSid[request.sid][2] #idSobe
    sobaRunda[pom1] += 1
    sobaIndeks[pom1] = (sobaIndeks[pom1] + 1) % len(listaTema)
    dodeliPoene(pom1, request.sid)
    emit('clearXs', to=pom1)
    clear()
    emit('clearChat', to=pom1)
    if sobaRunda[pom1] <= len(poSobama[pom1]) * 3:
        pom2 = poSobama[pom1][sobaIndeks[pom1] % len(poSobama[pom1])]
        emit('newPlayer', izdvojCrtaca(pom1, pom2, '🖌'), to=pom1)
        emit('eReady', listaTema[sobaIndeks[pom1]], room=pom2)
    else:
        emit('newPlayer', izdvojCrtaca(pom1, najbolji(pom1), '🏆'), to=pom1)


if __name__ == '__main__':
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    socketio.run(app, host=host, port=port)
