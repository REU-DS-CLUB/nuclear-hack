import requests
import json
import uuid
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
from openai import OpenAI
import datetime
import os
import time
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from psycopg import connect
from psycopg.rows import dict_row
import psycopg2


def max_start_and_min_date(df):
    min_data = "2024-01-01 00:00"
    max_date = "2024-04-03 00:00"
    return max_date, min_data

def get_token(auth_token, scope='GIGACHAT_API_PERS'):
    """
      Выполняет POST-запрос к эндпоинту, который выдает токен.

      Параметры:
      - auth_token (str): токен авторизации, необходимый для запроса.
      - область (str): область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».

      Возвращает:
      - ответ API, где токен и срок его "годности".
      """
    # Создадим идентификатор UUID (36 знаков)
    rq_uid = str(uuid.uuid4())

    # API URL
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Заголовки
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {auth_token}'
    }

    # Тело запроса
    payload = {
        'scope': scope
    }

    try:
        # Делаем POST запрос с отключенной SSL верификацией
        # (можно скачать сертификаты Минцифры, тогда отключать проверку не надо)
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return -1

def get_ss_token(auth_token, scope='SALUTE_SPEECH_PERS'):
    """
      Выполняет POST-запрос к эндпоинту, который выдает токен.

      Параметры:
      - auth_token (str): токен авторизации, необходимый для запроса.
      - область (str): область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».

      Возвращает:
      - ответ API, где токен и срок его "годности".
      """
    # Создадим идентификатор UUID (36 знаков)
    rq_uid = str(uuid.uuid4())

    # API URL
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Заголовки
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Bearer {auth_token}'
    }

    # Тело запроса
    payload = {
        'scope': scope
    }

    try:
        # Делаем POST запрос с отключенной SSL верификацией
        # (можно скачать сертификаты Минцифры, тогда отключать проверку не надо)
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return -1

def upload_voice(ss_token, voice):
    headers = {
    'Authorization': f'Bearer {ss_token}',
    'Content-Type': 'application/x-www-form-urlencoded',
}
    with open(voice, 'rb') as f:
        # print("--------------", voice)
        data = f.read()
        # print("---------------", data)

    response = requests.post('https://smartspeech.sber.ru/rest/v1/data:upload', headers=headers, data=data, verify=False)
    print(response)
    return response

def recognize_voice(ss_token, file_id):
    headers = {
    'Authorization': f'Bearer {ss_token}',
    'Content-Type': 'application/json',
    }
    
    data = '\n{\n  "options": {\n    "language": "ru-RU",\n    "audio_encoding": "OPUS",\n    "sample_rate": 48000,\n    "hypotheses_count": 1,\n    "enable_profanity_filter": false,\n    "max_speech_timeout": "20s",\n    "channels_count": 1,\n    "no_speech_timeout": "7s",\n    "hints": {\n        "words": ["станция", "ветка"],\n        "enable_letters": true,\n        "eou_timeout": "2s"\n    },\n    "speaker_separation_options": {\n      "enable": true, \n      "enable_only_main_speaker": false, \n      "count": 2\n    }\n  },\n  "request_file_id": "' + str(file_id) + '"\n}'
    data = data.encode()
    response = requests.post('https://smartspeech.sber.ru/rest/v1/speech:async_recognize', headers=headers, data=data, verify= False)
    return response

def get_status(ss_token, task_id):
    headers = {
    'Authorization': f'Bearer {ss_token}',
}

    response = requests.get('https://smartspeech.sber.ru/rest/v1/task:get?id='+str(task_id), headers=headers, verify=False)
    return response

def get_transcript(ss_token, response_file_id):
    headers = {
    'Authorization': f'Bearer {ss_token}',
}

    response = requests.get(
    f'https://smartspeech.sber.ru/rest/v1/data:download?response_file_id={response_file_id}',
    headers=headers, verify=False
)
    return response

