# -*- coding: utf-8 -*-

import tweepy
import webbrowser
import configparser
import random
from websocket_server import WebsocketServer
import time
import os

consumer_key = ''
consumer_secret = ''
callback_url = 'oob'

tweet_send_cnt = 0
random_list = []
tweet_list_text = []
random_list = []
relast_id = '0'
relast_id_tmp = ''
checkid = ''
checkid_loop = 0
checkid_sw = 0


searchword_loop_cnt = 0
searchword_loop_cnt_tmp = 0

main_config = configparser.ConfigParser()
main_config.read('data/ini/config.ini', encoding='utf-8')

os.system('title OBS-Twitter-Stream v' + main_config.get('MainConfig', 'ver'))

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
        'OAuth2_sw': 1,
        'ver': main_config.get('MainConfig', 'ver')
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

def search_word_api(search_word_def, si):

    tweet_list = []

    global searchword_loop_cnt
    global relast_id
    global checkid_sw

    searchword_loop_cnt = 0

    if si == '0':
        tweets = api.search(q = search_word_def  + ' -filter:retweets', result_type = 'recent', count = random.randint(10,50), include_entities = False)
    else:
        #前回取得したツイートより最新のツイートを取得する
        tweets = api.search(q = search_word_def  + ' -filter:retweets', result_type = 'recent', count = random.randint(5,10), include_entities = False, since_id = si)

    for result in tweets:
        if searchword_loop_cnt == 0:
            relast_id = result.id_str

        tweet_list.append(result.text +' (@'+ result.user.name +')')
        searchword_loop_cnt += 1

    return tweet_list

def checkid_relast(search_word_def):

    relast_id_return = ''

    tweets = api.search(q = search_word_def  + ' -filter:retweets', result_type = 'recent', count = 1, include_entities = False)

    for result in tweets:
        relast_id_return = result.id_str

    return relast_id_return

#JSと接続
def new_client(client, server):

    global tweet_send_cnt
    global random_list
    global tweet_list_text
    global random_list
    global checkid
    global relast_id
    global relast_id_tmp

    tweet_send_cnt = 0
    tweet_list_text = []
    random_list = []

    tweet_list_text = search_word_api(search_word, '0')
    relast_id_tmp = relast_id
    checkid = relast_id

    print('\nConnection is complete\n接続が完了しました\n')
    time.sleep(1)
    server.send_message(client, '接続完了')

#JSから切断
def client_left(client, server):
    print('\nDisconnected.\n切断されたため終了します\n')

#JSからのメッセージ受信
def message_received(client, server, message):

    global tweet_send_cnt
    global random_list
    global tweet_list_text
    global random_list
    global searchword_loop_cnt
    global relast_id
    global checkid
    global checkid_loop
    global checkid_sw
    global relast_id_tmp

    #JSからRTの送信が来た場合ツイートを送る
    if message == 'RT':

        #searchword_loop_cnt = 0 は取得できるツイートが存在しない
        if searchword_loop_cnt != 0:

            #すべてのツイートストックを送信し終えた
            if tweet_send_cnt == searchword_loop_cnt:
                time.sleep(0.5)

                tweet_send_cnt = 0
                tweet_list_text = []
                random_list = []

                #idを指定してにツイートを取得
                tweet_list_text = search_word_api(search_word, relast_id)

                #前回取得したツイートより最新のツイートが存在する場合
                if relast_id_tmp != relast_id:
                    relast_id_tmp = relast_id

                    checkid = relast_id
                    checkid_loop = 0

                    while True:
                        random_int = random.randint(0,searchword_loop_cnt -1)
                        if random_int not in random_list:
                            server.send_message(client, tweet_list_text[random_int])
                            checkid_loop += 1
                            break

                    random_list.append(random_int)
                    tweet_send_cnt += 1

                #前回取得したツイートより最新のツイートが存在しない場合
                else:

                    tweet_send_cnt = 0
                    tweet_list_text = []
                    random_list = []
                    checkid_loop = 0

                    #idを指定せずにツイートを取得
                    tweet_list_text = search_word_api(search_word, '0')

                    while True:
                        random_int = random.randint(0,searchword_loop_cnt -1)
                        if random_int not in random_list:
                            server.send_message(client, tweet_list_text[random_int])
                            checkid_loop += 1
                            break

                    random_list.append(random_int)
                    tweet_send_cnt += 1

            #まだ未送信のツイートがある
            else:

                #5回目のループで最新のツイートがあるかidを取得
                if checkid_loop >= 5:
                    checkid = checkid_relast(search_word)
                    checkid_loop = 0

                #取得したidを検証/最新のものであれば強制再取得
                if checkid != relast_id:
                    searchword_loop_cnt = tweet_send_cnt + 1

                while True:
                    random_int = random.randint(0,searchword_loop_cnt -1)
                    if random_int not in random_list:
                        server.send_message(client, tweet_list_text[random_int])
                        checkid_loop += 1
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
