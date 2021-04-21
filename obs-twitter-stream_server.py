# -*- coding: utf-8 -*-

import tweepy
import webbrowser
import configparser
import random
from websocket_server import WebsocketServer
import time
import os

os.system('title OBS-Twitter-Stream')

consumer_key = ''
consumer_secret = ''
callback_url = 'oob'

tweet_send_cnt = 10
random_list = []
tweet_list_text = []
random_list = []
relast_id = 0

searchword_loop_cnt = 0

main_config = configparser.ConfigParser()
main_config.read('data/ini/config.ini', encoding='utf-8')

if main_config.get('MainConfig', 'OAuth2_sw') == '0':

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)

    auth_url = auth.get_authorization_url()
    webbrowser.open(auth_url)

    verifier = input('\nPlease authenticate your account and get a PIN\nアカウントを認証してPINを取得してください\nPIN: ').strip()
    auth.get_access_token(verifier)

    auth.set_access_token(auth.access_token, auth.access_token_secret)

    main_config['TwitterAPI'] = {
        'access_token': auth.access_token,
        'access_token_secret': auth.access_token_secret
    }

    main_config['MainConfig'] = {
        'OAuth2_sw': 1
    }

    with open('data/ini/config.ini', 'w') as cw:
        main_config.write(cw)

else:

    access_token = main_config.get('TwitterAPI', 'access_token')
    access_token_secret = main_config.get('TwitterAPI', 'access_token_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)

    auth.set_access_token(access_token, access_token_secret)


api = tweepy.API(auth, wait_on_rate_limit=True)

screen_name = api.me().screen_name
print('\nThe following users have been authenticated\n以下のユーザーが認証されました\n@' + screen_name + '\n')

search_word = input('\nPlease enter a search word\n検索ワードを入力してください\n').strip()

print('\n')

def search_word_api(search_word_def):

    tweet_list = []
    global searchword_loop_cnt
    searchword_loop_cnt = 0

    tweets = api.search(q = search_word_def  + ' -filter:retweets', result_type = 'recent', count = 10, include_entities = False)

    for result in tweets:
        if searchword_loop_cnt == 0:
            relast_id = result.id

        tweet_list.append(result.text +' (@'+ result.user.name +')')
        searchword_loop_cnt += 1

    return tweet_list

search_word_api

def new_client(client, server):

    global tweet_send_cnt
    global random_list
    global tweet_list_text
    global random_list

    tweet_send_cnt = 10
    random_list = []
    tweet_list_text = []
    random_list = []

    print('\nConnection is complete\n接続が完了しました\n')
    time.sleep(2)
    server.send_message(client, '接続完了')

def client_left(client, server):
    print('\nDisconnected.\n切断されたため終了します\n')

def message_received(client, server, message):

    global tweet_send_cnt
    global random_list
    global tweet_list_text
    global random_list
    global searchword_loop_cnt

    if message == 'RT':

        if searchword_loop_cnt != 0:

            if tweet_send_cnt == 10:
                time.sleep(0.5)

                tweet_send_cnt = 0
                tweet_list_text = []
                random_list = []

                tweet_list_text = search_word_api(search_word)

                while True:
                    random_int = random.randint(0,searchword_loop_cnt -1)
                    if random_int not in random_list:
                        server.send_message(client, tweet_list_text[random_int])
                        break

                random_list.append(random_int)
                tweet_send_cnt += 1

            else:

                while True:
                    random_int = random.randint(0,searchword_loop_cnt -1)
                    if random_int not in random_list:
                        server.send_message(client, tweet_list_text[random_int])
                        break

                random_list.append(random_int)
                tweet_send_cnt += 1

        else:

            print('ツイートが存在しません\nテストツイートを行い、しばらくしてからページを再読込してください')

server = WebsocketServer(port=10356)

server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)

server.run_forever()
