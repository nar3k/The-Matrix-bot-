# -*- coding: utf-8 -*-

import telebot
import re
import sys, urllib, getopt, requests
from bs4 import BeautifulSoup
from config import *

__author__ = 'narek'

token = 'ENTER KEY HERE'


def google_the_best_answer(search_string):
    #googling the best answer on stackoverflow :)
    google_begin = "http://google.com/search?&rls=en&q="
    google_end = "&ie=UTF-8&oe=UTF-8"
    stack_overflow_ = '+site:http://stackoverflow.com/questions'
    search_string = search_string.replace('+','%2B')
    search_string = search_string.replace(' ','+')
    full_search_string = google_begin+search_string+stack_overflow_+google_end
    best_res = requests.get(full_search_string, verify=False)
    #parsing the google page
    soup = BeautifulSoup(best_res.text,'html.parser')
    answers = soup.find_all('div',class_='g')
    try:
        #getting stackoverflow page
        pattern = 'http.+'
        range_len = 3
        anwers_len = len(answers)
        url_list = [0]*range_len
        for index in range(range_len):
            if index < anwers_len:
                url_list[index] = re.findall(pattern, answers[index].a.get('href'))[0]
        url_list = [url for url in url_list if url !=0]
        url_list_len = len(url_list)
        answer_list = [0]*url_list_len
        #giving the best result
        for index in range(url_list_len):
            answer_list[index] = get_best_answer_and_vote_count(url_list[index])
        answer_list = [answer for answer in answer_list if answer !=0]
        answer_list.sort(key=lambda x:x[0],reverse=False)
        return answer_list[0][1]
    except IndexError:
            return "Some error has been occured..." #change to msg


def get_best_answer_and_vote_count(url):
    #giving the best result ( just the first one as we know that stackoverflow is already sorted)
    best_res = requests.get(url, verify=False)
    try :
        soup = BeautifulSoup(best_res.text,'html.parser')
        answer_soup = soup.find_all('div',class_='answer')[0]
        answer_text = answer_soup.find('div',class_='post-text').text
        post_count = int(answer_soup.find("span", class_= "vote-count-post ").text)

        return post_count,answer_text
    except:
        return 0

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
Hi. I'm The Matrix. I can help to write code faster.
Just ask me what to find. For example

<code>loop through two arrays python</code>

<em>I'm getting better and better everyday.
So for any questions contact</em> @nar3k
""",parse_mode='HTML')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    result = google_the_best_answer(message.text)
    #this just a wpapper that sends multople messages if the answer lenght exceeds a 4000
    n = len(result)
    k = int(round(5000/4000 + .5,0))
    if n > 4000:
        for i in range(k):
            start = int((n*i)/k)
            end = int((n*(i+1))/k-1)
            bot.send_message(message.chat.id,result[start:end+1])
    else:
        bot.send_message(message.chat.id, result)


bot.polling()
