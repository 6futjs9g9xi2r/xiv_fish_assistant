from EorzeaEnv import EorzeaLang
from EorzeaEnv import EorzeaTime
from EorzeaEnv import EorzeaWeather

from decimal import Decimal, ROUND_HALF_UP

import datetime
import pytz

import LT_list

def schedule_calc(fish):

    #天候を取得する量
    step = 7000

    Eorzea_time = EorzeaTime.now()

    #天候が変わってからLTでどれだけ経過したか
    elapsed_LT = int(Decimal(str((Eorzea_time.hour % 8 * 175 + Eorzea_time.minute * 2.917) / 60)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)) #丸めた

    #現在の天候に変化した時刻を基準時間とする
    base_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo')) - datetime.timedelta(minutes=elapsed_LT)

    #秒以下を0埋め
    base_time = datetime.datetime(base_time.year, base_time.month, base_time.day, base_time.hour, base_time.minute)

    #朝昼夜の算出
    term = 'term0'
    term_list = []

    if Eorzea_time.hour < 8:
        term = 'Morning'
        term_list = ['Morning', 'Day', 'Night']
    elif Eorzea_time.hour < 16:
        term = 'Day'
        term_list = ['Day', 'Night', 'Morning']
    else:
        term = 'Night'
        term_list = ['Night', 'Morning', 'Day']

    #朝昼夜のリスト作成
    term_list = term_list * int(step / 3)

    #天候の取得時、0番目は1つ前の天候が格納されるため、それに対応
    term_list.insert(0, 'term0')

    #1分誤差の対応
    plus_one_minute = base_time + datetime.timedelta(minutes=1)
    minus_one_minute = base_time - datetime.timedelta(minutes=1)

    #丸めが原因で1分誤差が出る場合があるので±1で場合分けをして調整
    if [str(base_time.hour),str(base_time.minute).zfill(2),term] in LT_list.LT_list:
        pass
    elif [str(plus_one_minute.hour),str(plus_one_minute.minute).zfill(2),term] in LT_list.LT_list:
        base_time = plus_one_minute
    elif [str(minus_one_minute.hour),str(minus_one_minute.minute).zfill(2),term] in LT_list.LT_list:
        base_time = minus_one_minute
    else:
        #TODO エラー処理
        print('err')
        print(base_time)
        print(term)
        print(plus_one_minute)
        print(minus_one_minute)

    #天候の取得
    t = tuple(EorzeaTime.weather_period(step=step))


    dates=[]

    #検索(紅龍)...i分後
    if fish == 'The Ruby Dragon':
        weather = EorzeaWeather.forecast('The Ruby Sea', t, strict=True)

        for i in range(step):
            if weather[i-1] == 'Thunder' and weather[i] == 'Clouds' and term_list[i] == 'Morning':

                d, h, m = calc_minute_after(i, term)

                date = base_time + datetime.timedelta(days=d,hours=h,minutes=m)

                dates.append(date)

        return dates

    #検索(イラッド・スカーン)...i分後
    elif fish == 'Ealad Skaan':
        weather = EorzeaWeather.forecast('Il Mheg', t, strict=True)

        for i in range(step):
            if weather[i-1] == 'Thunderstorms' and weather[i] == 'Clear Skies' and term_list[i] == 'Night':

                d, h, m = calc_minute_after(i, term)

                #ET23:00からなので21分後
                m += 21

                date = base_time + datetime.timedelta(days=d,hours=h,minutes=m)

                dates.append(date)

        return dates

    #検索(サプライズエッグ)...i分後
    elif fish == 'Cinder Surprise':
        weather = EorzeaWeather.forecast('Amh Araeng', t, strict=True)

        for i in range(step):
            if weather[i-1] == 'Dust Storms' and weather[i] == 'Heat Waves' and term_list[i] == 'Morning':

                d, h, m = calc_minute_after(i, term)

                date = base_time + datetime.timedelta(days=d,hours=h,minutes=m)

                dates.append(date)

        return dates

def calc_minute_after(i, term):
    #ET8時間は23分20秒だが、簡略化するために朝23/昼23/夜24で計算する
    calc_minutes = (i - 1) * 23 + (i - 1) // 3 

    #計算スタートが昼・夜だった場合1分調整
    if term == 'Day' or term == 'Night':
        calc_minutes += 1

    d = calc_minutes // 60 // 24
    h = calc_minutes // 60 % 24
    m = calc_minutes % 60
    return d, h, m
