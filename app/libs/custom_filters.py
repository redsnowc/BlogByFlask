from jinja2.filters import do_striptags


def switch_link_tag(tag: str) -> str:
    """
    自定义过滤器
    转换链接 tag 字段的显示内容
    :param tag: 链接 tag 字段原始值
    :return: 转换后的 tag 字段显示值
    """
    tag_dict = {
        'weixin': '微信',
        'weibo': '微博',
        'douban': '豆瓣',
        'zhihu': '知乎',
        'google': '谷歌',
        'linkedin': '领英',
        'twitter': '推特',
        'facebook': '脸书',
        'github': 'Github',
        'telegram': 'Telegram',
        'other': '其它',
        'friendLink': '友情链接'
    }
    return tag_dict.get(tag)


def get_search_part(content: str, search_str: str, left_offset: int = 30, part_len: int = 260) -> str:
    """
    根据搜索内容截取文章正文中相关的内容
    :param content: 文章正文
    :param search_str: 搜索内容
    :param left_offset: 左偏移量 default = 30
    :param part_len: 截取的内容总长 default = 260
    :return: 截取后的内容
    """
    no_tag_content = do_striptags(content)
    search_position = no_tag_content.lower().find(search_str.lower())
    start_position = max(0, search_position - left_offset)
    search_part = no_tag_content[start_position: start_position + part_len]

    if search_position - left_offset > 0:
        search_part = f'....{search_part}'

    if search_position + part_len < len(no_tag_content):
        search_part = f'{search_part}....'

    search_part = search_part.replace(search_str, f'<font color="#ff3366">{search_str}</font>')
    return search_part
