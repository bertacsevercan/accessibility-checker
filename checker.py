import requests
import argparse
import csv
import sys
import traceback
from os import mkdir
from re import search
from bs4 import BeautifulSoup
from termcolor import colored, cprint

description = "This program checks the given website's accessibility \
provided by the W3C guidelines and outputs a score from 0-100. Note that, this is not a definite tool for checking accessibility \
therefore the results should be treated as suggestions. Also, this program doesn't check \
WAI-ARIA attributes, it checks for other HTML semantics. \
Sources: https://www.w3.org/WAI/WCAG21/quickref/?showtechniques=121#identify-input-purpose, https://developer.mozilla.org/en-US/docs/Web/Accessibility"

# parser for CLI commands
parser = argparse.ArgumentParser(description=description)
parser.add_argument("url", help="enter the website url.")
parser.add_argument("-n", "--name", help="enter the name of the website.")
parser.add_argument("-s", "--short", action="store_true", help="show a short version of the result with highlights.")
parser.add_argument("-o", "--score", action="store_true", help="show only the score.")
parser.add_argument("-c", "--csv", action="store_true", help="write the scores as csv.")

args = parser.parse_args()

uni_test_url = "https://www.bilgi.edu.tr/tr/"
img_test_url = "https://mdn.github.io/learning-area/accessibility/html/accessible-image.html"
e_commerce_test = "https://www.gittigidiyor.com"
bad_table_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-table.html"
good_table_test_url = "https://github.com/mdn/learning-area/blob/master/css/styling-boxes/styling-tables/punk-bands-complete.html"
a_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-links.html"
bad_semantics_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-semantics.html"
good_semantics_test_url = "https://mdn.github.io/learning-area/accessibility/html/good-semantics.html"
bad_form_test_url = "https://mdn.github.io/learning-area/accessibility/html/bad-form.html"
good_form_test_url = "https://mdn.github.io/learning-area/accessibility/html/good-form.html"

session = requests.Session()  # for faster fetch

# header is to show the program as a device when requesting
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
request = None
try:
    request = session.get(args.url, headers=headers)
    # raise and handle http errors
    request.raise_for_status()
except requests.exceptions.HTTPError as err:
    raise SystemExit(err)

soup = BeautifulSoup(request.content, "html.parser")
score = 100  # initial score of the website
title = ""
c_success = "green"
c_danger = "red"
c_warning = "yellow"
c_primary = "blue"
c_secondary = "cyan"
c_alert = "magenta"
checklist = {
    "has_issue_headings": False, "has_issue_regions": False, "has_issue_image": False, "has_issue_anchor": False,
    "has_issue_table": False, "has_issue_form": False, "has_issue_lang": False, "has_issue_title": False
}


# not checking for wai-aria attrs

def check_heading_tags():
    global score
    h1 = soup.find("h1") is None
    h2 = soup.find("h2") is None
    h3 = soup.find("h3") is None
    h4 = soup.find("h4") is None
    h5 = soup.find("h5") is None
    h6 = soup.find("h6") is None

    if h1 and h2 and h3 and h4 and h5 and h6:
        score -= 10
        checklist["has_issue_headings"] = True
        if not args.score:
            cprint("The page has no headings!\n", c_danger, end="")
            cprint("Headings (<h1>-<h6>) provide important document structure and helps assistive technology users.\n",
                   c_success)


def check_page_regions():
    global score
    header = soup.find("header") is None
    nav = soup.find("nav") is None
    main = soup.find("main") is None
    footer = soup.find("footer") is None
    aside = soup.find("aside") is None

    if header and nav and main and footer and aside:
        score -= 10
        checklist["has_issue_regions"] = True
        if args.score:
            cprint("The page has no regions!\n", c_danger, end="")
            cprint(
                "Mark up different regions of the web page, so that they can be identified by web browsers and assistive technologies.\n",
                c_success)


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
                checklist["has_issue_image"] = True
                missing_alts.append(str(tag))
            elif tag["alt"] == "":
                score -= 1
                checklist["has_issue_image"] = True
                empty_alts.append(str(tag))
            if "title" not in attrs_keys:
                score -= 1
                checklist["has_issue_image"] = True
                missing_titles.append(str(tag))

        if not args.score:
            if missing_alts:
                cprint("These img tags are missing 'alt' attribute:\n", c_danger, end=" ")
                None if args.short else print("\n ".join(missing_alts))
                cprint("It's recommended to add 'alt' attribute to increase accessibility.", c_success)
            if missing_titles:
                cprint("These img tags are missing 'title' attribute:\n", c_danger, end=" ")
                None if args.short else print("\n ".join(missing_titles))
                cprint("Consider adding a title attribute to increase accessibility.", c_success)
            if empty_alts:
                cprint("These img tags have empty 'alt' attribute:\n", c_danger, end=" ")
                None if args.short else print("\n ".join(empty_alts))
                cprint("This is okay if you are using the images for decorative purposes."
                       "\nHowever, if possible it's recommended to use CSS to display images that are only decorative.",
                       c_success)


