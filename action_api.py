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

    if user:
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

    else: 
        return errorMessage(title="등록되지 않은 사용자", description="\"등록\"을 입력하여 등록 후 다시 사용해주세요.")

@app.post("/signup")
async def signup(request: Request):
    body = await request.json()
    user_id = body["userRequest"]["user"]["id"]


    if await UserDB.load(user_id) == None:
        user = {"id":user_id, "balance":100000, "adventure":{"chapter":1, "stage":1}, "coin_flip":{"streak":0}, "item_upgrade":{"item":{"grade":0}}}

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
    
    if user:
        return {
            "version": "2.0",
            "data": {
                "balance": f"{user['balance']:,}원"
            }
        }

    else: 
        return errorMessage(title="등록되지 않은 사용자", description="\"등록\"을 입력하여 등록 후 다시 사용해주세요.")

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

@app.post("/upgrade_sword")
async def upgrade_sword(request: Request):
    body = await request.json()
    user_id = body["userRequest"]["user"]["id"]

    item_image = {
        0: "https://i.ifh.cc/3Wv0hb.png", 
        5: "https://i.ifh.cc/ywADHm.png",
        10: "https://i.ifh.cc/oAjLFn.png",
        15: "https://i.ifh.cc/Or8YwG.png"
    }
    
    probabilities = {
                        1: 1.0, 2: 1.0, 3: 1.0, 4: 0.9, 5: 0.5,
                        6: 0.4, 7: 0.3, 8: 0.2, 9: 0.15, 10: 0.1,
                        11: 0.05, 12: 0.03, 13: 0.02, 14: 0.015,
                        15: 0.008, 16: 0.004, 17: 0.002, 18: 0.0008, 19: 0.0003, 20: 0.0001
                    }

    user = await UserDB.load(user_id)

    if user: 
        balance = user['balance'] 
        item_grade = user['item_upgrade']['item']['grade']

        cost = 1000

        if balance < cost:
            return errorMessage(title="잔액 부족", description="골드가 부족합니다.")

        await UserDB.update(user_id, {"balance":balance-cost})
        success_chance = probabilities.get(item_grade+1, 0)

        if random.random() < success_chance:
            await UserDB.update(user_id, {"item_upgrade":{"item":{"grade":item_grade+1}}})

            if item_grade+1 < 5: 
                image = item_image[0]
            
            elif item_grade+1 < 10: 
                image = item_image[5]
            
            elif item_grade+1 < 10: 
                image = item_image[10]
                
            else:
                image = item_image[15]

            return {
                        "version": "2.0",
                        "template": {
                            "outputs": [
                            {
                                "basicCard": {
                                "title": f"⭐ 강화 성공 ⭐ +{item_grade} ➝ +{item_grade+1}",
                                "description": f"사용 골드 : {cost} \n잔고 : {(balance - cost):,}원",
                                "thumbnail": {
                                    "imageUrl": image,
                                    "fixedRatio": True
                                },
                                "buttons": [
                                    {
                                    "action": "message",
                                    "label": "강화",
                                    "messageText": "강화"
                                    }
                                ]
                                }
                            }
                            ]
                        }
                    }

            return next_level, balance, f"성공 ({item_grade+1}강)"

        else:
            if item_grade <= 5:
                if item_grade+1 < 5: 
                    image = item_image[0]
            
                elif item_grade+1 < 10: 
                    image = item_image[5]
                
                elif item_grade+1 < 15: 
                    image = item_image[10]
                    
                else:
                    image = item_image[15]

                await UserDB.update(user_id, {"item_upgrade":{"item":{"grade":item_grade}}})

                return {
                        "version": "2.0",
                        "template": {
                            "outputs": [
                            {
                                "basicCard": {
                                "title": f"💥 강화 실패 💥 +{item_grade} ➝ +{item_grade} (+0)",
                                "description": f"사용 골드 : {cost} \n잔고 : {(balance - cost):,}원",
                                "thumbnail": {
                                    "imageUrl": image,
                                    "fixedRatio": True
                                },
                                "buttons": [
                                    {
                                    "action": "message",
                                    "label": "강화",
                                    "messageText": "강화"
                                    }
                                ]
                                }
                            }
                            ]
                        }
                    }

            if item_grade <= 10:
                failed_grade = max(0, item_grade - 2)
                dropped_levels = item_grade - failed_grade

                if failed_grade < 5: 
                    image = item_image[0]
            
                elif failed_grade < 10: 
                    image = item_image[5]
                
                elif failed_grade < 15: 
                    image = item_image[10]
                    
                else:
                    image = item_image[15]

                await UserDB.update(user_id, {"item_upgrade":{"item":{"grade":failed_grade}}})

                return {
                        "version": "2.0",
                        "template": {
                            "outputs": [
                            {
                                "basicCard": {
                                "title": f"💥 강화 실패 💥 +{item_grade} ➝ +{failed_grade} (⬇ {dropped_levels})",
                                "description": f"사용 골드 : {cost} \n잔고 : {(balance - cost):,}원",
                                "thumbnail": {
                                    "imageUrl": image,
                                    "fixedRatio": True
                                },
                                "buttons": [
                                    {
                                    "action": "message",
                                    "label": "강화",
                                    "messageText": "강화"
                                    }
                                ]
                                }
                            }
                            ]
                        }
                    }

            else:
                await UserDB.update(user_id, {"item_upgrade":{"item":{"grade":0}}})

                return {
                        "version": "2.0",
                        "template": {
                            "outputs": [
                            {
                                "basicCard": {
                                "title": f"☠ 강화 실패 ☠ +{item_grade} ➝ 0 ⬇ (-{item_grade})",
                                "description": f"사용 골드 : {cost} \n잔고 : {(balance - cost):,}원",
                                "thumbnail": {
                                    "imageUrl": item_image[0],
                                    "fixedRatio": True
                                },
                                "buttons": [
                                    {
                                    "action": "message",
                                    "label": "강화",
                                    "messageText": "강화"
                                    }
                                ]
                                }
                            }
                            ]
                        }
                    }

    else: 
        return errorMessage(title="등록되지 않은 사용자", description="\"등록\"을 입력하여 등록 후 다시 사용해주세요.")


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

    if user:

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

    else: 
        return errorMessage(title="등록되지 않은 사용자", description="\"등록\"을 입력하여 등록 후 다시 사용해주세요.")


uvicorn.run(app, host="0.0.0.0", port=8000)
