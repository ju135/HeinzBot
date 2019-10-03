import json
import requests
from APIKeyReader import read_key

base_url = "https://www.mittag.at/"

def receive_menue(bot, update):
    access_token = get_access_token()
    # defining address of campina to show up first
    longitute = 14.513489
    latitude = 48.368304
    menue_url = base_url + "api/2/menus?v=android1.5.0&max=6&lon=" + str(
        longitute) + "&lat=" + str(latitude) + "&fields=prices"
    header_params = {'Authorization': 'Bearer ' + access_token}
    r = requests.get(menue_url, headers=header_params)
    menue_data = json.loads(r.text)

    replyText = ""

    for singleRestaurant in menue_data["menus"]:
        # just select campina, nsquare and gasthaus-lamplmair
        if (singleRestaurant["restaurant"]["id"] == "campina") or (singleRestaurant["restaurant"]["id"] == "nsquare") or (singleRestaurant["restaurant"]["id"] == "gasthaus-lamplmair"):
            replyText += ("*" + singleRestaurant["restaurant"]["name"] + ":*")
            replyText += (singleRestaurant["menu"])
            if("prices" in singleRestaurant["restaurant"]):
                replyText += ("\n_Preise laut mittag.at:_")
                for price in singleRestaurant["restaurant"]["prices"]:
                    replyText += (price["description"] + ": " + str("{0:.2f}".format(price["price"])) + "€")
            replyText += "\n"

    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=replyText, parse_mode=telegram.ParseMode.MARKDOWN)

def get_access_token() -> str:
    authorization_payload = {'client_id': read_key("mittag_client_id"),
                             'client_secret': read_key("mittag_client_secret"),
                             'grant_type': 'client_credentials',
                             'scope': 'public+fav+reservation'}
    auth_url = base_url + "oauth/token"
    r = requests.post(auth_url, data=authorization_payload)
    auth_data = json.loads(r.text)
    access_token = auth_data['access_token']
    return access_token