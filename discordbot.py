# インストールした discord.py を読み込む
import discord
from discord.ext import tasks

import os

import datetime
import pytz

#from config import *
from discord_ID import *
from schedule_calc import schedule_calc
from fish_dict import fish_dict

#ローカル用
#from discord_token import DISCORDPY_TOKEN

#heroku デプロイ用
DISCORDPY_TOKEN = os.environ['DISCORDPY_TOKEN']

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():

    # 現在の時刻
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    #秒以下を0埋め
    now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)

    #テスト用
    #now = datetime.datetime(2021, 10, 5, 10, 13)
    print(now)

    channel = client.get_channel(CHANNEL_ID_MENTION)

    async def send_Notice(fishing_date, role_ID, minutes_ago):
        date_ago = fishing_date - datetime.timedelta(minutes=minutes_ago)

        #現在時刻がx分前だった場合に通知
        if now == date_ago:
            await channel.send('<@&' + str(role_ID) + '> ' + str(minutes_ago) + '分前\n' + fishing_date.strftime('%Y/%m/%d (%a) %H:%M'))    


    for value in fish_dict.values():
        
        fishing_date = schedule_calc(value['name_EN'])[0]

        #30分前
        await send_Notice(fishing_date, value['role_ID'], 30)
        #15分前
        await send_Notice(fishing_date, value['role_ID'], 15)
        #5分前
        await send_Notice(fishing_date, value['role_ID'], 5)


#ループが始まる前に、clientの準備が整うまで待機する
@loop.before_loop
async def before_loop():
    print('waiting...')
    await client.wait_until_ready()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):

    guild = client.get_guild(SERVER_ID)

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    #登録
    if message.channel.id == CHANNEL_ID_REGISTER:

        for v in fish_dict.values():

            if message.content == '!' + v['name_JA']:
                role = guild.get_role(v['role_ID'])
                
                if role in message.author.roles:
                    await message.author.remove_roles(role)
                    await message.reply(v['name_JA'] + 'のタイマーをOFFにしました')
                else:
                    await message.author.add_roles(role)
                    await message.reply(v['name_JA'] + 'のタイマーをONにしました')


    
    #スケジュール
    if message.channel.id == CHANNEL_ID_SCHEDULE:

        for v in fish_dict.values():

            if message.content == '!' + v['name_JA']:
                msg = v['name_JA'] + ' スケジュール\n'
                msg += '```'
                fishing_dates = schedule_calc(v['name_EN'])

                for fishing_date in fishing_dates:
                    #TODO Herokuに日本語のロケールがないので、曜日を日本語にするなら独自の関数を実行する必要がある
                    msg += fishing_date.strftime('%Y/%m/%d(%a) %H:%M') + '\n'
            
                msg += '```'
                await message.reply(msg)


#ループ処理実行
loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(DISCORDPY_TOKEN)