import requests
import sys
from bs4 import BeautifulSoup

website_url = input("Enter website url: ")  # sys.argv[1]

session = requests.Session()  # for faster fetch
# file = open("accessibility-score.txt", "w+", encoding="utf-8")

# header is to show the program as a device when requesting
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

request = session.get(website_url, headers=headers)

# needs better error handling
if request.status_code == 404:
    print(f"Sorry, unable to find the website.")
    sys.exit()
elif request.status_code != 200:
    print("Something went wrong! Status code: ", request.status_code)
    sys.exit()

soup = BeautifulSoup(request.content, "html.parser")
all_img = soup.find_all("img")
for tag in all_img:
    if tag["alt"] is None:  # check if all img file contains alt tag
        print(tag)
