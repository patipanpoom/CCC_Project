# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
weather data harvester function
"""

import json
from datetime import datetime

import requests
from flask import current_app

Observations = ["94839", "94838", "94844", "94693", "94843", "95831",
                "95832", "95839", "95827", "95835", "94827", "94836",
                "94920", "94834", "94835", "94826", "94842", "95825",
                "95822", "94829", "94840", "95845", "94833", "94830",
                "94828", "95826", "94837", "95840", "95936", "94866",
                "94854", "94898", "94864", "95866", "95872", "94872",
                "94876", "94871", "94857", "94865", "94870", "95941",
                "94847", "94892", "95867", "94863", "94853", "95864",
                "95874", "94855", "94861", "95833", "94874", "94859",
                "94875", "95843", "95836", "94862", "95896", "94884",
                "94903", "94878", "94894", "94905", "94906", "95837",
                "94889", "94881", "94860", "94882", "94849", "94858",
                "94856", "95907", "94949", "94891", "95901", "95913",
                "99806", "94893", "94911", "95890", "94912", "94914",
                "94933", "94913", "95904", "94935", "94930", "94908",
                "95918", "99813", "99815", "99816", "99819", "99795",
                "99809", "99810", "99811"]


def config(k):
    # pylint: disable=duplicate-code
    """

    :param k: Key value for the configuration.
    :return: value of the key.
    """
    with open(f"/configs/default/shared-data/{k}", "r", encoding="utf-8") as f:
        return f.read()


def main():
    """
    Main function to get the weather data from the BOM API.
    :return:
    """
    current_app.logger.setLevel("INFO")
    for obs in Observations:
        try:
            url = config("BOM_BASE_URL") + obs + ".json"
            current_app.logger.info(url)
            data = requests.get(url, timeout=10).json()
            current_app.logger.info(f"Harvested weather observation for {obs}")
            record = {}
            record["siteid"] = data["observations"]["data"][0]["wmo"]
            record["sitename"] = data["observations"]["data"][0]["name"]
            record["geo"] = ",".join(map(str,[
                data["observations"]["data"][0]["lat"],
                data["observations"]["data"][0]["lon"],
            ]))
            record["timestamp"] = datetime.strftime(
                datetime.strptime(
                    data["observations"]["data"][0]["local_date_time_full"], "%Y%m%d%H%M%S"
                ),
                "%Y-%m-%dT%H:%M:%SZ",
            )
            record["airtemp"] = str(data["observations"]["data"][0]["air_temp"])
            record["dewpt"] = str(data["observations"]["data"][0]["dewpt"])
            record["realhum"] = str(data["observations"]["data"][0]["rel_hum"])
            record["vis"] = data["observations"]["data"][0]["vis_km"]
            record["weather"] = data["observations"]["data"][0]["weather"]
            record["winddir"] = data["observations"]["data"][0]["wind_dir"]
            record["windspd"] = data["observations"]["data"][0]["wind_spd_kmh"]
            record["cloud"] = data["observations"]["data"][0]["cloud"]
            record["raintrace"] = data["observations"]["data"][0]["rain_trace"]

            response = requests.post(
                url="http://router.fission/enqueue/weather",
                headers={"Content-Type": "application/json"},
                data=json.dumps(record),
                timeout=10,
            )

            if response.status_code != 201:
                current_app.logger.error(f"Error: {response.status_code}")

        except Exception as e: # pylint: disable=broad-except
            current_app.logger.error(f"Error: {e}")
    return "OK"
