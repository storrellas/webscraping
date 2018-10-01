from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import datetime
import sys
import jsonlines


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


def generate_item(row, day):
    item = []
    for j, td in enumerate(row.select('td')):
        if j == 0:
            index = td.text.rfind(' ')
            item.append(td.text[0:index])
            item.append(td.text[index+1:])
        else:
            str = td.text.replace('\n','')
            item.append(str)

    # Get formatted year
    try:
        year = int(item[-1])
        date = datetime.datetime(year, 1, 1) + datetime.timedelta(day - 1)
        # NOTE: This does not work with dates <1900
        #item.insert(0, date.strftime("%Y%m%d"))
        birthdate = date.isoformat()[0:10]
        birthdate = birthdate.replace('-','')
        item.insert(0, birthdate)
    except:
        item.insert(0, '')
    item = item[:-1]

    return item

if __name__ == "__main__":


    filename = 'output.jsonl'
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

    # Iterate over links
    writer = jsonlines.open(filename, mode='w')
    for i, date_link in enumerate(link_list):

        # Get HTML content
        day = i + 1
        print("Processing day ", day, " of year")

        #############################
        # if day != 45:
        #     continue
        #############################

        # Get Raw HTML
        raw_html = simple_get(base_url + date_link)

        # Scrap table
        html = BeautifulSoup(raw_html, 'html.parser')
        for j, tr in enumerate(html.select('.bq_left table tbody tr')):
            item_list = []
            item = generate_item(tr, day)
            writer.write(item)


    print("Your results should be in ", filename)
    writer.close()


    print("-- Script End --")
