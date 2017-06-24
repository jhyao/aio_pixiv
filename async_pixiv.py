import time

import config
import asyncio
import aiohttp
import aiofiles
import pixiv
import os

data = {
    'pages': 0,
    'done_pages': 0,
    'illusts': 0,
    'done_illusts': 0,
    'images': 0,
    'done_images': 0,
    'requests': 0,
    'failed_request': 0,
}


# page_list = asyncio.Queue(maxsize=config.max_page)
# illust_list = asyncio.Queue(maxsize=config.max_illust)
# download_list = asyncio.Queue(maxsize=config.max_download)


async def get_text(session: aiohttp.ClientSession, url, headers=None, timeout=5 * 60, count=0):
    data['requests'] += 1
    text = b''
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            text = await response.read()
    except (asyncio.TimeoutError, aiohttp.client_exceptions.ClientError):
        if count < 3:
            print('failed, retry.')
            text = await get_text(session, url, headers, timeout, count + 1)
        else:
            data['failed_request'] += 1
    return text


async def handle_member(session, member_id, loop=None):
    print('handling member', member_id)
    loop = loop or asyncio.get_event_loop()
    member_url = config.member_illust_url(member_id)
    text = await get_text(session, member_url)
    text = text.decode('utf-8')
    member_name = pixiv.get_member_name(text)
    member_info = (member_id, member_name)
    page_nums = pixiv.get_page_nums(text)
    page_coro_list = []
    for page in range(1, page_nums + 1):
        page_url = config.member_illust_page(member_id, page)
        # await page_list.put((page_url, member_info))
        page_coro = handle_page(session, page_url, member_info)
        page_coro_list.append(page_coro)
    if page_coro_list:
        await asyncio.wait(page_coro_list)


async def handle_page(session, page_url, member_info, loop=None):
    """
    :param member_info: (member_id, member_name)
    """
    data['pages'] += 1
    print('handling page', page_url)
    loop = loop or asyncio.get_event_loop()
    text = await get_text(session, page_url)
    text = text.decode('utf-8')
    illust_ids = pixiv.get_illust_ids(text)
    illust_coro_list = []
    for illust_id in illust_ids:
        # await illust_list.put((item, member_info))
        illust_coro = handle_illust(session, illust_id, member_info)
        illust_coro_list.append(illust_coro)
    if illust_coro_list:
        await asyncio.wait(illust_coro_list)
    data['done_pages'] += 1
    print('complete page %d/%d' % (data['done_pages'], data['pages']), page_url)


async def handle_illust(session, illust_id, member_info, loop=None):
    """
        :param member_info: (member_id, member_name)
    """
    data['illusts'] += 1
    print('handling illust', illust_id)
    loop = loop or asyncio.get_event_loop()
    illust_url = config.illust_url(illust_id)
    text = await get_text(session, illust_url)
    image_info = pixiv.get_image_url(text)
    image_coro_list = []
    if image_info[0] == 1:
        image_coro = handle_image(session, image_info[1], illust_url, config.store_path(*member_info))
        image_coro_list.append(image_coro)
    elif image_info[0] == 2:
        manga_url = config.manga_url(illust_id)
        text = await get_text(session, manga_url)
        manga_pages = pixiv.get_manga_pages(text)
        for page in manga_pages:
            text = await get_text(session, page)
            image_url = pixiv.get_manga_image(text)
            if image_url:
                image_coro = handle_image(session, image_url, page, config.store_path(*member_info))
                image_coro_list.append(image_coro)
    else:
        image_coro_list = []
    if image_coro_list:
        await asyncio.wait(image_coro_list)
    data['done_illusts'] += 1
    print('complete illust %d/%d' % (data['done_illusts'], data['illusts']), illust_id)


async def handle_image(session, image_url, referer=None, store_path=None, cover=False, timeout=5 * 60, loop=None):
    loop = loop or asyncio.get_event_loop()
    type = 'complete'
    data['images'] += 1
    print('handling image', image_url)
    if not store_path:
        store_path = config.default_store_path
    if not os.path.isdir(store_path):
        try:
            os.mkdir(store_path)
        except:
            print('mkdir failed', store_path)
            type = 'failed'
    filename = str(image_url).split('/')[-1]
    filepath = store_path + '\\' + filename
    if os.path.exists(filepath) and not cover:
        type = 'dld'
    else:
        headers = {
            # ':authority': 'i.pximg.net',
            # ':method': 'GET',
            # ':scheme': 'https',
            # 'accept': 'image/webp,image/*,*/*;q=0.8',
            # 'accept-encoding': 'gzip, deflate, sdch, br',
            # 'accept-language': 'en,zh-CN;q=0.8,zh;q=0.6',
            'referer': referer,
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        text = await get_text(session, image_url, headers, timeout)
        if text:
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(text)
            type = 'success'
        else:
            type = 'failed'
    data['done_images'] += 1
    print('image %s %d/%d' % (type, data['done_images'], data['images']), image_url)


async def check_cookie():
    print('checking...')
    text = None
    cookie_jar = pixiv.get_cookie_jar()
    async with aiohttp.ClientSession(cookie_jar=cookie_jar, headers=config.header) as session:
        text = await get_text(session, config.pixiv_url)
        async with aiofiles.open('pixiv.html', 'wb') as f:
            await f.write(text)
        cookie_jar.save(config.cookie_jar_path)
    title = pixiv.get_title(text)
    if title == '[pixiv]':
        print('check pass')
    else:
        print('No cookie available!Input 0 to exit.')
        print('Please update your cookie file from chrome.After that please press Enter to continue.')
        choice = input('Enter/Exit:')
        if choice == '0':
            exit()
        else:
            async with aiohttp.ClientSession(cookies=pixiv.get_cookies(), headers=config.header) as session:
                cookie_jar = session.cookie_jar
                cookie_jar.save()
                check_cookie()
    return cookie_jar


async def start(loop=None):
    loop = loop or asyncio.get_event_loop()
    cookie_jar = await check_cookie()
    async with aiohttp.ClientSession(cookie_jar=cookie_jar, headers=config.header) as session:
        member_coro = handle_member(session, 5053454)
        await asyncio.wait([member_coro])
        # illust_coro = handle_illust(session, 50799681, (111111, 'unknown'))
        # await asyncio.wait([illust_coro])

start_time = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(start(loop))
loop.close()
cost_time = time.time()-start_time
print('cost time:',round(cost_time, 2), 'seconds')
print('avreage download:',round(data['done_images']/cost_time*60, 2),'images pre minute')
