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
