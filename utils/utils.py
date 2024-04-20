import requests
import json
import uuid
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
from openai import OpenAI

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

def get_user_dates(api_key, user_message, date_now):
    

    date_now = '2022-09-01'
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
        lev = fuzz.WRatio(row["станция"], user_station)
        lev_dict["station"] = row["station"]
        lev_dict["lev"] = lev
        lev_dict["line"] = row["line"]
        lev_dict_list.append(lev_dict) 

    lev_df = pd.DataFrame(lev_dict_list)
        
    return lev_df.sort_values(by='lev', ascending=False).head(3)

def station_rename(df):
    df.rename({"Б.Рокоссовского":"Бульвар Рокоссовского",
    "Преображенск. пл":"Преображенская площадь",
    "Пр-т Вернадск.СЛ":"Проспект Вернадского",
    "Красногвардейск.":"Красногвардейская",
    "Павелецкая ЗЛ":"Павелецкая",
    "Театральная(Зам)":"Театральная",
    "Белорусская ЗЛ":"Белорусская",
    "Киевская АПЛ":"Киевская",
    "Смоленская АПЛ":"Смоленская",
    "Арбатская АПЛ":"Арбатская",
    "Пл. Революции":"Площадь Революции",
    "Курская АПЛ":"Курская",
    "Электрозав-я АПЛ":"Электрозаводская",
    "Арбатская ФЛ":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",
    "":"",

                       











    },axis=1, inplace=True)

#return json.loads(answer['choices'][0]['message']['content'])["station"]