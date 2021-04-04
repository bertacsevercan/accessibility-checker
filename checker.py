import requests
import sys
from bs4 import BeautifulSoup
from termcolor import colored, cprint

# use Argparse for CLI
# add color
# website_url = input("Enter the website url: ")  # sys.argv[1]

img_test_url = "https://mdn.github.io/learning-area/accessibility/html/accessible-image.html"
e_commerce_test = "https://www.gittigidiyor.com"
table_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-table.html"
a_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-links.html"
bad_semantics_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-semantics.html"
good_semantics_test_url = "https://mdn.github.io/learning-area/accessibility/html/good-semantics.html"
bad_form_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-form.html"
good_form_test_url = "https://mdn.github.io/learning-area/accessibility/html/good-form.html"
session = requests.Session()  # for faster fetch
# file = open("accessibility-score.txt", "w+", encoding="utf-8")

# header is to show the program as a device when requesting
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
request = None
try:
    request = session.get(img_test_url, headers=headers)
    # raise and handle http errors
    request.raise_for_status()
except requests.exceptions.HTTPError as err:
    raise SystemExit(err)

soup = BeautifulSoup(request.content, "html.parser")
website_title = soup.title.text
score = 100  # initial score of the website


def check_img_tag():
    global score
    all_img = soup.find_all("img")
    if all_img:
        missing_alts = []
        missing_titles = []
        empty_alts = []
        for tag in all_img:
            attrs_keys = tag.attrs.keys()
            if "alt" not in attrs_keys:  # check if all img tags contain alt attr
                score -= 1
                missing_alts.append(str(tag))
            elif tag["alt"] == "":
                empty_alts.append(str(tag))
            if "title" not in attrs_keys:
                missing_titles.append(str(tag))

        if missing_alts:
            cprint("These img tags are missing 'alt' attribute:\n", "red", end=" ")
            print(" \n ".join(missing_alts))
            cprint("It's recommended to add 'alt' attribute to increase accessibility.")
        if missing_titles:
            cprint("These img tags are missing 'title' attribute:\n", "yellow", end=" ")
            print(" \n ".join(missing_titles))
            cprint("Consider adding a title attribute to increase accessibility.", "green")
        if empty_alts:
            cprint("These img tags have empty 'alt' attribute:\n", "yellow", end=" ")
            print("\n ".join(empty_alts))
            cprint("This is okay if you are using the images for decorative purposes."
                   "\nHowever, if possible you should use CSS to display images that are only decorative.", "green")


def check_a_tag():
    global score
    all_a = soup.find_all("a")
    missing_hrefs = []
    new_windows = []
    if all_a:
        for tag in all_a:
            attrs_keys = tag.attrs.keys()
            if tag["href"] == "#":
                score -= 1
                missing_hrefs.append(str(tag))
            elif "target" in attrs_keys and tag["target"] == "_blank":
                new_windows.append(str(tag))
        if missing_hrefs:
            print("These anchor tags' href attributes are '#'. Consider using a button instead:\n",
                  "\n ".join(missing_hrefs))
        if new_windows:
            print(
                "These anchor tags are redirecting to a new page, consider adding an explanation to the content such as: '(opens in a new window)':  \n",
                "\n ".join(new_windows))


def check_table_tag():  # scope, th, caption etc.
    global score
    all_table = soup.find_all("table")  # list(map(lambda x: x.contents, soup.find_all("table")))
    missing_ths = []
    missing_captions = []
    missing_scopes = []
    for table in all_table:
        if table.th is None:
            score -= 1
            missing_ths.append(str(table))
        elif table.th is not None:
            for th in table.find_all("th"):
                attrs_keys = th.attrs.keys()
                if "scope" not in attrs_keys:
                    missing_scopes.append(th)
        if table.caption is None:
            score -= 1
            missing_captions.append(str(table))

    if missing_ths:
        print("These table tags are missing 'th' child tag:\n" + " \n ".join(missing_ths))
    if missing_captions:
        print("These table tags are missing 'caption' child tag:\n" + " \n ".join(missing_captions))
    if missing_scopes:
        print("These th tags are missing 'scope' attribute:\n" + " \n ".join(missing_scopes))


def check_form_tag():  # labels
    pass


def check_language():
    attrs_keys = soup.find("html").attrs.keys()
    if "lang" not in attrs_keys:
        cprint("Html tag is missing 'lang' attribute. Therefore, the language of the document or a page element is unidentified.", "red")


cprint(website_title, attrs=['underline', 'bold'])
check_img_tag()
check_a_tag()
check_table_tag()
check_language()
cprint(f"Score: {score}", "blue")
