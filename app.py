import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True
import requests
from bs4 import BeautifulSoup
import datetime

time = datetime.datetime.now()
url = 'https://www.oddsshark.com/nba/consensus-picks'

def parse_home_away_tags(tag):
    ret={}
    ret['name'] = tag(class_='name')[0].text
    ret['consensus-percent'] =tag(class_='consensus-percent')[0].text
    ret['consensus-spread'] =tag(class_='consensus-spread')[0].text
    ret['consensus-price'] =tag(class_='consensus-price')[0].text
    ret['ou-percent'] =tag(class_='ou-percent')[0].text
    ret['ou-price'] =tag(class_='ou-price')[0].text
    ret['ou-total'] = tag(class_='ou-total')[0].text if tag(class_='ou-total') else ''
    # print(ret)
    return ret
def combine_two_tags_into_match(tag1,tag2):
    teamStr= time.strftime('%Y / %m / %d %X ') + '\n'+ tag1['name']+ ' vs \n'+ tag2['name']
    oddsInfo = '讓分盤:'+ "\n" + \
    tag1['name'] + " 讓分： "+tag1['consensus-spread'] + " 賠率："+ tag1['consensus-price'] + '\n' +\
    tag2['name'] + " 讓分： "+tag2['consensus-spread'] + " 賠率："+ tag2['consensus-price'] + '\n'+ \
    '高低分盤  '+ \
    tag1['ou-total'][3:] + '分'+ '\n' + \
    '高分賠率:' + tag1['ou-price'] + '\n'+ \
    '低分賠率:' + tag1['ou-price'] 

    consensus_info = '大數據分析 「共識統計勝率」:' + "\n\n" + \
        '客隊 '+tag1['name']+'  : ' + tag1['consensus-percent'] + '\n' \
        '主隊 '+tag2['name']+'  : ' + tag2['consensus-percent']+ '\n\n' + \
        '高分 : ' + tag1['ou-percent'] + '\n'+\
        '低分 : ' + tag2['ou-percent'] + '\n'
    return teamStr + '\n\n' + oddsInfo + '\n\n' +consensus_info

def compose_str(info_items):
    retList=[]
    for i in info_items:
        ret=''
        home_tag = i.contents[0].tbody.contents[1]
        away_tag = i.contents[0].tbody.contents[0]
        home_tag = parse_home_away_tags(home_tag)
        away_tag = parse_home_away_tags(away_tag)
        # ret+="########################################### \n"
        ret+=combine_two_tags_into_match(away_tag,home_tag)
        retList.append(ret)
    return retList



@app.route('/', methods=['GET'])
def home():
    response = requests.get(url=url)
    soup = BeautifulSoup(response.text, 'html')
    info_items = soup.find_all('div', 'consensus-matchup')
    dataList = compose_str(info_items) 
    lineUrl = 'https://notify-api.line.me/api/notify'
    token='0GSJOPkkVKhsjb3RUuetuG8A6csVTvLgTHz9CfmvLT6'
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    } 
    
    for i in dataList:
        payload = {'message': i}
        r = requests.post(lineUrl , headers = headers, params = payload)
        print(r.status_code)
    return "<h1>:D</h1>"


app.run(port=5000)