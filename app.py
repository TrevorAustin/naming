import json, requests
from BeautifulSoup import BeautifulSoup
from flask import Flask, request


app = Flask(__name__)

@app.route('/')
def homepage():
    return open('templates/homepage.html').read()

@app.route('/api/')
def api():

    # grab the name they're searching for
    name = request.args.get('name')
    name = str(name)

    data = []
    name_options = build_name_options(name)
    for name_option in name_options:

        option_data = lookup_info(name_option)
        option_data["option"] = name_option
        data.append(option_data)

    response = json.dumps(data, indent=1)
    resp_headers = {"Content-Type:": "application/json"}
    return (response, 200, resp_headers)


def build_name_options(name):
    """takes a single name and returns common variations on it"""
    return [name]
    prefixes = ["", "get", "try"]
    suffixes = ["", "app", "co"]

    perms = []
    for p in prefixes:
        for s in suffixes:
            perms.append(p + name + s)

    return perms


def lookup_info(option):
    """takes a potential naming option and looks up info about it"""

    """
    other sources to search:
    - USPTO
    """

    domainr_response = requests.get("https://domai.nr/api/json/search?q=" + option).json()
    other_domains = []
    com_is_available = None
    com_register = ""
    for result in domainr_response.get("results", []):
        if result.get("path") != "":
            continue  # no one uses those path hacks...

        if result.get("domain", "").endswith(".com"):
            com_is_available = result.get("availability") == "available"
            if com_is_available:
                com_register = result.get("register_url")
        elif result.get("availability") == "available":
            other_domains.append({
                "domain": result.get("domain"),
                "register": result.get("register_url")
                })


    return {
        "com_is_available": com_is_available,
        "com_register": com_register,
        "other_domains": other_domains,
        "twitter_is_available": requests.get("https://twitter.com/" + option).status_code == 404,
        "facebook_is_available": requests.get("https://www.facebook.com/" + option).status_code == 404,
        # "google_results": scrape_google(option),
    }

    return []


def scrape_google(keyword):

    url = "http://www.google.com/search?q={term}".format(
        term=keyword.strip().replace(" ", "+"),
    )

    # spoof some headers
    headers = {
        "user-agent": "Naming Bot",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-charset": "utf-8",
        "accept-encoding": "gzip,deflate,sdch",
        "accept-language": "en-US,en",
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text)

    search_results = soup.findAll("li", "g")
    results = []
    for search_result in search_results:

        try:
            anchor = search_result.find("h3", "r").find("a")
            results.append({
                "link": anchor.get("href", ""),
                "title": anchor.renderContents(),
                "desc": search_result.find("span", "st").renderContents(),
                "disp_url": search_result.find("cite").renderContents()
            })
        except:
            continue

    return results


if __name__ == '__main__':
    app.debug = True
    app.run()