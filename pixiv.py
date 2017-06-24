import re

import config
import asyncio
import aiohttp
import json
import aiofiles
from bs4 import BeautifulSoup


def get_cookies():
    cookies = {}
    with open(config.cookie_json_path) as f:
        for cookie_item in json.loads(f.read()):
            cookies[cookie_item['name']] = cookie_item['value']
    return cookies


def get_cookie_jar():
    cookie_jar = aiohttp.CookieJar()
    cookie_jar.load(config.cookie_jar_path)
    return cookie_jar


def get_page_nums(text):
    if text:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
        page_ul = soup.find('ul', class_='page-list')
        if page_ul:
            return len(page_ul.contents)
        else:
            return 1
    else:
        return 0


def get_illust_ids(text):
    if text:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
        images_list = soup.find_all('a', class_='work')
        images_url = [str(item['href']) for item in images_list]
        pattern = re.compile(r'\d+')
        illust_ids = [pattern.findall(item)[0] for item in images_url]
    else:
        illust_ids = []
    return illust_ids


def get_member_name(text):
    """
    :param text: html text from config.member_url(member_id)
    :return: member_name
    """
    if text:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
        select = soup.find('h1', class_='user')
        if select:
            return select.string
    return ''


def get_image_url(text):
    """
    :param text: html text from config.illust_url(illust_id)
    :return: (type,url) 
        type 1 for single image, the url is the image url;
        type 2 for manga illust, the url is the mange url;
        type 0 for unknown type, the url is None
    """
    if text:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
        select = soup.select('.original-image')
        if select:
            image_url = select[0]['data-src']
            return 1, image_url
        else:
            select = soup.select('.multiple')
            if select:
                return 2, None
    return 0, None


def get_manga_image_paths(text):
    """
    :param text: html text from config.manga_page_url(illust_id)
    :return: [image_urls]
    """
    pass
    # manga_page_url = config.manga_page_url(illust_id)
    # manga_html = get_text(manga_page_url)
    # manga_soup = BeautifulSoup(manga_html, 'html.parser', from_encoding='utf-8')
    # manga_select = manga_soup.select('.ui-scroll-view')
    # page_num = len(manga_select)
    # for page in range(0, page_num):
    #     manga_big_url = config.manga_big_url(illust_id, page)
    #     manga_big_html = get_text(manga_big_url)
    #     manga_big_soup = BeautifulSoup(manga_big_html, 'html.parser', from_encoding='utf-8')
    #     manga_big_select = manga_big_soup.select('img')
    #     original_image_url = manga_big_select[0]['src']
    #     t = {
    #         'image_url': original_image_url,
    #         'referer': manga_big_url
    #     }
    #     illust_info['image_url'].append(t)
    # illust_info['illust_type'] = 'manga'


def get_title(text):
    if text:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
        title = soup.head.title.string
        return title
    else:
        return None


def get_manga_pages(text):
    # html text from config.manga_url(illust_id)
    if text:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
        item_containers = soup.find_all('a', class_='full-size-container')
        if item_containers:
            manga_image_pages = [config.pixiv_url + item['href'] for item in item_containers]
            return manga_image_pages
    return []


def get_manga_image(text):
    # html text from manga_page
    if text:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
        image = soup.find('img')
        if image:
            return image['src']
    return None