def voice_to_text(voice: str):
    auth_key = "MTljNjgxNmQtNDFmOS00MjQ3LWIxMzYtYzA0ODRlZWFmOGY5Ojk0MjgwZGJkLTBmYWMtNGNhZC05NTAzLWY0NWNlZGUzOWJhYQ=="
    response = get_ss_token(auth_token=auth_key)
    # print(response)
    if (response != -1):
        ss_token = response.json()['access_token']
        response = upload_voice(ss_token=ss_token, voice=voice)
        
        if (response != -1):
            file_id = response.json()["result"]["request_file_id"]            
            response = recognize_voice(ss_token=ss_token, file_id=file_id)
            # print(*response)
            # print("----------------", file_id)
            
            if (os.path.exists(voice)):
                os.remove(voice)
            
            task_id = response.json()["result"]["id"] 
            # print("----------------", task_id)
            status = ""
            
            while (status != "DONE" and status != "-1"):
                time.sleep(1)
                response = get_status(ss_token=ss_token, task_id=task_id)
                # print(*response)
                if (status != "ERROR"):
                    status = response.json()["result"]["status"]   
                    # print(status)
                else:
                    print("Проблема со статусом")
                    status = "-1"
            
            if (status == "DONE"):
                response_file_id = response.json()["result"]["response_file_id"] 
                response = get_transcript(ss_token=ss_token, response_file_id=response_file_id)
                
                if (response != -1):
                    # print(*response)
                    text = response.json()[0]["results"][0]["normalized_text"] #text
                    print("-------------------------------RESULT---------------------")
                    print(text)
                    return text
                else:
                    print("Проблема с получением транскрипта")         

        else:
            print("Проблема с запросом")

    else:
        print("Проблема при осуществулении доступа к SalutSpeech Token")
        
# voice_to_text(r"D:\source\repos\nuclear-hack\voiceAwACAgIAAxkBAAOCZiPvdXpCGkUtba9TPn4OWxF_BsEAAkxHAAJjiCBJJThFtRFabo00BA.oga")

def validate_date(end_date, start_date):
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
    max_date, min_data = max_start_and_min_date()
    max_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
    min_data = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')

    if (end_date > max_date):
        return False
    elif (start_date < min_data):
        return False
    else:
        return True

    

    
def get_gigachat_message(auth_key, user_message):
    """
    Отправляет POST-запрос к API чата для получения ответа от модели GigaChat.

    Параметры:
    - auth_token (str): Токен для авторизации в API.
    - user_message (str): Сообщение от пользователя, для которого нужно получить ответ.

    Возвращает:
    - str: Ответ от API в виде текстовой строки.
    """
    # URL API, к которому мы обращаемся

    response = get_token(auth_token=auth_key)
    if response != -1:
        giga_token = response.json()['access_token']
    else:
        return "Проблема при осуществулении доступа к GigaChat Token"

    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Подготовка данных запроса в формате JSON
    payload = json.dumps({
        "model": "GigaChat",  # Используемая модель
        "messages": [
            {
                "role": "user",  # Роль отправителя (пользователь)
                "content": user_message  # Содержание сообщения
            }
        ],
        "temperature": 0.5,  # Температура генерации
        "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
        "n": 1,  # Количество возвращаемых ответов
        "stream": False,  # Потоковая ли передача ответов
        "max_tokens": 512,  # Максимальное количество токенов в ответе
        "repetition_penalty": 1,  # Штраф за повторения
        "update_interval": 0  # Интервал обновления (для потоковой передачи)
    })

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',  # Тип содержимого - JSON
        'Accept': 'application/json',  # Принимаем ответ в формате JSON
        'Authorization': f'Bearer {giga_token}'  # Токен авторизации
    }

    # Выполнение POST-запроса и возвращение ответа
    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        json_string = response.json()
        return json_string["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        # Обработка исключения в случае ошибки запроса
        print(f"Произошла ошибка: {str(e)}")    
        return -1
    

def get_user_station(user_message):
    auth_key = "MTQ1Zjk2YTMtOWI2YS00MzUyLWIwN2QtZDkxZGU3N2UzMTg1OmM0YmRkOTIzLWY2ZDctNDk4MC04OTBjLWM2ZDk0NzQ0YmRhYQ=="
    task_gigachat = "используя информацию из user_message вычлени название станции метро и отправь его в формате json в виде: {'station' :'название станции из user_message'}"
    message = f"отправь без комментриаев 'user_message': {user_message},'task':'{task_gigachat}'"

    user_station_json = json.loads(get_gigachat_message(auth_key=auth_key, user_message=message).replace("'", '"'))
    return user_station_json["station"]


def get_user_dates(user_message, date_now):

    with open('ProxyapiSecret.txt', 'r') as file:
        api_key = file.read()

    task_gpt  = """
    Проанализируй user_message для определения запрашиваемого в сообщении временного интервала учитвая время date_now:
    1. Выдели начало запрашиваемого периода в формате (ГГГГ-ММ-ДД ЧЧ:ММ). Например для запроса проанализируй пассажиропоток за предыдущий год при текущей дате 2022-09-01 нужно вывести 01.01.2021.
    2. Выдели конец запрашиваемого периода в формате (ГГГГ-ММ-ДД ЧЧ:ММ). Например для запроса проанализируй пассажиропоток за предыдущий год при текущей дате 2022-09-01 нужно вывести 31.12.2021.
    В коцне верни json в формате {end_date': 'конец периода','start_date': 'начало периода} без переноса строк'
    """

    request_gpt = f"date_now: {date_now} , user_massage: {user_message}, task: {task_gpt}"

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.proxyapi.ru/openai/v1",
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": request_gpt}]
    )

    answer = response.choices[0].message.content
    answer = answer.replace("'", '"')
    answer = json.loads(answer)
    return answer
    

