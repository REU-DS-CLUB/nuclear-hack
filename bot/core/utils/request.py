import requests

async def document(name: str, path: str):
    url = f"http://80.87.107.22:8002/handlers/file/{name}"
    
    file =  open(path, "rb")
    FF = {"file" : file}

    response = requests.post(url, files=FF, verify= False)
    # try:
    #     response = requests.post(url, files=FF, verify= False)
    # except Exception as e:
    #     print("Ошибка в request.document()")
    #     print(e)
    print(response)
    return response

async def voice(path: str):
    url = f"http://80.87.107.22:8002/handlers/audio_prev"
    
    file =  open(path, "rb")
    FF = {"file" : file}

    try:
        response = requests.post(url, files=FF, verify= False) 
    except:
        print("Ошибка в request.voice()")
    print(response)
    return response
    

async def user_text(texts: str):
    url = f"http://80.87.107.22:8002/handlers/text_prev?text={texts}"

    try:
        response = requests.post(url, verify= False)
        print(*response)
    except:
        print("Ошибка в request.text()")
    finally:
        return response

async def prediction(station, dates):
    
    url = f"http://80.87.107.22:8002/handlers/text?station_name={station[0]}&branch={station[1]}&start_date={dates['start_date']}&end_date={dates['end_date']}"
    
    try:
        response = requests.post(url, verify= False) 
    except:
        print("Ошибка в request.prediction()")
    print(response)
    return response

async def text_to_predict(texts: str):
    url = f"http://80.87.107.22:8002/handlers/predict?text={texts}"
    
    try:
        response = requests.post(url, verify= False) 
    except:
        print("Ошибка в request.text+to+predict()")
    print(response)
    return response