import json
import time
import re

from urllib.parse import urlparse, urljoin
from werkzeug.utils import secure_filename

from flask_wtf import FlaskForm
from flask import current_app, request, redirect, url_for
from werkzeug import Response
from werkzeug.datastructures import ImmutableMultiDict
from typing import Union


def get_form_error_items(form: 'FlaskForm') -> tuple:
    """
    获取表单验证失败的字段名称及错误信息
    :param form: 表单类实例
    :return: 验证失败的字段名称列表和错误信息列表组成的元祖
    """
    form_error_items = form.errors.items()
    fields_name = []
    fields_errors = []
    if form_error_items:
        for field_name, errors in form_error_items:
            fields_name.append(field_name)
            fields_errors += errors
    return fields_name, fields_errors


def check_ajax_request_data(data: Union[dict, ImmutableMultiDict], target_model_name: str):
    """
    ajax 请求校验函数
    校验 ajax 请求发送的数据是否有效
    只能接受标准的 json 对象转换的 dict 或者表单序列化字符串转换的 ImmutableMultiDict
    要求数据中必须传递需要查询的数据库模型名称以及需要查询的 id
    :param data: ajax 请求的数据
    :param target_model_name: 目标查询数据表模型名称
    :return: 请求数据有误则返回包含错误码及提示，数据无误则返回数据库查询记录
    """
    failed_data = {'code': 0, 'msg': ''}

    # 判空
    if not data:
        failed_data['msg'] = '未接收到任何请求数据'
        return json.dumps(failed_data)

    # 如果 data 类型有误则直接返回错误提示
    if not (type(data) == dict or type(data) == ImmutableMultiDict):
        failed_data['msg'] = 'AJAX 请求数据格式不正确'
        return json.dumps(failed_data)

    model_name = data.get('modelName')
    data_id = data.get('id')

    # 判断 model_name 空值
    if not model_name:
        failed_data['msg'] = '未指定查询模型'
        return json.dumps(failed_data)

    # 判断 data_id 空值
    if not data_id:
        failed_data['msg'] = '未指定查询 id'
        return json.dumps(failed_data)

    # 判断 data_id 是否为整数
    if not type(data_id) == int:
        if not str(data_id).isdigit():
            failed_data['msg'] = '查询 id 不是数字'
            return json.dumps(failed_data)

    # 将 data_id 转换成整数
    data_id = int(data_id)

    # 获取配置文件中的 MODELS 配置项，它是一个字典 'ModelName': Model
    models = current_app.config['MODELS']

    # 判断指定的查询模型是否存在
    model = models.get(model_name)
    if not model:
        failed_data['msg'] = '指定查询模型不存在'
        return json.dumps(failed_data)

    # 判断模型名称是否与目标查询模型名称相符
    if model.__name__ != target_model_name:
        failed_data['msg'] = '指定查询模型与该查询不符'
        return json.dumps(failed_data)

    # 判断数据库查询记录是否存在
    record = model.query.get(data_id)
    if not record:
        failed_data['msg'] = '未查找到任何记录'
        return json.dumps(failed_data)

    return record


def is_safe_url(target: str) -> bool:
    """
    校验 URL 是否属于本站
    :param target: 需要校验的 URL
    :return True or False
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default_endpoint: str = 'web.index', **kwargs) -> Response:
    """
    执行跳转操作，可用于各种 POST 操作之后的跳转
    :param default_endpoint: 默认 endpoint，如果获取不到 `next` 以及 `request.referrer` 或 URL 校验失败之后的默认跳转页面
    :param **kwargs 视图可能所需的参数
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default_endpoint, **kwargs))


def allowed_file(filename: str) -> bool:
    """
    校验文件格式是否被允许
    :param filename: 需要校验的文件名
    :return: True or False
    """
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def avoided_file_duplication(filename: str) -> str:
    """
    给文件名添加 UNIX 时间戳避免文件名重复
    :param filename: 需要处理的文件名
    :return: 处理后的文件名
    """
    unix_time_list = str(time.time()).split('.')
    second = unix_time_list[0]
    millisecond = unix_time_list[1]
    extension = filename.rsplit('.', 1)[1]
    prefix = filename.rsplit('.', 1)[0]
    filename = f'{prefix}s{second}ms{millisecond}.{extension}'
    return secure_filename(filename)


def remove_html_tag(html_str: str) -> str:
    """
    去除 HTML 标记
    :param html_str: HTML 字符串
    :return: 无 HTML 标记字符串
    """
    regex = re.compile('<[^>]*>')
    return regex.sub('', html_str).replace('\n', '').replace('\r', '').replace(' ', '')