def get_lev(metro_data, user_station):
    lev_dict_list = []
    for index, row in metro_data.iterrows():
        lev_dict = {}
        lev = fuzz.WRatio(row["Станция"], user_station)
        lev_dict["Станция"] = row["Станция"]
        lev_dict["Расстояние Ливинштейна"] = lev
        lev_dict["Линия"] = row["Линия"]
        lev_dict_list.append(lev_dict) 

    lev_df = pd.DataFrame(lev_dict_list)
    lev_df = lev_df.sort_values(by="Расстояние Ливинштейна", ascending=False)
    json_answer = {
        "0": [lev_df.iloc[0]["Станция"], lev_df.iloc[0]["Линия"]],
        "1": [lev_df.iloc[1]["Станция"], lev_df.iloc[1]["Линия"]],
        "2": [lev_df.iloc[2]["Станция"], lev_df.iloc[2]["Линия"]]
    }
    return json.dumps(json_answer, ensure_ascii=False)

def rename_station(df):
    with open("utils/rename_station.json", 'r') as file:
        rename_dict = json.load(file)
    
    drop = ["К", "ТПУ Рязанская"]
    df = df[~df["Станция"].isin(drop)]
    df['Станция'] = df['Станция'].replace(rename_dict)
    return df


def date_column_change(df):
    actual_col = []
    for date_column in df.iloc[:, 3:].columns:
        actual_col.append(date_column)

    df.iloc[:, 3:].columns = actual_col
    return df

def del_last_3_symbols(df):
    new_columns = [col[:-3] if i >= 3 else col for i, col in enumerate(df.columns)]
    df.columns = new_columns
    return df

def get_metro_json():
    with open("moscow_metro.json", "r") as f:
        stations = json.load(f)
        return stations
    
def merge_stations(df, stations_data):
    # Преобразуем список словарей в DataFrame напрямую
    stations_info = pd.DataFrame(stations_data)
    
    # Переводим названия станций в нижний регистр
    df['Станция'] = df['Станция'].str.lower()
    stations_info['station'] = stations_info['station'].str.lower()
    
    # Функция для получения лучшего совпадения по Левенштейну
    def get_best_match(row):
        best_match = process.extractOne(row['Станция'], stations_info['station'], scorer=fuzz.token_sort_ratio)
        return best_match[0] if best_match[1] >= 80 else None  # Возвращаем совпадение, если достаточно хорошее
    
    # Применяем функцию сопоставления
    df['matched_station'] = df.apply(get_best_match, axis=1)
    
    # Объединяем данные
    result_df = pd.merge(df, stations_info, left_on='matched_station', right_on='station', how='left')
    
    # Убираем временную колонку
    result_df.drop(columns=['matched_station'], inplace=True)
    
    # Возвращаем итоговый DataFrame
    return result_df


def preprocessing(df):
    df.rename(columns={'Дата': 'Линия'}, inplace=True)
    df = rename_station(df)
    default_columns = df.iloc[:, :3].columns.values
    reverse_col = df.iloc[:, 3:].columns[::-1].values
    df = pd.concat([df[default_columns], df[reverse_col]], axis=1)
    df = date_column_change(df)
    df.columns = [str(col).strip() for col in df.columns]
    df.drop_duplicates(subset=['Станция', 'Номер линии', 'Линия'], inplace=True)
    df = del_last_3_symbols(df)
    return df

