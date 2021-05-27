import datetime
import urllib
from urllib.request import urlopen
import time
import logging

import bs4
import telegram

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, log_errors

from constants.bezirke import BEZIRKE

# selenium for forecast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options


@register_module()
class KachelmannBot(AbstractModule):
    def __getClosestTime(self, increment):
        time = datetime.datetime.utcnow()
        diff = time.minute % increment
        time = time - datetime.timedelta(minutes=diff)

        timestring = time.strftime("%Y%m%d-%H%Mz")
        return timestring

    def __getKachelmannImage(self, pageURL):
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64)"
        }
        soup = self.get_soup(pageURL, header)

        imageurl = soup.find("meta", property="og:image")
        imageurl = imageurl["content"]
        return imageurl

    def __getRegion(self, region):
        errorMessage = ""
        if not region:
            errorMessage = "Parameter angeben bitte! Mögliche Regionen:\n" + ", ".join(BEZIRKE.keys())
            return (region, errorMessage)
        try:
            region = BEZIRKE[region.upper()]
        except KeyError:
            errorMessage = "De Region kenn i ned 🙄"
            return (region, errorMessage)

        return (region, errorMessage)

    def get_soup(self, url, header):
        req = urllib.request.Request(url, headers=header)
        open_url = urlopen(req)
        soup = bs4.BeautifulSoup(open_url, "html.parser")
        return soup

    @register_command(command="radar", short_desc="Shows the rain radar of a region. 🌧",
                      long_desc="This command returns an image containing the current "
                                "rain conditions of a given austrian region.\n"
                                "Possible regions are: " + ", ".join(BEZIRKE.keys()),
                      usage=["/radar $region-abbreviation", "/radar FR"])
    def radar(self, update: Update, context: CallbackContext):

        queryText = self.get_command_parameter("/radar", update)

        region, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                     text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/regenradar"
        timestring = self.__getClosestTime(5)
        pageURL = (baseURL + "/{}/{}.html").format(region, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        context.bot.send_photo(chat_id=chat_id, photo=imageURL)

    @register_command(command="tracking", short_desc="Storm-tracking of a region. ⛈⚡️",
                      long_desc="This command returns an image containing the current "
                                "storm-tracking information of a given austrian region.\n"
                                "Possible regions are: " + ", ".join(BEZIRKE.keys()),
                      usage=["/tracking $region-abbreviation", "/tracking AT"])
    def tracking(self, update: Update, context: CallbackContext):

        queryText = self.get_command_parameter("/tracking", update)

        region, errorMessage = self.__getRegion(queryText)
        if errorMessage != "":
            # invalid region
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                     text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/stormtracking"
        timestring = self.__getClosestTime(5)
        pageURL = (baseURL + "/{}/blitze-radarhd/{}.html").format(region, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        context.bot.send_photo(chat_id=chat_id, photo=imageURL)

    @register_command(command="wind", short_desc="Shows the wind gusts of a region. 💨🌬",
                      long_desc="This command returns an image containing the current "
                                "wind direction or wind gust information of a given austrian region.\n"
                                "Possible regions are: " + ", ".join(BEZIRKE.keys()),
                      usage=["/wind (böen|mittel) $region", "/wind böen AT", "/wind mittel WZ"])
    def wind(self, update: Update, context: CallbackContext):

        queryText = self.get_command_parameter("/wind", update)

        # split query into type and region
        syntaxErrorMessage = "I checks ned ganz, bitte schick ma dein command im Muster:\n`/wind (böen|mittel) <Region>`"
        windtype = ""
        region = ""
        try:
            windtype, region = queryText.split(maxsplit=2)
        except (ValueError, AttributeError) as e:
            # send syntax error
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                     text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # get region
        region, errorMessage = self.__getRegion(region)
        if errorMessage != "":
            if region == "böen" or region == "böe" or region == "mittel":
                # mixed up parameters (/wind at böen), send syntax error
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                         text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                # else send unknown region error
                context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                         text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # check type
        if windtype is not None and (windtype.lower() == 'böen' or windtype.lower() == 'böe'):
            windtype = "windboeen"
        elif windtype is not None and windtype.lower() == "mittel":
            windtype = "windrichtung-windmittel"
        else:
            # unknown type, send error
            errorMessage = "Mechadsd du Böen oder Mittelwind? Schick ma ans vo de zwa: 🌬️\n`/wind böen <Region>`\n`/wind mittel <Region>`"
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                     text=errorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # build page url
        baseURL = "https://kachelmannwetter.com/at/analyse/superhd/"
        timestring = self.__getClosestTime(60)
        pageURL = (baseURL + "{}/{}/{}.html").format(region, windtype, timestring)

        # get image
        imageURL = self.__getKachelmannImage(pageURL)

        # send image
        chat_id = update.message.chat_id
        context.bot.send_photo(chat_id=chat_id, photo=imageURL)

    @register_command(command="forecast", short_desc="Shows the forecast for the selected location",
                      long_desc="This command returns an image containing the"
                                "forecast for temperature, rainfall, clouds, wind, sunshine and barometric pressure.\n",
                      usage=["/forecast <location>", "/forecast Hagenberg", "/forecast Ellmau"])
    @log_errors(perform_finally_call=True)
    #             "Possible forecast types are super HD (SHD) and HD (HD)",
    #   usage=["/forecast [SHD|HD] <location>", "/forecast SHD Hagenberg", "/forecast HD Ellmau"])
    def forecast(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                 text="Command temporary disabled", parse_mode=telegram.ParseMode.MARKDOWN)
        return
        queryText = self.get_command_parameter("/forecast", update)

        # split query
        syntaxErrorMessage = "I checks ned ganz, bitte schick ma dein command im Muster:\n`/forecast <Ort>`"
        location = ""
        try:
            location = queryText.split(maxsplit=1)
        except (ValueError, AttributeError) as e:
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                     text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            print("Error splitting command")
            return

        if location == "":
            context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                     text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
            print("Error splitting command")
            return

        # # split query into forecast type and location
        # syntaxErrorMessage = "I checks ned ganz, bitte schick ma dein command im Muster:\n`/forecast [SHD|HD] <Ort>`"
        # forecasttype = ""
        # location = ""
        # try:
        #     forecasttype, location = queryText.split(maxsplit=2)
        # except (ValueError, AttributeError) as e:
        #     # send syntax error
        #     context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
        #                              text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
        #     print("Error splitting command")
        #     return

        # forecasttype = forecasttype.upper()

        # print("location: {}, type: {}".format(location, forecasttype))

        # if (location == "" or location == "SHD" or location == "HD" or (forecasttype == "SDH" or forecasttype == "HD")):
        #     # send syntax error
        #     context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
        #                              text=syntaxErrorMessage, parse_mode=telegram.ParseMode.MARKDOWN)
        #     print("Error parsing forecast type")
        #     return

        # load search page        

        options = Options()
        # Enable headless mode to run on systems without a display (docker container)
        options.headless = True

        driver = webdriver.Firefox(options=options, log_path='./log/geckodriver.log')
        # This function is being called as finally statement:
        self.finally_call = lambda: driver.close()
        searchUrl = "https://kachelmannwetter.com/at/vorhersage"
        driver.get(searchUrl)

        # click away cookie message
        try:
            print("Trying to find cookie message ...")
            elem = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".nx2XwXx4"))
            )
            print("Found message, clicking button ...")
            cookieButton = driver.find_element_by_css_selector("button.nx3Fpp8U.nx3gnDVX").click()
        except TimeoutException:
            print("Cookie message not found, skipping ...")

        # search for location on search page
        print("Searching for location")
        searchBox = driver.find_element_by_id("forecast-input-0")
        searchBox.clear()
        searchBox.send_keys(location)
        searchButton = driver.find_element_by_css_selector("span.input-group-addon:nth-child(4)").click()

        if (driver.current_url == searchUrl + "/search"):
            print("Still on search page")
            # if the URL after the search is still the search URL,
            # there are either multiple or no results for the location.
            searchRes = driver.find_elements_by_id("search-results")[0]
            if (searchRes.find_elements_by_tag_name("p")[
                0].text == 'Wir haben zu Ihrer Sucheingabe leider keine passenden Orte gefunden.'):
                # no results found
                errMsg = "Moasd des Loch kenn i? Probier vllt an aundan Ort. 🗺️"
                context.bot.send_message(chat_id=update.message.chat_id,
                                         reply_to_message_id=update.message.message_id,
                                         text=errMsg)
            elif (searchRes.find_elements_by_tag_name("p")[
                      0].text == 'Wir haben mehrere infrage kommende Orte für Ihre Sucheingabe gefunden.'):
                # just take the first search result - otherwise the communication flow
                # will be slowed down for a functionality that can be forced by using a more
                # specific search term in the first place
                driver.find_elements_by_class_name("fcwcity")[0].find_element_by_tag_name("a").click()

        # let page render
        print("Waiting for page to render")
        elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'visibility_graph')))
        time.sleep(1)  # wait for animation to finish

        # hide header (will jump into forecast otherwise)
        driver.execute_script("document.getElementById('w0').remove()")
        driver.execute_script("document.getElementById('w3').remove()")
        driver.execute_script("document.getElementsByClassName('menue-head')[0].remove()")

        # save image
        print("Saving image")
        imagePath = "./images/forecast_image.png"
        elem = driver.find_element_by_id("weather-forecast-compact")
        elem.screenshot(imagePath)
        # pngImage = elem.screenshot_as_png # can't send binary data, need to save first ...

        # get location name
        locName = ""
        try:
            locName = driver.find_elements_by_class_name("forecast-h1")[0].text + driver.find_elements_by_class_name("h3-landkreis")[0].text
        except NoSuchElementException as nse:
            # don't add text, keep empty
            print("No location name found")

        # send image
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open(imagePath, "rb"), caption=locName)
