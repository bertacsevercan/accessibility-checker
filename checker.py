import requests
import sys
from bs4 import BeautifulSoup

website_url = input("Enter the website url: ")  # sys.argv[1]

session = requests.Session()  # for faster fetch
# file = open("accessibility-score.txt", "w+", encoding="utf-8")

# header is to show the program as a device when requesting
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
request = None
try:
    request = session.get(website_url, headers=headers)
    # handle http errors
    request.raise_for_status()
except requests.exceptions.HTTPError as err:
    raise SystemExit(err)

soup = BeautifulSoup(request.content, "html.parser")
all_img = soup.find_all("img")
print(soup.prettify())  # soup.title.text  => get the name/title of the website
for tag in all_img:
    attrs_keys = tag.attrs.keys()
    if "alt" not in attrs_keys:  # check if all img tags contain alt attr
        print(tag)
