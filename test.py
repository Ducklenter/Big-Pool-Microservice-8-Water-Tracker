import requests
import time

BASE_WATER = "http://localhost:5001"
BASE_REMINDER = "http://localhost:5000"
USER = "test_user"

if __name__ == "__main__":

    print("Default goal: 2000 ml")
    r = requests.get(BASE_WATER + "/goal/" + USER)
    print(r.json())

    print("Make custom goal of 500 ml")
    r = requests.put(BASE_WATER + "/goal", json={"user_id": USER, "goal_ml": 500})
    print(r.json())

    print("Print custom goal of 500")
    r = requests.get(BASE_WATER + "/goal/" + USER)
    print(r.json())

    print("Log 1000 ml intake")
    r = requests.post(BASE_WATER + "/intake", json={"amount_ml": 1000, "user_id": USER})
    print(r.json())
