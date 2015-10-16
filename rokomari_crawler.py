# __author__ == __saleh__

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
from pprint import pprint

from pymongo import MongoClient

client = MongoClient()
db = client.boipotro_final
collection = db.boipotro_collection_new
boipotro_info_new = db.boipotro_info_new



#This is a function to get soup from an url
def make_soup(url):
    data = requests.get(url)
    content = data.text.encode("utf8", "ignore")
    soup = BeautifulSoup(content)
    return soup


#This is a function to find all category url
def get_category_urls(soup):
    for link in soup.findAll('a'):
        links = link.get('href')
        if "category" in links:
            #print links
            #li = links.replaceAll(";jsessionid=.*?(?=\\?|$)", "")
            index = links.index(';')
            url = main_url + links[:index]
            category_urls.append(url)


#This is a function to get a content
def get_content(url):
    data = requests.get("url")
    content = data.text.encode("utf8", "ignore")
    content = content.replace("\r", "")
    content = content.replace("\n", "")
    content = content.lower()
    return content


#This is a function for getting specific book_url
def get_book_url(soup):
    for link in soup.findAll('a'):
        links = link.get('href')
        if "book" in links:
            index = links.index(';')
            url = main_url + links[:index]


#get all category urls from rokomari.com
def get_categories(category_urls, main_url):
    with open('rokomari_categories.json') as data_file:
        data = json.load(data_file)

    cat = data["rokomari_categories"]

    for item in cat:
        category = item['category']
        sub_cat = item["sub_categories"]
        for item in sub_cat:
            sub_category = item['category']
            #print item["_id"]
            url = main_url + str(item["cat_id"])
            temp = [category, sub_category, url]
            category_urls.append(temp)


#database for rokomari
def get_db():
    from pymongo import MongoClient

    client = MongoClient()
    db = client.boipotro_db
    return db


#This is the main function
def main():
    home_url = "http://rokomari.com"
    main_url = "http://rokomari.com/category/"
    category_urls = []

    get_categories(category_urls, main_url)

    for url in category_urls:
        page_no = 1

        while True:
            sub_url = url[2] + "?page=" + str(page_no)
            print sub_url
            # break
            soup = make_soup(sub_url)
            for link in soup.findAll('a', attrs = {"class" : "lnk-bok"}):
                links = link['href']

                book_info = {}


                index = links.index(';')
                book_url = home_url + links[:index]
                book_info["book_url"] = book_url

                #now find the book name
                soup2 = make_soup(book_url)
                #print book_url
                book_title = soup2.find('div', attrs={"class": "gen-div fnt-15"})
                print type(book_title.text.strip())
                print "Book Name is: %s" % book_title.text.strip()
                book_info["book_name"] = book_title.text.strip()


                #Now find the writer name
                writer_name = soup2.find('div', attrs={"class": "gen-div-2 fnt-10"}).text.strip()
                print type(writer_name)
                a = writer_name.replace("\t","").replace("\r", "").replace("\n", "")
                list = a.split(',')
                book_info["writer"] = list
                for item in list:
                    print item

                #another method for finding writer name print soup.find("table",attrs = {"class":"tb-spec fnt-1"}).a.text.strip()
                #now find the book's rating
                rat = soup2.findAll("div", attrs={"name": "sRaty"})
                rat = str(rat)
                rating = re.search(r'\d.\d', rat)
                if rating:
                    print float(rating.group())
                    book_info["rating"] = float(rating.group())

                '''rating = soup2.find('div', attrs = {"class":"float-left margin-top-4"}).text.strip()
                match = re.findall(r'\d',rating)

                rat_rev=[0,0]
                index = 0
                for rat in match:
                    #rat = int(rat)
                    rat_rev[index] = rat
                    index += 1
                print "rating is %s" %rat_rev[0]
                print "review is %s" %rat_rev[1]'''

                #find the book's previous price
                try:
                    prev_price = soup2.find("span", attrs={"class": "float-left fnt-prev-price"}).text
                    match = re.search(r'\d+', prev_price)
                    if match:
                        print "previous price is: %s" % match.group()
                        book_info["previous_price"] = match.group()

                except Exception as e:
                    print e.message


                #find the book's current price
                cur_price = soup2.find("span", attrs={"class": "float-left fnt-cur-price-2"}).text
                match = re.search(r'\d+', cur_price)
                if match:
                    print "Current price is: %s" % match.group()
                    book_info["current_price"] = match.group()


                #find the book's image url
                soup2 = make_soup(book_url)
                img_link = soup2.find("div", attrs={"class": "det-a1"})
                print "Image url is: %s" % img_link.img['src']
                book_info["image_url"] = img_link.img['src']


                #find the publisher's name
                pub = soup2.findAll("a")
                for item in pub:
                    try:
                        if "publisher" in item.get('href'):
                            print item.text.strip()
                            book_info["publisher"] = item.text.strip()
                    except Exception as e:
                        print e.message

                soup2 = make_soup(book_url)
                for item in soup2.findAll("td"):
                    if "Edition" in item:
                        print item.text.strip(), ":", item.find_next("td").text
                        book_info["edition"] = item.find_next("td").text

                    if "No of Pages" in item:
                        print item.text.strip(), ":", item.find_next("td").text.strip()
                        book_info["no_of_pages"] = item.find_next("td").text.strip()

                    if "Country" in item:
                        print item.text.strip(), ":", item.find_next("td").text.strip()
                        book_info["country"] = item.find_next("td").text.strip()

                    if "Language" in item:
                        print item.text.strip(), ":", item.find_next("td").text.strip()
                        book_info["language"] = item.find_next("td").text.strip()

                    if "ISBN" in item:
                        print item.text.strip(), ":", item.find_next("td").text.strip()
                        book_info["isbn"] = item.find_next("td").text.strip()

                    if "Author" in item:
                        author =  item.find_next("td").text.strip()
                        a = author.replace("\t","").replace("\r", "").replace("\n", "")
                        list2 = a.split(',')
                        for item in list2:
                            print item
                        book_info["author"] = list2




                for item in soup2.findAll("span"):
                    if "Availability:" in item.text:
                        print item.text.strip(), ":", item.find_next("span").text.strip()
                        book_info["availability"] = item.find_next("span").text.strip()



                book_info["store"] = "rokomari"
                book_info["category"] = url[0]
                book_info["sub_category"] = url[1]

                print "yes----------------sssssssssssssssss"
                id = boipotro_info_new.save(book_info)  #inserting data in monogodb database collection name as boipotro_info_new

                print id
                pprint(book_info)




            #print sub_url
            data = requests.get(sub_url)
            content = data.text.encode("utf8", "ignore")

            content = content.replace("\r", "")
            content = content.replace("\n", "")
            content = content.lower()
            match = re.search(r'<span class="disabled">next', content)
            if match:
                break
            else:
                page_no += 1


if __name__ == "__main__":

    while True:
        print datetime.date.today()

        print "crawler started yes"

        main()

        print "owao!!! crawl completed"
        print "Going to sleep for 48 hours ta ta..."

        for i in ["/", "-", "|", "\\", "|"]:
            print "%s\r" % i,

        time.sleep(48 * 60 * 60)