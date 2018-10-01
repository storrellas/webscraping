from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import datetime


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


if __name__ == "__main__":
    base_url = 'https://www.brainyquote.com'
    print("-- Script init --")
    raw_html = simple_get(base_url + '/birthdays/')
    html = BeautifulSoup(raw_html, 'html.parser')

    # Get links from page
    link_list = []
    for i, a in enumerate(html.select('.bq_calday a')):
        link_list.append(a['href'])

    # Generated link list
    print(len(link_list))

    day = 1

    # Treat first request
    raw_html = simple_get(base_url + a['href'])

    # Scrap table
    html = BeautifulSoup(raw_html, 'html.parser')
    for i, tr in enumerate(html.select('.bq_left table tbody tr')):
        item = []
        print("-- item --")
        for j, td in enumerate(tr.select('td')):
            if j == 0:
                index = td.text.rfind(' ')
                item.append(td.text[0:index])
                item.append(td.text[index+1:])
            else:
                str = td.text.replace('\n','')
                item.append(str)

        # Get formatted year
        year = int(item[-1])
        date = datetime.datetime(year, 1, 1) + datetime.timedelta(day - 1)
        print(date)
        print(date.strftime("%Y%m%d"))
        item.insert(0, date.strftime("%Y%m%d"))
        print(item)
        item = item[:-1]

        if i == 2:
            break




    print("-- Script End --")
