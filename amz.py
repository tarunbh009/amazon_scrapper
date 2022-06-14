from flask import Flask,request,render_template,jsonify
from bs4 import BeautifulSoup as bs
import requests
from flask_cors import CORS,cross_origin
from urllib.request import urlopen as uReq
import time


app=Flask(__name__)

@app.route('/',methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')

@app.route('/review',methods=['GET','POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString=request.form['content'].replace(" ","")
            amazon_url="https://www.amazon.in/s?k="+searchString
            uClient=uReq(amazon_url)
            amazon_page=uClient.read()
            uClient.close()

            amazon_html=bs(amazon_page,'html.parser')
            bigboxes=amazon_html.find_all('div',{'class':'sg-col sg-col-4-of-12 sg-col-8-of-16 sg-col-12-of-20 s-list-col-right'})
            box=bigboxes[0].div.div.div.a
            productLink="https://www.amazon.in/"+box['href']
            prodRes = requests.get(productLink)

            prodRes.encoding='utf-8'
            prod_html=bs(prodRes.text,'html.parser')

            commentboxes=prod_html.find_all('div',{'class':'a-section review aok-relative'})


            filename=searchString+".csv"
            fw=open(filename,"w")
            headers="product,customer name,rating,heading,comment,\n"
            fw.write(headers)
            reviews=[]
            for commentbox in commentboxes:
                try:
                    name = commentbox.find_all('span', {'class': 'a-profile-name'})[0].text
                except:
                    name = 'No Name'

                try:
                    rating = commentbox.find_all('div', {'class': 'a-row'})[2].text[0]
                except:
                    rating = 'no rating'

                try:
                    cust_heading = commentbox.find_all('a', {'data-hook': 'review-title'})[0].text.replace("\n", "")
                except:
                    cust_heading = 'No heading'
                try:
                    cust_comment = commentbox.find_all('div', {'data-hook': 'review-collapsed'})[0].text.replace("\n", "")
                except:
                    cust_comment = "No comment"

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": cust_heading,
                          "Comment": cust_comment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print('The Exception message is:',e)
            return("something is wrong")
    else:
        return render_template('index.html')
if __name__=='__main__':
    app.run(debug=True)











