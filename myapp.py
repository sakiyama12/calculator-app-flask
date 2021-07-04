# -*- coding: utf-8 -*-
import json
import os
import re

from flask import Flask, render_template, redirect, request, session 

application = Flask(__name__)
application.secret_key = 'secret'

DATA_FILE = 'clacdata.json'

# 計算機能
def calc_data(formula, button):
    """入力式を演算します
    :param formula:　これまで入力された演算式
    :type formula: str
    :param button: 押しされたボタン
    :type button: str
    :return: None
    """
    
    SYMBOL = ["*","+","-","/","%","."]
    ans = ""
    
    if button == '=':
        if formula[-1:] in SYMBOL: # 記号の場合、記号より前で計算
            formula = formula[:-1]

        if re.findall(r"/0", formula) != []:
            zero1 =  len(re.findall(r"/0", formula))
            zero2 = len(re.findall(r"/0.\d+", formula))
            if zero1 != zero2:
                ans = "ERROR"
            else:
                ans = '= ' + str(eval(formula))
        else:
            ans = '= ' + str(eval(formula))
    elif button == 'AC': #クリアの場合
        formula = ''
    elif button == '+/-': # 正負符号の場合
        formula = str(eval(formula)) + "*(-1)"
    elif button in SYMBOL: # 記号の場合
        if formula[-1:] not in SYMBOL and formula[-1:] != '':
            formula += button
        elif formula[-1:] in SYMBOL: # 記号の場合入れ替える
            formula = formula[:-1] + button
    else: #数字などの場合
        formula += button
    
    res = [formula,ans]

    return res

# 計算履歴保存・表示
def save_data(res):
    """記録データを保存します
    :param res: [これまで入力された演算式,演算結果]
    :type res: list
    :return: None
    """

    if res[1] != "":
        try:
            # jsonモジュールでデータベースファイルを開きます
            database = json.load(open(DATA_FILE, mode="r", encoding="utf-8"))
        
        except FileNotFoundError:
            database = []

        database.insert(0, {
            "formula": res[0],
            "result": res[1]
        })

        json.dump(database, open(DATA_FILE, mode="w", encoding="utf-8"), indent=4, ensure_ascii=False)

#計算式更新
def get_formula(res):
    """計算式を更新します
    :param res: [計算式,計算結果]
    :type res: list
    :param res[0]:　計算式
    :type res[0]: str
    :param res[1]: 計算結果
    :type res[1]: str
    :return: None
    """
    if res[1] == '':
        formula = res[0]
    # else:
    #     formula = ""
    return formula

#def get_string(button):


def load_data():
    """記録データを返します"""
    try:
        # jsonモジュールでデータベースを開きます
        database = json.load(open(DATA_FILE, mode="r", encoding="utf-8"))
    except FileNotFoundError:
        database = []
    return database


@application.route('/')
def index():
    """トップページテンプレートを使用してページを表示します"""
    # 記録データを読み込みます
    calcs = load_data()
    return render_template('index.html', calcs=calcs)

@application.route('/save', methods=['GET'])
def save():
    """記録用URL"""
    # 入力から計算します
    button = request.args.get('button') # ボタン
    session.permanent = True  # <--- makes the permanent session

    if button != "":
        if "formula" in session: #sessionにユーザー情報があったとき
            formula = session['formula']
        else:
            formula = ""
        
        result = calc_data(formula, button)
        # 計算式と結果を保存します
        save_data(result)

        # 記録データを読み込みます
        calcs = load_data()

        if button == "=":
            session['formula'] = ""
            return render_template('index.html', formula=result[0], result=result[1], calcs=calcs)

    session['formula'] = result[0]
    return render_template('index.html', formula=result[0], result=result[1], calcs=calcs)

@application.route('/delete', methods=['POST'])
# 履歴削除
def remove_data():
    # リセットボタンが押されたら、jsonデータを全削除する
    button = request.form.get("delete") # ボタン
    if button != "":
        os.remove(DATA_FILE)
    return redirect('/')


if __name__ == '__main__':
    # IPアドレス0.0.0.0の8000番ポートでアプリケーションを実行します
    application.run('0.0.0.0', 8000, debug=True)