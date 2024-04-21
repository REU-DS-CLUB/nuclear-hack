import requests

def document(name: str, path: str):
    url = f"http://213.189.219.51:8000/handlers/file/{name}"
    
    file =  open(path, "rb")
    FF = {"file" : file}

    try:
        response = requests.post(url, files=FF, verify= False)
    except:
        print("Ошибка в request.document()")
        return -1
    print(response)
    print(*response)
    return response

def voice(path: str):
    url = f"http://213.189.219.51:8000/handlers/audio"
    
    file =  open(path, "rb")
    FF = {"file" : file}

    try:
        response = requests.get(url, files=FF, verify= False)
    except:
        print("Ошибка в request.document()")
        return -1
    print(response)
    print(*response)
    return response