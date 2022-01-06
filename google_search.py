# -*- coding: utf-8 -*-
from logging import shutdown
from bs4 import BeautifulSoup
import re
from flask import Flask, render_template, request, session
import requests
import pprint
import json
from requests.exceptions import Timeout
# 返却された検索結果の読み取りにつかう
from googleapiclient.discovery import build # APIへのアクセスにつかう
# import session

# =================================
# =================================
app = Flask(__name__)


# =================================
# =================================
# カスタム検索エンジンID
CUSTOM_SEARCH_ENGINE_ID = "87dabc623cf5e8624"
# API キー
API_KEY = "AIzaSyBQN-iwelbXSw10cHPGMN5Tny78wCud2ro"

# APIにアクセスして結果をもらってくるメソッド
def get_search_results(query):
    
    # APIでやりとりするためのリソースを構築
    # 詳細: https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-pysrc.html#build
    search = build(
        "customsearch", 
        "v1", 
        developerKey = API_KEY
    )
    
    # Google Custom Search から結果を取得
    # 詳細: https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
    result = search.cse().list(
        q = query,
        cx = CUSTOM_SEARCH_ENGINE_ID,
        lr = 'lang_ja',
        num = 5,
        start = 1
    ).execute()
    # print("{}".format(json.dumps(result,indent=4)))

    # 受け取ったjsonをそのまま返却
    return result

# 検索結果の情報をSearchResultに格納してリストで返す
def summarize_search_results(result):

    # 結果のjsonから検索結果の部分を取り出しておく
    result_items_part = result['items']

    # 抽出した検索結果の情報はこのリストにまとめる
    result_items = []
    
    # 今回は (start =) 1 個目の結果から (num =) 10 個の結果を取得した
    for i in range(0, 5):
        # i番目の検索結果の部分
        result_item = result_items_part[i]
        # i番目の検索結果からそれぞれの属性の情報をResultクラスに格納して
        # result_items リストに追加する
        s_r = SearchResult(
                title = result_item['title'],
                url = result_item['link'],
                snippet = result_item['snippet']
            )
        
        result_items.append(s_r.Making_d())

    # 結果を格納したリストを返却
    return result_items

# 検索結果の情報を格納するクラス
class SearchResult:
    def __init__(self, title, url, snippet):
        self.title = title
        self.url = url
        self.snippet = snippet

    def __str__(self):
        # コマンドライン上での表示形式はご自由にどうぞ
        return "[title] " + self.title + "\n\t[detail] " + self.snippet + "\n\t[url]" + self.url

    # def show_url(self):
    #     print(self.url)

    def Making_d(self):
        d_info = dict(title=self.title, url=self.url, detail=self.snippet)
        return d_info

# htmlとやり取りするパート

app = Flask(__name__)

app.secret_key = 'abcdefghijklmn'

@app.route('/', methods=['GET'])
def get():
    # messagebox.showinfo('タイトル', 'メッセージ内容')
    return render_template('index.html')

# イエス・ノー聞くページ *page2*
@app.route('/templates/page2', methods=["get"])
def page2():
    return render_template('page2.html')

@app.route('/templates/page2', methods=['POST'])
def post():
    name = request.form.get('name')
    prefecture = request.form.get('prefectures')
    query = name
    query2 = prefecture
    query3 = '"食べログ"'
    the_word = query + " " + query2 + " " + query3

        # APIから検索結果を取得
    result = get_search_results(the_word)
    # result には 返却されたjsonが入る

    # 検索結果情報からタイトル, URL, スニペット, 検索結果の順位を抽出してまとめる
    result_items_list = summarize_search_results(result) 
    # result_items_list には SearchResult のリストが入る

    # 他のページへ渡せるようにsessionを使う
    session['result_items_list'] = result_items_list

    
    # コマンドラインに検索結果の情報を出力
    # 1個分だけ表示
    print(result_items_list[0])
    
    print()
    print(query2)
    return render_template('page2.html', rst_info=result_items_list)

@app.route('/templates/page3', methods=["get"])
def page3():
    searched_list = session.get('result_items_list', None)
    print(searched_list[1])
    return render_template('page3.html', rst_info=searched_list)

@app.route('/templates/goal', methods=["get"])
def goal():

    searched_list = session.get('result_items_list', None)
    #↓OKが出た店の食べログURLでスクレイピング
    url_t = searched_list[0]['url']
    r = requests.get(url_t)
    soup = BeautifulSoup(r.text)
    name_rst = soup.find('div', class_='rstinfo-table__name-wrap').text
    station_rst = soup.find('span', class_='linktree__parent-target-text').text
    tel_rst = soup.find('p', class_='rstdtl-side-yoyaku__tel-number').text

    return render_template('goal.html', searched_list=searched_list, name_rst=name_rst, \
        station_rst=station_rst, tel_rst=tel_rst)

@app.route('/templates/fail', methods=["get"])
def fail():
    return render_template('fail.html')

# xxxxxxxxxxxxxxxxxxxxxxxxxx
# ここ↓はファイルの一番下に位置していること！！！
if __name__ == '__main__':
    # app.run(debug=True)
    app.debug = True
    app.run()
# xxxxxxxxxxxxxxxxxxxxxxxxxx






