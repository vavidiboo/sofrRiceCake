from typing import Optional, List, Dict, Any


class KakaoResponse:
    @staticmethod
    def _response(outputs: List[Dict[str, Any]], data: Optional[Dict[str, Any]] = None, quick_replies: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        body = {"version": "2.0", "template": {"outputs": outputs}}

        if quick_replies:
            body["template"]["quickReplies"] = quick_replies

        if data is not None:
            body["data"] = data

        return body

    @staticmethod
    def quick_reply(label: str, message: str) -> Dict[str, str]:
        return {"label": label, "action": "message", "messageText": message}

    #buttons 
    @staticmethod
    def message_button(label: str, message: str) -> Dict[str, str]:
        return {"action": "message", "label": label, "messageText": message}

    @staticmethod
    def web_link_button(label: str, url: str) -> Dict[str, str]:
        return {"action": "webLink", "label": label, "webLinkUrl": url}

    @staticmethod
    def block_button(label: str, block_id: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        btn = {"action": "block", "label": label, "blockId": block_id}

        if extra:
            btn["extra"] = extra

        return btn

    #simple outputs 
    @staticmethod
    def simple_text(text: str, quick_replies: Optional[List[Dict[str, Any]]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return KakaoResponse._response([{"simpleText": {"text": text}}], data=data, quick_replies=quick_replies)

    @staticmethod
    def simple_image(image_url: str, alt_text: str = "", quick_replies: Optional[List[Dict[str, Any]]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"simpleImage": {"imageUrl": image_url, "altText": alt_text}}

        return KakaoResponse._response([payload], data=data, quick_replies=quick_replies)

    #basic card
    @staticmethod
    def basic_card(title: str, desc: str, image_url: Optional[str] = None, buttons: Optional[List[Dict[str, Any]]] = None, quick_replies: Optional[List[Dict[str, Any]]] = None, data: Optional[Dict[str, Any]] = None, fixed_ratio: bool = False) -> Dict[str, Any]:
        card = {"basicCard": {"title": title, "description": desc, "buttons": buttons or []}}

        if image_url:
            card["basicCard"]["thumbnail"] = {"imageUrl": image_url, "fixedRatio": fixed_ratio}

        return KakaoResponse._response([card], data=data, quick_replies=quick_replies)

    #commerce card
    @staticmethod
    def commerce_card(title: str, desc: str, price: int, currency: str = "KRW", image_url: Optional[str] = None, buttons: Optional[List[Dict[str, Any]]] = None, quick_replies: Optional[List[Dict[str, Any]]] = None, data: Optional[Dict[str, Any]] = None, discount: Optional[int] = None) -> Dict[str, Any]:
        commerce = {
            "commerceCard": {
                "description": desc,
                "price": price,
                "currency": currency,
                "thumbnails": [],
                "buttons": buttons or [],
            }
        }
        if title:
            commerce["commerceCard"]["title"] = title

        if image_url:
            commerce["commerceCard"]["thumbnails"].append({"imageUrl": image_url})

        if discount is not None:
            commerce["commerceCard"]["discount"] = discount

        return KakaoResponse._response([commerce], data=data, quick_replies=quick_replies)

    @staticmethod
    def list_item(title: str, desc: Optional[str] = None, image_url: Optional[str] = None, link: Optional[str] = None) -> Dict[str, Any]:
        item = {"title": title}
        if desc:
            item["description"] = desc

        if image_url:
            item["imageUrl"] = image_url

        if link:
            item["link"] = {"web": link}

        return item

    @staticmethod
    def list_card(header_title: str, items: List[Dict[str, Any]], buttons: Optional[List[Dict[str, Any]]] = None, quick_replies: Optional[List[Dict[str, Any]]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        card = {
            "listCard": {
                "header": {"title": header_title},
                "items": items,
            }
        }
        if buttons:
            card["listCard"]["buttons"] = buttons
        return KakaoResponse._response([card], data=data, quick_replies=quick_replies)

    #data only response
    @staticmethod
    def data_payload(data: Dict[str, Any]) -> Dict[str, Any]:
        # Some Kakao skills return data without template outputs.
        return {"version": "2.0", "data": data}
