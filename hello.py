# -*- coding: utf-8 -*-
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def post():
    name = request.form.get('name')
    # return render_template('index.html')
    print(name)
    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run()