# HOUR DISTRIBUTION COEF
def form_timelist():
    # задаем начальную точку
    current_time = datetime.time(0, 0)

    timestamps = []
    periods = 0

    # каждые полчаса записываем в список 
    while periods < 48:
        timestamps.append(current_time.strftime('%H:%M'))
        current_time = (datetime.datetime.combine(datetime.date(1, 1, 1), current_time) + datetime.timedelta(minutes=30)).time()
        periods+=1

    return timestamps

def fill_plot_values():
    
    work = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 44000, 62000, 115000, 161000, 245000, 250000, 185000, 175000, 130000, 125000, 105000, 100000, 101000, 102000, 102000, 101000, 107000, 112000, 122000, 126000, 140000, 154000, 185000, 215000, 255000, 237000, 173000, 145000, 125000, 100000, 86000, 72000, 62000, 48000, 35000, 0, 0, 0]
    rest = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30000, 40000, 50000, 55000, 72000, 82000, 85000, 95000, 80000, 95000, 80000, 95000, 100000, 105000, 107000, 115000, 118000, 122000, 125000, 130000, 123000, 121000, 123000, 125000, 125000, 120000, 105000, 102000, 100000, 92000, 86000, 75000, 80000, 60000, 50000, 0, 0, 0]
    
    return work, rest


def coef(date, start="00:00", end="23:30"):

    # date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M').date()
    time_start = datetime.datetime.strptime(start, "%H:%M").time()
    time_end = datetime.datetime.strptime(end, "%H:%M").time()

    timestamps = form_timelist()
    workday, weekday = fill_plot_values()

    # в зависимости от дня недели выбираем патерн (выходные или будни)
    if date.weekday in (5, 6): 
        values = weekday
    else:
        values = workday
    
    # ищем индексы с временем
    # index_start = timestamps.index(time_start.strftime('%H:%M'))
    # index_end = timestamps.index(time_end.strftime('%H:%M'))
    index_start = next((i for i, ts in enumerate(timestamps) if ts >= time_start.strftime('%H:%M')), 0)
    index_end = next((i for i, ts in enumerate(timestamps) if ts >= time_end.strftime('%H:%M')), len(timestamps) - 1)

    return sum(values[index_start:index_end + 1]) / sum(values)


def get_db_connect():

    with open('utils/db_secret.json') as f:
        params = json.load(f)

    try:
        connection = psycopg2.connect(**params)
        print("Подключение к базе данных успешно установлено")
        return connection
    except psycopg2.OperationalError as e:
        print("Произошла ошибка при подключении к базе данных:", e)
        return None

def get_connection():

    POSTGRES_HOST='80.87.107.22'
    POSTGRES_PORT=5432
    POSTGRES_DATABASE='hack'
    POSTGRES_USERNAME='user'
    POSTGRES_PASSWORD='password'

    host = POSTGRES_HOST
    port = POSTGRES_PORT
    dbname = POSTGRES_DATABASE
    user = POSTGRES_USERNAME
    password = POSTGRES_PASSWORD

    cnn = connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        row_factory=dict_row
    )

    return cnn






def catboost_learn():
    with get_connection() as cnn:
        with cnn.cursor() as cur:
            cur.execute("SELECT * FROM raw")
            data = cur.fetchall()   
            
            data = preprocessing(pd.DataFrame(data))
    #stations = get_metro_json()
    #data = merge_stations(data, stations)
    #data.drop(columns=['railway_station', 'station_id', 'line', 'station'], inplace=True)
    """
    
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    cat_features = ['Станция', 'Номер линии', 'Линия']
    model = CatBoostRegressor(iterations=1000, learning_rate=0.1, depth=10, cat_features=cat_features)
    model.fit(X, y)

    predictions = model.predict(X[:, 1:])
    res = {X.columns[i]: predictions[i] for i in range(len(predictions))}
    """

    return data
                



def get_day_plot():

    pred = 80000

    date = datetime.datetime.strptime("2024-04-04", '%Y-%m-%d')
    
    timestamps = form_timelist()
    workday, weekday = fill_plot_values()

    if date.weekday in (5, 6): 
        x = [i / sum(workday) * pred for i in weekday] 
    else:
        x = [i / sum(workday) * pred for i in workday] 
    
    
    plt.figure(figsize=(15, 6))
    plt.plot(timestamps, x, color='b', marker='o')
    plt.xlabel('Время')
    plt.ylabel('Количество пассажиров')
    plt.title('Пассажиропоток')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()
