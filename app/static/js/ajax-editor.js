function AjaxEditor(option) {
    /*
    * ajax 修改数据对象
    * */
    this.$ = Zepto;
    this.$document = this.$(document);
    this.$ajaxError = this.$('#ajaxError');
    this.$mask = this.$('#mask');
    this.$editBtn = this.$('.edit-btn');
    this.updateFlag = false;

    // 后端开启了 csrf 保护功能，csrf_token 必须要传递
    // 通过模板语法 `{{ csrf_token() }}` 即可得到 csrf_token
    this.csrf_token = option.csrf_token;
    // 查询数据的 URL
    this.get_record_url = option.get_record_url;
    // 更新数据的 URL
    this.update_record_url = option.update_record_url;
    // 需要查询并修改数据的模型名称
    this.modelName = option.modelName;
    // 创建编辑表单的函数
    this.createEditForm = option.createEditForm;
    // 更新原始数据的函数
    this.rebuildOrigTr = option.rebuildOrigTr;

    this.$origTr = null;
    this.$formTr = null;
    this.$cancelBtn = null;
    this.$confirmBtn = null;

    this.recordId = '';
    this.recordData = null;

    this.init = function () {
        // 初始化操作，绑定事件并设置请求头
        this._beforeAjaxSend();
        this._bindEvent();
    };

    this._beforeAjaxSend = function () {
        // 设置请求头，使用 Flask-WTF 的 CSRFProtect 插件的必须步骤
        this.$.ajaxSettings.beforeSend = (xhr) => {
            xhr.setRequestHeader('X-CSRFToken', this.csrf_token);
        }
    };

    this._removeFromTr = function () {
        // 移除编辑表单列并显示原始表格列
        this.$formTr.hide();
        this.$formTr.prev().show();
        this.$origTr.css('opacity', '1');
        this.$origTr.css('transform', 'scale(1)');
        this.$formTr.remove();
    };

    this._showHideAjaxError = function (errorMsg) {
        // 显示请求校验失败或者 ajax 请求失败时的信息
        this.$ajaxError.text(errorMsg);
        this.$ajaxError.removeClass('d-none');
        this.$mask.removeClass('d-none');

        this.$mask.on('click', function () {
            // 一般来说大部分意外情况刷新页面都能解决
            window.location.reload()
        });
    };

    this._getRecord = function (recordId) {
        /*
        * 获取数据库记录的 ajax 请求
        * 该方法必须要接受一个记录的 id 值
        * */
        const data = {modelName: this.modelName, id: recordId};

        let errorMsg;

        this.$.ajax({
            type: 'POST',
            url: this.get_record_url,
            data: JSON.stringify(data),                     // 将 data 序列化成 JSON 字符串
            dataType: 'json',                               // dataType 设置好的之后后端传递的 JSON 字符串可以自动被转换
            contentType: 'application/json; charset=UTF-8', // request.get_json() 正常工作的必须设置

            success: data => {
                // 后端返回的状态码有两种
                // 1 = 记录请求成功
                // 0 = 发送的请求数据验证失败
                if (data.code) {
                    this.recordData = data.data;
                    if (this.$formTr) {
                        this._removeFromTr();
                    }
                    this.$document.trigger('getRecordDone');

                } else {
                    errorMsg = data.msg;
                }
            },

            error: (xhr, errorType, error) => {
                errorMsg = errorType + ': ' + error;
            },

            complete: () => {
                // 渲染请求的错误信息
                if (errorMsg) {
                    this._showHideAjaxError(errorMsg);
                }
            }
        });
    };

    this._updateRecord = function () {
        // 更新数据库的记录的 ajax 请求
        const $editError = this.$formTr.find('#editError');
        const $inputText = this.$formTr.find('input[type="text"]');

        // 该方法传递给后端的是表单数据的序列化字符串
        // flask 表单类可以直接验证这种序列化的字符串
        let formData = this.$formTr.find('#editForm').serialize();
        let formErrorMsg;
        let ajaxErrorMsg;

        formData += `&modelName=${this.modelName}`;

        this.$.ajax({
            type: 'POST',
            url: this.update_record_url,
            data: formData,
            dataType: 'json',

            success: data => {
                // 后端返回的状态码有三种
                // 1 = 成功
                // 2 = 表单验证错误
                // 0 = 发送的请求数据验证失败
                if (data.code === 2) {
                    formErrorMsg = data.msg
                } else if (data.code === 0) {
                    ajaxErrorMsg = data.msg;
                } else {
                    // 执行完更新操作之后，需要再从后端请求获取一次查询记录
                    this._getRecord(this.recordId);
                    // 为了避免点击编辑按钮时获取记录的 ajax 请求和更新数据结束后获取记录的 ajax 请求冲突这里设置一个标记
                    this.updateFlag = true;
                }
            },

            error: (xhr, errorType, error) => {
                ajaxErrorMsg = errorType + ': ' + error;
            },

            complete: () => {
                if (ajaxErrorMsg) {
                    // 渲染非正常错误
                    this._showHideAjaxError(ajaxErrorMsg);
                    return;
                }

                if (formErrorMsg) {
                    // 渲染表单错误提示
                    let fieldNameArr = [];
                    let fieldErrorArr = [];
                    let errorMsgStr;

                    for (let fieldName in formErrorMsg) {
                        fieldNameArr.push(fieldName);
                        fieldErrorArr.push(formErrorMsg[fieldName]);
                    }

                    errorMsgStr = fieldErrorArr.join('<br>');
                    $editError.html(errorMsgStr);
                    $editError.removeClass('d-none');

                    $inputText.each((index, elem) => {
                        const $elem = this.$(elem);
                        if (fieldNameArr.indexOf($elem.attr('name')) !== -1) {
                            $elem.addClass('is-invalid');
                        } else {
                            $elem.removeClass('is-invalid');
                        }
                    })
                }
            }
        })
    };

    this._bindEvent = function () {
        // 绑定事件

        this.$editBtn.on('click', (event) => {
            // 编辑按钮事件
            if (this.$formTr) {
                this._removeFromTr();
            }
            const $thisEditBtn = this.$(event.target);
            this.$origTr = $thisEditBtn.parents('tr');
            this.recordId = this.$origTr.data('id');
            this._getRecord(this.recordId);
        });

        this.$document.on('getRecordDone', () => {
            // 接受到 `getRecordDone` 事件后，隐藏原始列，渲染编辑表单，并给按钮绑定事件
            this.$origTr.hide();
            this.$origTr.css('opacity', '0');
            this.$origTr.css('transform', 'scale(1.1)');
            this.$formTr = this.$(this.createEditForm(this.recordData));
            this.$origTr.after(this.$formTr);


            this.$cancelBtn = this.$('#cancelBtn');
            this.$confirmBtn = this.$('#confirmBtn');

            this.$cancelBtn.on('click', () => {
                // 取消操作
                this._removeFromTr();
            });

            this.$confirmBtn.on('click', () => {
                // 点击触发更新操作
                this._updateRecord();
            });
        });

        this.$document.on('getRecordDone', () => {
            // 接受到 `getRecordDone` 事件且更新标记为 true 时重建原始数据列，并隐藏编辑表单
            if (this.updateFlag) {
                this.rebuildOrigTr(this.$origTr, this.recordData);
                this._removeFromTr();
                // 操作结束一定要把 updateFlag 的状态改为 false
                this.updateFlag = false;
            }
        })
    }
}