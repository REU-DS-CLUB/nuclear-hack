from msilib.schema import File
from tkinter import W
import requests
import json
import uuid
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import os
import time

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
        data = f.read()

    response = requests.post('https://smartspeech.sber.ru/rest/v1/data:upload', headers=headers, data=data, verify=False)
    print(response)
    return response

def recognize_voice(ss_token, file_id):
    headers = {
    'Authorization': f'Bearer {ss_token}',
    'Content-Type': 'application/json',
}
    
    data = '\n{\n  "options": {\n    "language": "ru-RU",\n    "audio_encoding": "mp3",\n    "sample_rate": 16000,\n    "hypotheses_count": 1,\n    "enable_profanity_filter": false,\n    "max_speech_timeout": "20s",\n    "channels_count": 2,\n    "no_speech_timeout": "7s",\n    "hints": {\n        "words": ["станция", "ветка"],\n        "enable_letters": true,\n        "eou_timeout": "2s"\n    },\n    "insight_models": ["csi"],\n    "speaker_separation_options": {\n      "enable": true, \n      "enable_only_main_speaker": false, \n      "count": 2\n    }\n  },\n  "request_file_id": "' + str(file_id) + '"\n}'
    data = data.encode()
    response = requests.post('https://smartspeech.sber.ru/rest/v1/speech:async_recognize', headers=headers, data=data, verify= False)
    return response

def get_status(ss_token, task_id):
    headers = {
    'Authorization': f'Bearer {ss_token}',
}

    response = requests.get(f'https://smartspeech.sber.ru/rest/v1/task:get?id={task_id}', headers=headers, verify=False)
    return response

def get_transcript(ss_token, response_file_id):
    headers = {
    'Authorization': f'Bearer {ss_token}',
}

    response = requests.get(
    f'https://smartspeech.sber.ru/rest/v1/data:download?response_file_id={response_file_id}',
    headers=headers,
)
    return response

def voice_to_text(voice: str):
    auth_key = "MTljNjgxNmQtNDFmOS00MjQ3LWIxMzYtYzA0ODRlZWFmOGY5Ojk0MjgwZGJkLTBmYWMtNGNhZC05NTAzLWY0NWNlZGUzOWJhYQ=="
    response = get_ss_token(auth_token=auth_key)
    print(response)
    if response != -1:
        ss_token = response.json()['access_token']
        response = upload_voice(ss_token=ss_token, voice=voice)
        
        if (response != -1):
            file_id = response.json()["result"]["request_file_id"]            
            response = recognize_voice(ss_token=ss_token, file_id=file_id)
            print(response)
            
            task_id = response["result"]["id"] 
            status = ""
            
            while (status != "DONE" or status != "-1"):
                time.sleep(0.1)
                response = get_status(ss_token=ss_token, task_id=task_id)
                if (status != - 1):
                    status = response["result"]["status"]                    
                else:
                    print("Проблема со статусом")
                    status = "-1"
            
            if (status == "DONE"):
                response_file_id = response["result"]["response_file_id"] 
                response = get_transcript(ss_token=ss_token, response_file_id=response_file_id)
                
                if (response != -1):
                    text = response["results"]["text"] #normalized_text
                    print("-------------------------------")
                    print(text)
                    return text
                else:
                    print("Проблема с получением транскрипта")
                
                        

        else:
            print("Проблема с запросом")

    else:
        print("Проблема при осуществулении доступа к SalutSpeech Token")
        
voice_to_text(r"D:\source\repos\nuclear-hack\utils\voiceAwACAgIAAxkBAAN0ZiPGsNSnef-qBS87pf6jXAFTkaEAAolHAAJjiBhJfyY61sPVXWE0BA.mp3")
    
def get_chat_station(auth_key, user_message):
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
    
def get_lev(metro_data, user_station):
    metro = pd.DataFrame(metro_data)
    lev_dict_list = []
    for metro in metro["station"]:
        lev_dict = {}
        lev = fuzz.WRatio(metro, user_station)
        lev_dict["station"] = metro
        lev_dict["lev"] = lev
        lev_dict_list.append(lev_dict) 

    lev_df = pd.DataFrame(lev_dict_list)
        
    return lev_df.sort_values(by='lev', ascending=False)

#return json.loads(answer['choices'][0]['message']['content'])["station"]