def check_a_tag():
    global score
    all_a = soup.find_all("a")
    missing_hrefs = []
    new_windows = []
    bad_links = []
    if all_a:
        for tag in all_a:
            attrs_keys = tag.attrs.keys()
            if "href" in attrs_keys:
                if tag["href"] == "#":
                    score -= 1
                    checklist["has_issue_anchor"] = True
                    missing_hrefs.append(str(tag))
                elif "target" in attrs_keys and tag["target"] == "_blank":
                    new_windows.append(str(tag))
            if tag.string and "click here" in tag.string:
                score -= 1
                checklist["has_issue_anchor"] = True
                bad_links.append(str(tag))

        if not args.score:
            if missing_hrefs:
                cprint("These anchor tags' href attributes are '#':\n", c_danger, end=" ")
                None if args.short else print("\n ".join(missing_hrefs))
                cprint("If you are not using anchor tags for navigation consider using a button instead.", c_success)

            if new_windows:
                cprint(
                    "These anchor tags are redirecting to a new page:\n", c_warning, end=" ")
                None if args.short else print("\n ".join(new_windows))
                cprint("Consider adding an explanation to the content such as: '(opens in a new window)'.", c_success)

            if bad_links:
                cprint(
                    "These anchor tags contain non-descriptive content message such as: 'click here':\n", c_warning,
                    end=" ")
                None if args.short else print("\n ".join(bad_links))
                cprint(
                    "Make sure your links' content messages make sense out of context, read on their own, as well as in the context of the paragraph they are in.",
                    c_success)


def check_table_tag():
    global score
    all_table = soup.find_all("table")  # list(map(lambda x: x.contents, soup.find_all("table")))
    missing_ths = []
    missing_captions = []
    missing_scopes = []
    for table in all_table:
        if table.th is None:
            score -= 1
            checklist["has_issue_table"] = True
            missing_ths.append(str(table))
        elif table.th is not None:
            for th in table.find_all("th"):
                attrs_keys = th.attrs.keys()
                if "scope" not in attrs_keys:
                    score -= 1
                    checklist["has_issue_table"] = True
                    missing_scopes.append(str(th))
        if table.caption is None:
            score -= 1
            checklist["has_issue_table"] = True
            missing_captions.append(str(table))

    if not args.score:
        if missing_ths:
            cprint("These table tags are missing 'th' child tag:\n", c_danger, end=" ")
            None if args.short else print("\n ".join(missing_ths))
            cprint("'th' tag helps screen readers to identify table content better.", c_success)
        if missing_captions:
            cprint("These table tags are missing 'caption' child tag:\n", c_danger, end=" ")
            None if args.short else print("\n ".join(missing_captions))
            cprint(
                "Captions act as alt text for a table, giving a screen reader user a useful quick summary of the table's contents.",
                c_success)
        if missing_scopes:
            cprint("These th tags are missing 'scope' attribute:\n", c_danger, end=" ")
            None if args.short else print("\n ".join(missing_scopes))
            cprint("Scopes help a screen reader user to associate rows or columns together as groupings of csv.",
                   c_success)


