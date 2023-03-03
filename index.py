from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import token
from database import save_vk_user, find_couple_for_vk_user

vk = vk_api.VkApi(token=token)
long_poll = VkLongPoll(vk)


def send_msg(user_id, message):
    vk.method("messages.send", {"user_id": user_id, "message": message, "random_id": randrange(10 ** 7), })


def send_msg_with_photo(user_id, message,  photo_id):
    vk.method("messages.send", {"user_id": user_id, "message": message, "random_id": randrange(10 ** 7),
                                "attachment": f"photo{photo_id}", })


def user_profile_is_closed(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "is_closed"})
    return response[0].get("is_closed")


def save_user_data(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "sex,bdate,city,relation"})[0]
    save_vk_user(response.get("id"), response.get("sex"), response.get("age"), response.get("city").get("id"),
                 response.get("relation"))


def get_domain_by_user_id(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "domain"})
    return f"vk.com/{response[0].get('domain')}"


def get_photo_url_by_user_id(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "photo_400_orig"})
    return f"{response[0].get('photo_400_orig')}"


def get_photo_id_by_user_id(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "photo_id"})
    return response[0].get('photo_id')


def is_start_request(text):
    if text.lower() in "/старт":
        return True
    else:
        return False


for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg_text = event.text
            client_user_id = event.user_id
            if is_start_request(msg_text):
                if user_profile_is_closed(client_user_id):
                    send_msg(client_user_id, "Ваш профиль закрыт, для работы VKinder откройте профиль")
                else:
                    save_user_data(client_user_id)
                    couple = find_couple_for_vk_user(client_user_id)
                    if couple is None:
                        send_msg(event.user_id, "Мы не смогли подобрать вам пару, загляните позже")
                    else:
                        send_msg(event.user_id, "Мы подобрали вам пару!")
                        send_msg_with_photo(event.user_id, f"{get_domain_by_user_id(couple.user_id)}",
                                            get_photo_id_by_user_id(couple.user_id))

            else:
                send_msg(event.user_id, "Привет, для запуска необходимо написать /старт")
