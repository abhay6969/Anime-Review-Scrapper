from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as ureq
import logging
import pymongo


client = pymongo.MongoClient("mongodb+srv://Abhay_Tripathi:abhay6969@cluster0.icrof6w.mongodb.net/?retryWrites=true&w=majority")
db = client.test
collection = db['Records']

logging.basicConfig(filename="scrapper.log",level=logging.INFO)
app = Flask(__name__)

@app.route("/",methods = ["GET"] )
def homepage():
    return render_template("index.html")

@app.route("/review",methods = ["POST","GET"])
def index():
    if request.method == "POST":
        try:
            search = request.form['content']
            searchString = request.form['content'].replace(" ","")
            mal = "https://myanimelist.net/search/all?q=" + searchString
            uclient = ureq(mal)
            mal_page =  uclient.read()
            uclient.close()
            mal_html = bs(mal_page,'html.parser')
            bigbox = mal_html.find_all("div",{"class":"title"})
            box = bigbox[0]
            p_link = box.a['href']
            p_req = requests.get(p_link)
            p_text = p_req.text
            p_html = bs(p_text,'html.parser') 
            print(p_html)
            re_box = p_html.find_all('div',{"class":"review-element js-review-element"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            header ="Anime Name,Customer Name,Feelings,Comments \n"
            fw.write(header)
            reviews = []
            for i in re_box:
                try:
                    name = i.div.find_all('div',{"class":"username"})[0].text
                    b = len(name)
                    name = a[1:b-1]
                except:
                    logging.info("name")
                
                try:
                    feelings = i.div.find_all("div",{"class","tags"})[0].text
                except:
                    feelings = "No Comments"
                    logging.info(feelings)
                
                try:
                    comments = i.div.find_all("div",{"class":"text"})[0].text
                    comments =comments.replace("\n","").replace("\r","").replace("--","")
                    comments.strip()
                    comments = comments[0:1200]
                except:
                    comments = "No Comments"
                    logging.info(comments)
                
                my_dict = {"anime" : search, "commentor name" : name, "Recommendation": feelings, "comment":comments}

                reviews.append(my_dict)
            logging.info("log my final result {}".format(reviews))
            collection.insert_many(reviews)
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            logging.info(e)
            return "Something is Wrong"

    else:
        return render_template('index.html')

if __name__=="__main__":
    app.run(host="0.0.0.0")