def check_form_tag():  # decrease score according to input numbers for labels.
    global score
    all_form = soup.find_all("form")
    missing_labels = []
    labels = []
    inputs = []
    mismatch_labels = []
    mismatch_inputs = []
    for form in all_form:
        if form.label is None:
            score -= 1
            checklist["has_issue_form"] = True
            form_split = str(form).split("\n")
            opening_tag = form_split[0]
            closing_tag = form_split[len(form_split) - 1]
            missing_labels.append(f"{opening_tag} ... {closing_tag}")
        elif form.label is not None:
            for label in form.find_all("label"):
                labels.append(label)
            for _input in form.find_all("input"):
                inputs.append(_input)
            if len(labels) == len(inputs):
                for i in range(len(labels)):
                    if "for" in labels[i].attrs.keys() and "id" in inputs[i].attrs.keys():
                        if labels[i]["for"] != inputs[i]["id"]:
                            score -= 1
                            checklist["has_issue_form"] = True
                            mismatch_labels.append(str(labels[i]))
                            mismatch_inputs.append(str(inputs[i]))
            else:
                is_labels_more = len(labels) > len(inputs)
                score -= len(labels) if is_labels_more else len(inputs)
                checklist["has_issue_form"] = True
                for i in range(len(labels)):
                    mismatch_labels.append(str(labels[i]))
                for i in range(len(inputs)):
                    mismatch_inputs.append(str(inputs[i]))

    if not args.score:
        if missing_labels:
            cprint("These forms are missing the labels for inputs:", c_danger)
            None if args.short else print("\n".join(missing_labels))
            cprint(
                "To associate the label unambiguously with the form input and make it clear how to fill it in, consider adding label tags.",
                c_success)
        if mismatch_labels and mismatch_inputs:
            cprint("These forms' labels' 'for' attributes don't match with inputs' 'id' attribute:", c_danger)
            if not args.short:
                for i in range(len(mismatch_labels)):
                    print(" " + mismatch_labels[i])
                for i in range(len(mismatch_inputs)):
                    print(" " + mismatch_inputs[i])
            cprint(
                "To associate the <label> with an <input> element, you need to give the <input> an 'id' attribute."
                "\nThe <label> then needs a 'for' attribute whose value is the same as the input's 'id'.",
                c_success)


def check_language():
    global score
    try:
        html = soup.find("html").attrs
    except AttributeError:
        score -= 10
        checklist["has_issue_lang"] = True
        None if args.score else cprint(
            "Html tag is missing. It is recommended that the inner tags should be wrapped with '<html>'.",
            c_danger)
        return None
    attrs_keys = html.keys()
    if "lang" not in attrs_keys:
        score -= 10
        checklist["has_issue_lang"] = True
        None if args.score else cprint(
            "Html tag is missing 'lang' attribute. Therefore, the language of the document  is unidentified.",
            c_danger)
    else:
        return html["lang"]


def check_title():
    global score
    global title
    if soup.title is None:
        title = "Unknown"
        score -= 10
        checklist["has_issue_title"] = True
        None if args.score else cprint(
            "It is important in each HTML document to include a <title> that describes the page's purpose.",
            c_danger)
    else:
        title = soup.title.text
    website_title = colored(title, c_alert, attrs=['underline', 'bold'])
    cprint("Title: " + website_title + "\n", c_secondary)


def show_score():
    global score
    color = ""
    message = "May needs some work!"
    if score >= 70:
        color = c_success
        message = "Looks good!"
    elif score >= 50:
        color = c_primary
    elif score >= 30:
        color = c_warning
    elif score < 30:
        color = c_danger
    if score < 0:
        score = 0
    print()
    cprint(message, c_secondary)
    cprint(f"Score: {score}", color, "on_grey")


def create_csv_dir():
    dir_name = "csv"
    try:
        # Create target Directory
        mkdir(dir_name)
        print("Directory", dir_name, "created.")
    except FileExistsError:
        print("Directory", dir_name, "already exists.")


def write_csv():
    first_row = []
    heading_list = ["Name", "Score", "Language", "Domain"]
    heading_list.extend(checklist.keys())
    try:
        with open('csv/web-accessibility.csv', 'r', newline='', encoding="utf-8") as file:
            reader = csv.reader(file)
            first_row = next(reader)
    except FileNotFoundError:
        print("Creating csv file...")

    if args.csv:
        # regex for capturing top-level domain
        regex = r"\.[^.]{2,3}(?:\.[^.]{2,3})?(?:$|/)"
        domain = search(regex, args.url).group()
        checklist_values = list(checklist.values())
        csv_content = [args.name or title.strip(), score, check_language(), domain]
        csv_content.extend(checklist_values)
        with open('csv/web-accessibility.csv', 'a+', newline='') as file:
            writer = csv.writer(file)
            None if first_row == heading_list else writer.writerow(heading_list)
            writer.writerow(csv_content)


def collect_err(e):
    format_url = f"-url: {args.url}\n"
    lines = [format_url, e]
    with open('exceptions.txt', 'a+') as file:
        file.writelines(lines)


try:
    create_csv_dir()
    None if not args.name else cprint("Name: " + args.name, c_warning, "on_grey")
    check_title()
    check_language()
    check_heading_tags()
    check_page_regions()
    check_img_tag()
    check_a_tag()
    check_table_tag()
    check_form_tag()
    show_score()
    write_csv()
except Exception as err:
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
    format_err = ''.join(tb.format()) + "\n"
    cprint("Error occurred: " + err.__class__.__name__, c_danger)
    collect_err(format_err)
