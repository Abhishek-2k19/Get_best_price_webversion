'''
This is main program which will take url for keeping
track of price of your favourite product and it will
plot its price history plot  
Author : Abhishek-2k19 (Abhishek S. Purohit)
Date : 29th June 2021
'''

# from itertools import product
from flask import Flask, render_template,request

import validators
from bs4 import BeautifulSoup
import requests
# import smtplib
import datetime
import os
import csv
# import time

import pandas as pd
import plotly.express as px
import glob
import plotly.graph_objects as go

import urllib.parse

from werkzeug.utils import redirect

app = Flask(__name__)

def store_price(prod_name,price,url):
    path = "./"+prod_name.replace(' ','_')+".csv"
    if not os.path.exists(path):
        with open("./Database.csv",'a') as file:
            writer = csv.writer(file,lineterminator ="\n")
            entry = [url,prod_name]
            writer.writerow(entry)

        with open(path,'w') as file:
            writer = csv.writer(file,lineterminator ="\n")
            headings = ["Timestamps", "price(INR)"]
            writer.writerow(headings)

    with open(path,'a') as file:
        writer = csv.writer(file,lineterminator ="\n")
        timestamp = f"{datetime.datetime.date(datetime.datetime.now())} , {datetime.datetime.time(datetime.datetime.now())}"
        writer.writerow([timestamp,price])
        print("Added entry to csv file")

def check_price(url):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}

    webpage = requests.get(url, headers = headers)

    bs = BeautifulSoup(webpage.content,'html.parser')
    
    prod_name = bs.find('span',{"class":"B_NuCI"}).get_text()
    price = (float)(bs.find("div",{"class":"_30jeq3 _16Jk6d"}).get_text()[1:].replace(',',''))

    print(prod_name)
    return price,prod_name

@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method=='POST':
        # if request.form['target_url']==' ':
        #     return render_template('index.html')
        valid = validators.url(request.form['target_url'])
        if valid==True:
            price,product = check_price(request.form['target_url'])
            store_price(product,price,request.form['target_url'])
            # return render_template('product.html',product = product,price = price )
            return redirect('/'+product.replace(' ','_'))
        else:
            return render_template('alert.html')

    return render_template('index.html')

@app.route('/<product>')
def prod_page(product):
    # print(urllib.parse.unquote(product))
    prod = glob.glob(urllib.parse.unquote(product)+".csv",recursive=True)
    print(prod[0])

    filename = prod[0]
    
    df = pd.read_csv(filename)

    fig = go.Figure([go.Scatter(x=df['Timestamps'], y=df['price(INR)'],fill='tozeroy')],)
    fig.update_xaxes(title = "Timeline",showticklabels = False)
    fig.update_yaxes(title = "Price")
    fig.update_layout(title = filename[:-4])
    fig.show()
    return render_template('come_again.html')

@app.route('/updateDatabase')
def update():
    with open('./Database.csv','r') as f:
        data_entry = csv.reader(f)
        for entry in data_entry:
            price,product = check_price(entry[0])
            path = "./"+product.replace(' ','_')+".csv"
            with open(path,'a') as file:
                writer = csv.writer(file,lineterminator ="\n")
                timestamp = f"{datetime.datetime.date(datetime.datetime.now())} , {datetime.datetime.time(datetime.datetime.now())}"
                writer.writerow([timestamp,price])
    
    return "Successfully updated all the csv files!"




if __name__ == "__main__":
    app.run(debug=False)
