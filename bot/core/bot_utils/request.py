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
        response = requests.get(url, files=FF, verify= False) 
    except:
        print("Ошибка в request.voice()")
    print(response)
    return response
    

def text(text: str):
    url = f"http://80.87.107.22:8002/handlers/audio_prev"

    try:
        response = requests.get(url, verify= False)
    except:
        print("Ошибка в request.text()")
    print(response)
    return response