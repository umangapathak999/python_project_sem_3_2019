from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
import requests
import itertools

app = Flask(__name__)

#   https://www.dictionary.com/browse/word?s=ts

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/make-puzzle', methods=["POST"])
def make_puzzle():
    row = int(request.form['row'])
    column = int(request.form['column'])

    return render_template('makePuzzle.html', row=row, column=column)


@app.route('/get-data', methods=["POST"])
def get_data():
    dat = request.form
    row = int(request.form['row'])
    column = int(request.form['column'])
    data = []
    i=0
    j=0
    min = row*column+1;
    max=-1
    while i<row:
        j=0
        d = []
        while j<column:
            strRow = str(i)
            strColumn = str(j)
            name = strRow + strColumn
            print(name)
            d.append(int(dat[name]))
            if int(dat[name]) < min and int(dat[name]) != 0:
                min = int(dat[name])
            if max<int(dat[name]):
                max = int(dat[name])
            j = j+1
        data.append(d)
        i = i+1
    max = max+1
    return render_template('getData.html', row=row, column=column, data=data, min=min, max=max, k=0)


@app.route('/network-error')
def networkError():
    return render_template("networkError.html")


@app.route('/show-result', methods=["POST"])
def show_result():
    dat = request.form
    min = int(dat['min'])
    max = int(dat['max'])
    row = int(dat['row'])
    column = int(dat['column'])
    data = []
    val = []
    pVal = []
    i = 0
    while i < row:
        j = 0
        d = []
        while j < column:
            strRow = str(i)
            strColumn = str(j)
            name = strRow + strColumn
            d.append(int(dat[name]))
            j = j + 1
        data.append(d)
        i = i + 1
    # word finding starts:

    for i in range (min, max):
        name1 = "val" + str(i)
        name2 = "pVal" + str(i)
        val.append(dat[name1])
        pVal.append(dat[name2])

    numWord = []
    for da in data:
        word = ""
        for d in da:
            word = word + ' ' + str(d) + " "
        numWord.append(word)

    i = 0

    while i < column:
        word = ""
        j=0
        while j < row:
            word = word + ' ' + str(data[j][i]) + ' '
            j = j + 1
        numWord.append(word)
        i = i + 1

    for word in numWord:
        words = word.split(" 0 ")   # split word by delimiter ' 0 '
        if len(words) > 1:
            for w in words:
                if w != '' and len(w) > 3:
                    numWord.append(w)
            numWord.remove(word)

    words = []
    for word in numWord:
        wor = ""
        w = word.split(" ")
        for wo in w:
            if wo != "" and wo != " ":
                val1 = int(wo)
                val1 = val1 - 1
                if val1 > -1 and val[val1] != '':
                    wor = wor + val[val1]
                if val1 > -1 and val[val1] == '':
                    wor = wor + "_" + str(val1) + "_"
        words.append(wor)

    sub = 0
    for v in val:
        if v != "" and v in str(pVal):
            pVal.remove(v)
            sub = sub + 1

    for word in words:
        if len(word) <= 3:
            words.remove(word)
    pVal = list(set(pVal))
    prevWords = words.copy()
    allVal = list(itertools.permutations(pVal, len(pVal)))
    print(allVal)
    for v in allVal:
        if check(words, list(v), sub):
            words = makeWords(words, pVal, sub)
            return render_template("showResult.html", words=words)
        words = prevWords.copy()
        print(prevWords)

    return render_template("cannotSolveError.html", words=words)


def makeWords(words, pVal, sub):
    j=0
    for word in words:
        w = word.split("_")
        i=0
        for x in w:
            if w == "":
                i = i + 1
                continue
            try:
                val = int(x)
            except:
                i = i + 1
                continue
            w[i] = pVal[val-sub]
            i = i + 1
        words[j] = ''.join(w)
        j = j+1
    return words


def check(words, pVal, sub):
    j=0
    print("word")
    print(words)
    prevWords = words
    for word in words:
        w = word.split("_")
        i=0
        for x in w:
            if w == "":
                i = i + 1
                continue
            try:
                val = int(x)
            except:
                i = i + 1
                continue
            w[i] = pVal[val-sub]
            i = i + 1
        words[j] = ''.join(w)
        j = j+1
    for word in words:

        page_link = 'https://www.phpspellcheck.com/phpspellcheck/core/?note=&command=CTXSPELL&args=' + word.lower() + '&lan=English%20%28International%29&sender=0&settingsfile=default-settings'
        page_response = requests.get(page_link, timeout=100)
        page_content = BeautifulSoup(page_response.content, "html.parser")
        print(page_content)
        if "F" in str(page_content):
            words = prevWords
            print(words)
            return False
    return True


if __name__ == '__main__':
    app.run(debug=True)
