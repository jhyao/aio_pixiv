# coding:utf-8
import json

import re

max_page = 5
max_illust = 30
max_download = 30

pixiv_url = 'https://www.pixiv.net'
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'referer': 'http://www.pixiv.net'
}

cookie_json_path = 'cookie_json.txt'
cookie_jar_path = 'cookie_jar.txt'
default_store_path = 'G:\\pixiv'


def member_url(member_id):
    return 'https://www.pixiv.net/member.php?id=' + str(member_id)


def member_illust_url(member_id):
    return 'https://www.pixiv.net/member_illust.php?id=' + str(member_id)


def member_bookmark_url(member_id):
    return 'https://www.pixiv.net/bookmark.php?id=' + str(member_id)


def illust_url(illust_id):
    return 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + str(illust_id)


def member_illust_page(member_id, page):
    return 'https://www.pixiv.net/member_illust.php?id=' + str(member_id) + '&type=all&p=' + str(page)


def manga_url(illust_id):
    return 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=' + str(illust_id)


def manga_page_url(illust_id, page):
    return 'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=' + str(illust_id) + '&page=' + str(page)


def store_path(member_id, member_name=None):
    if not member_name:
        member_name = ''
    pattern = re.compile('[\\/:?<>*"|]')
    name = re.sub(pattern, '-', member_name)
    return 'G:\\pixiv\\' + str(member_id) + '-' + name


'''
参数说明
word
s_mode=s_tag(标签)|s_tc(标题简介)|s_tag_full(完全一致) 默认s_tag
r_18=1(只有r18)
ratio=0.5(横版)|-0.5(竖版)|0(正方)
blt=最小收藏数,bgt=最大收藏数
order=popular_d(按热门度排序)|date(按旧排序) 默认空(按新排序)
scd=搜索开始日期
p=页数

'''


def search_url(word, page=1, ratio='', blt='0', bgt='*', order='popular_d', scd=''):
    return 'http://www.pixiv.net/search.php?word=' + str(word) + '&order=' + str(order) + '&ratio=' + str(
        ratio) + '&blt=' + str(blt) + '&p=' + str(page)


def member_focus_url(member_id, page, rest='show'):
    return 'http://www.pixiv.net/bookmark.php?type=user&id=' + str(member_id) + '&rest=' + rest + '&p=' + str(page)
