from django.shortcuts import render
from django.http import HttpResponse
import json
import urllib.request
import sys

#名前を調整する関数です。
def name(nom):
  if "室" in nom:
    target = "室"
    idx = nom.find(target)
    return nom[:idx+1]
  elif "堂" in nom and "席" not in nom:
    target = "堂"
    idx = nom.find(target)
    return nom[:idx+1]
  elif "席" in nom:
    target = "席"
    idx = nom.find(target)
    return nom[:idx+1]
  else:
    return nom

def send(day, period, option):
  if option == 0:
    return ""
  if day == option or option == 6:
    if day == 1:
      return "月" + str(period) + "限 "
    if day == 2:
      return "火" + str(period) + "限 "
    if day == 3:
      return "水" + str(period) + "限 "
    if day == 4:
      return "木" + str(period) + "限 "
    if day == 5:
      return "金" + str(period) + "限 "
  else:
    return ""

def classroom(cle, option):
  class_result = ""
  for day in range(5):
    for period in range(5):
      keykey = str(day + 1) + "_" + str(period + 1)
      if keykey in cle:
        class_result = class_result + str(send(day+1, period+1, option))
  return class_result


# Create your views here.
def index(request):
    if 'want_room' in request.GET:
      option = int(request.GET['want_room'])
    else:
      option = 0

    #return HttpResponse("Hello, world. You're at the polls index.")
    #使用端末数のjsonファイルです。(当然ですが時間帯によって変化します)
    urllib.request.urlretrieve('https://wifi-monitor.nc.u-tokyo.ac.jp/map/data/ap-data2.json', 'data.json')

    #部屋の情報です。(https://wifi-monitor.nc.u-tokyo.ac.jp/map/data/ap.json に"availability"を追加したものです; しばらくは変化しないと思います)
    urllib.request.urlretrieve('https://kontonspace.web.fc2.com/komaba/ap.json', 'room.json')

    #jsonを読みます。
    json_path = open('data.json', 'r', encoding='utf-8')
    json_l = json.load(json_path)
    json_path1 = open('room.json', 'r', encoding='utf-8')
    json_room = json.load(json_path1)

    #各部屋の"合計"を計算します。(同じspace_idのルータの人数をまとめます。)
    nouveau_liste = dict()
    for value in json_l:
        flag = False
        if json_l[value]['space_id'] != 'nan' and json_l[value]['space_id'] > 200000000000: #ちなみに100000000000台は本郷です。
            for value1 in nouveau_liste:
                if nouveau_liste[value1]['space_id'] == json_l[value]['space_id']:
                    nouveau_liste[value1]['numClient'] += json_l[value]['numClient']
                    flag = True
                    break
            if not flag:
                nouveau_liste[value] = dict()
                nouveau_liste[value]['space_id'] = json_l[value]['space_id']
                nouveau_liste[value]['numClient'] = json_l[value]['numClient']

    #人数順にソート。
    nouveau_liste = sorted(nouveau_liste.items(), key=lambda x: x[1]['numClient'])

    content = "<head><title>Komaba-Wifi-List</title></head><body><form action='' method='get' class='wakaru'><select name='want_room'>"
    content = content + "<option value='0'>授業情報を非表示</option><option value='1'>月</option><option value='2'>火</option><option value='3'>水</option><option value='4'>木</option><option value='5'>金</option><option value='6'>全表示</option></select>"
    content = content.replace("value='" + str(option) + "'", "value='" + str(option) + "' selected")
    content = content + "<input type='submit' value='送信'></form><font color='#000000'>☆利用可能な教室を表示しますね!☆</font><br>"

    for value in range(len(nouveau_liste)):
        for room in json_room:
            if json_room[room]['space_id'] == nouveau_liste[value][1]['space_id']:
                if 'availability' not in json_room[room]: #"availability"がない=声出し可
                    room_name = name(json_room[room]['description'])
                    
                    if 'class' in json_room[room]:
                        content = content + "<font color='#00aa00'>" + room_name + "　</font>" + str(nouveau_liste[value][1]['numClient']) + "　<font color='#aa0000'>" + classroom(json_room[room]['class'], option) + "</font><br>"
                        break
                    else:
                        content = content + "<font color='#00aa00'>" + room_name + "　</font>" + str(nouveau_liste[value][1]['numClient']) + "<br>"
                    
                    #content = content + "<font color='#00aa00'>" + room_name + "　</font>" + str(nouveau_liste[value][1]['numClient']) + "<br>"
                    break
                elif json_room[room]['availability'] == "quiet": #静粛教室の情報
                    room_name = name(json_room[room]['description'])
                    content = content + "<font color='#aa00aa'>" + room_name + "　</font>" + str(nouveau_liste[value][1]['numClient']) + "<br>"
                    break

    content = content + "緑が<font color='#00aa00'>声出し可</font>、紫が<font color='#aa00aa'>静粛教室</font>です!"
    return HttpResponse(content)
