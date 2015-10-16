import re
import time
import requests
from bs4 import BeautifulSoup
import os
import sys
import json
from pprint import pprint
import datetime
import pymongo
from pymongo import MongoClient

client = MongoClient()
db = client.boipotro_final


import rokomari_categories
#This is a function to get soup from an url

def make_soup(url):
    data = requests.get(url)
    content = data.text.encode("utf8", "ignore")
    soup = BeautifulSoup(content)
    return soup




#This is a function to get  content
def get_content(url):
    data = requests.get("url")
    content = data.text.encode("utf8", "ignore")
    content = content.replace("\r", "")
    content = content.replace("\n", "")
    content = content.lower()
    return content


#This is a function to find all category url

def get_category_urls(soup):
    for link in soup.findAll('a'):
        links = link.get('href')
        if "category" in links:
            #print links
            #li = links.replaceAll(";jsessionid=.*?(?=\\?|$)", "")
            index = links.index(';')
            url = main_url+links[:index]
            category_urls.append(url)

def get_categories(category_urls):

    with open('karigor_categories.json') as data_file:
        data = json.load(data_file)


    cat = data["karigor_categories"]

    for item in cat:
        category =  item['category']
        sub_cat = item["sub_categories"]
        for item in sub_cat:
            sub_cat =  item['category']
            #print item["_id"]
            url = item["url"]
            temp = [category, sub_cat, url]
            category_urls.append(temp)




def main():

    category_urls = []
    get_categories(category_urls)

    for category in category_urls:
        page_no = 1

        while True:
            sub_url = category[2] + "&paged=" + str(page_no)
            soup = make_soup(sub_url)

            books = soup.findAll("a")
            count = 1
            for item in books:

                book_info = {}
                if "product=" in item.get('href'):
                    book_info["book_url"] = item.get('href')
                    print item.get('href')
                    soup2 = make_soup(item.get('href'))
                    b =  soup2.find("h1", attrs = {"class" : "product_title entry-title"})
                    print "book name is %s " %b.text
                    book_info["book_name"] = b.text


                    writer_name = soup2.find("a", attrs = {"rel" : "tag"}).text
                    print "Writter name is: %s " %writer_name
                    book_info["writer_name"] = writer_name

                    publisher = soup2.findAll("a", attrs = {"rel" : "tag"}, limit = 2)
                    for item in publisher:
                        print item.text
                        book_info["publisher_name"] = item.text

                    prev_price = soup2.find("del")
                    p = prev_price.text
                    p = p.split(".")
                    print p[0]
                    book_info["previous_price"] = p[0]

                    cur_price = soup2.find("ins")
                    c= cur_price.text
                    c = c.split(".")
                    print c[0]
                    book_info["current_price"] = c[0]

                    img_link = soup2.find("img", attrs = {"class": "attachment-shop_single wp-post-image"})
                    print "Image url is: %s" %img_link['src']
                    book_info["thumbnail"] = img_link['src']

                    try:
                        isbn = soup2.find("span", attrs = {"class" : "sku"})
                        print isbn.text
                        book_info["isbn"] = isbn.text
                    except Exception as e:
                        print e.message

                    image = soup2.find("a", attrs = {"class" : "zoom first"})
                    print image['href']
                    book_info["image"] = image['href']


                    book_info["category"] = category[0]
                    book_info["sub_category"] = category[1]
                    book_info["store"] = "book_karigor"


                    id = db.boipotro_info_new.save(book_info)
                    #book_info["object_id"] = id
                    pprint(book_info)

                    count += 1
                    if count>12:
                        break


            data = requests.get(sub_url)
            content = data.text.encode("utf8", "ignore")
            #content = content.decode("utf")

            content = content.replace("\r", "")
            content = content.replace("\n", "")
            content = content.lower()
            match = re.search(r'>Next', content)
            if match:
                page_no += 1
                print "next page is going"
            else:
                break



if __name__ == "__main__":

    while True:
        print datetime.date.today()

        print "karigor crawler started......"

        main()

        print "owao!!! crawl completed"
        print "Going to sleep for 48 hours ta ta..."

        for i in ["/", "-", "|", "\\", "|"]:
            print "%s\r" % i,

        time.sleep(48 * 60 * 60)