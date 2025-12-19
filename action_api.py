from fastapi import FastAPI, Request
import uvicorn
import random
from db import DataBase, UserDB
import firebase_admin
from firebase_admin import credentials
import os
import json


key_dict = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"]) 
DataBase.connect(key_dict)

app = FastAPI()


def errorMessage(title, description):
    return {
                "version": "2.0",
                "template": {
                    "outputs": [
                    {
                        "basicCard": {
                        "title": title,
                        "description": description,
                        "thumbnail": {
                            "imageUrl": "https://i.ifh.cc/RgHrDl.jpg"
                                        }
                                    }
                    }
                                ]
                                }
            }

def okMessage(title, description):
    return {
                "version": "2.0",
                "template": {
                    "outputs": [
                    {
                        "basicCard": {
                        "title": title,
                        "description": description,
                        "thumbnail": {
                            "imageUrl": "https://i.ifh.cc/M9WJWN.jpg"
                                        }
                                    }
                    }
                                ]
                                }
            }

@app.post("/")
async def root(request: Request):
    body = await request.json()
    print("kakao body:", body)

    utterance = body["userRequest"]["utterance"]
    user_id = body["userRequest"]["user"]["id"]

    return {"CODE":200}

@app.post("/show_advanture_status")
async def show_advanture_status(request: Request):
    body = await request.json()
    user_id = body["userRequest"]["user"]["id"]

    user = await UserDB.load(user_id)

    max_chapter = int(user['adventure']['chapter'])

    status = {0: "탐험할 수 있는 지역입니다.", 1: "아직 탐험할 수 없는 지영입니다."}

    

    stage_status = [0 if i <= max_chapter else 1 for i in range(1, 8)]

    print(stage_status)

    return {
        "version": "2.0",
        "data": {
            "1st": status[stage_status[0]],
            "2st": status[stage_status[1]],
            "3st": status[stage_status[2]],
            "4st": status[stage_status[3]],
            "5st": status[stage_status[4]],
            "6st": status[stage_status[5]],
            "7st": status[stage_status[6]]
        }
    }

@app.post("/signup")
async def signup(request: Request):
    body = await request.json()
    user_id = body["userRequest"]["user"]["id"]


    if await UserDB.load(user_id) == None:
        user = {"id":user_id, "balance":100000, "adventure":{"chapter":1, "stage":1}, "coin_flip":{"streak":0}}

        await UserDB.upload(dict(user))

        return okMessage(title="계정 생성 완료", description="성공적으로 계정 생성이 완료되었습니다.")

    else:
        return errorMessage(title="이미 등록된 사용자", description="이미 등록되어 있는 사용자입니다.")

@app.post("/open_box")
async def open_box(request: Request):
    body = await request.json()
    user_id = body["userRequest"]["user"]["id"]

    count = body["action"]["params"]["개수"]

    result_text = f"@{user_id}님,{count}개 상자를 열었더니 100골드를 얻었습니다!"

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": result_text}}
            ]
        }
    }

@app.post("/check_balance")
async def check_balance(request: Request):
    body = await request.json()
    user_id = body["userRequest"]["user"]["id"]

    user = await UserDB.load(user_id)
    print(user_id)

    return {
        "version": "2.0",
        "data": {
            "balance": f"{user['balance']:,}원"
        }
    }

@app.post("/adventure")
async def adventure(request: Request):
    body = await request.json()
    print("kakao body:", body)

    user_id = body["userRequest"]["user"]["id"]
    
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": "HI"}}
            ]
        }
    }

@app.post("/coin_flip")
async def coin_flip(request: Request):
    body = await request.json()
    
    user_id = body["userRequest"]["user"]["id"]
    user_answer = body["action"]['clientExtra']['answer'] 

    coin_status = {0: "앞", 1: "뒷"}
    coin_image = {0: "https://i.ifh.cc/NlFXr8.jpg", 1: "https://i.ifh.cc/zjFCPF.jpg"}
    status = random.randint(0, 1)

    answer = coin_status[status]

    user = await UserDB.load(user_id)
    balance = user['balance'] 
    streak = user['coin_flip']['streak']

    if answer == user_answer:     
        bouns = 50 * (2 ** streak)

        description = "승리!"

        if streak+1 >= 2: 
            description = f"🔥 {streak+1}연승 중!!  {2 ** streak}배 보상!"

        await UserDB.update(user_id, {"coin_flip":{"streak": streak+1}})
        await UserDB.update(user_id, {"balance":balance+bouns})

        return {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                        {
                            "basicCard": {
                            "title": f"{answer}면!",
                            "description": f"{description} \n잔고 : {(balance + bouns):,}원 (+{bouns:,}원)",
                            "thumbnail": {
                                "imageUrl": coin_image[status]
                            },
                            "buttons": [
                                {
                                "action": "message",
                                "label": "다시하기",
                                "messageText": "동전 던지기"
                                }
                            ]
                            }
                        }
                        ]
                    }
                }

    else:         
        await UserDB.update(user_id, {"coin_flip":{"streak": 0}})
        await UserDB.update(user_id, {"balance":balance-50})

        return {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                        {
                            "basicCard": {
                            "title": f"{answer}면!",
                            "description": f"패배하였습니다. \n잔고 : {(balance - 50):,}원 (-50원)",
                            "thumbnail": {
                                "imageUrl": coin_image[status]
                            },
                            "buttons": [
                                {
                                "action": "message",
                                "label": "다시하기",
                                "messageText": "동전 던지기"
                                }
                            ]
                            }
                        }
                        ]
                    }
                }

uvicorn.run(app, host="0.0.0.0", port=8000)







