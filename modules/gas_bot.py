import json
import requests

from telegram import Update
from telegram.ext import CallbackContext

from modules.abstract_module import AbstractModule
from utils.decorators import register_module, register_command, log_errors


@register_module()
class GasBot(AbstractModule):
    @register_command(command="sprit",
                      short_desc="Sends the current gas price of given region ⛽️",
                      long_desc=f"This command sends the currently cheapest gas price of a given region.\n"
                                f"The fuel type can be set as command parameter and can be either 'SUP' "
                                f"(Super) or 'DIE' (Diesel - default).",
                      usage=["/sprit $plz [$fueltype]", "/sprit 4232", "/sprit 4232 SUP", "/sprit 8181 DIE"])
    @log_errors()
    def send_gas_price(self, update: Update, context: CallbackContext):
        query = self.get_command_parameter("/sprit", update)
        if not query:
            update.message.reply_text("Parameter angeben bitte...")
            return

        parts = query.split(" ")
        plz = parts[0]
        supported_fuel_types = ["DIE", "SUP"]
        fuel_type = supported_fuel_types[0]
        if len(parts) > 1:
            chosen_fuel_type = parts[1].upper()
            if chosen_fuel_type in supported_fuel_types:
                fuel_type = chosen_fuel_type

        url = "https://api.e-control.at/sprit/1.0/regions/units"
        r = requests.get(url)
        units_data = json.loads(r.text)

        for state in units_data:
            for region in state['b']:
                for city in region['g']:
                    if city['p'] == plz:
                        longitude = city['l']
                        latitude = city['b']
                        url = f"https://api.e-control.at/sprit/1.0/search/gas-stations/by-address?latitude={latitude}" \
                              f"&longitude={longitude}&fuelType={fuel_type}&includeClosed=false"
                        r = requests.get(url)
                        gas_station_data = json.loads(r.text)
                        gas_station_index = 0
                        reply_message = ""
                        for gas_station in gas_station_data:
                            if gas_station_index > 10:
                                break
                            for price in gas_station['prices']:
                                if gas_station_index == 0:
                                    reply_message = f"Bester Preis für {price['label']} in der " \
                                                    f"Nähe: {price['amount']}€ bei \"{gas_station['name']}\" " \
                                                    f"in {gas_station['location']['city']}, " \
                                                    f"{gas_station['location']['address']}"
                                    if len(gas_station_data) > 1:
                                        reply_message += "\nWeitere Preise:\n"
                                else:
                                    reply_message += f"{price['amount']}€ bei \"{gas_station['name']}\" " \
                                                     f"in {gas_station['location']['city']}, " \
                                                     f"{gas_station['location']['address']}\n"
                                # Only care about the first price of each gas-station
                                break
                            gas_station_index += 1

                        update.message.reply_text(reply_message)
                        return
        update.message.reply_text("Sorry, de PLZ hob i leider ned gfunden..")
