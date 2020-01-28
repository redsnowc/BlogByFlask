function createLinkEditForm(recordData) {
    /**
     * 创建编辑表单
     * @param: recordData 记录数据
     */
    return `<tr id="formTr">
              <td colspan="5">
                <form action="#" method="post" id="editForm" class="form-inline">
                  <input type="hidden" name='id' value="${recordData.id}">
                  <label class="sr-only" for="editLinkName">链接名称</label>
                  <input class="form-control my-1 mr-sm-2"
                         type="text" value="${recordData.name}"
                         placeholder="链接名称" name="name" id="editLinkName">
                  <label class="sr-only" for="editLinkUrl">链接地址</label>
                  <input class="form-control my-1" 
                         type="text" value="${recordData.url}"
                         placeholder="链接地址" name="url" id="editLinkUrl">
                  <label class="my-1 mr-sm-2 ml-2" for="editLinkTag">标签</label>
                  <select class="custom-select my-1 mr-sm-2" id="editLinkTag" name="tag" data-selectedValue="${recordData.tag}">
                    <option value="weixin">微信</option>
                    <option value="weibo">微博</option>
                    <option value="douban">豆瓣</option>
                    <option value="zhihu">知乎</option>
                    <option value="google">谷歌</option>
                    <option value="linkedin">领英</option>
                    <option value="twitter">推特</option>
                    <option value="facebook">脸书</option>
                    <option value="github">Github</option>
                    <option value="telegram">Telegram</option>
                    <option value="other">其它</option>
                    <option value="friendLink">友情链接</option>
                  </select>
                  <button type="button" class="btn btn-light mr-2 my-1" id="cancelBtn">取消更新</button>
                  <button type="button" class="btn btn-info my-1" id="confirmBtn">更新链接</button>
                </form>
                <div class="text-danger new-category-error small d-none inline-form-edit-error" id="editError"></div>
              </td>
            </tr>`
}

function rebuildLinkOrigTr($origTr, recordData) {
    /**
     * 重建数据展示的列
     * @param: $origTr 初始的数据展示列
     * @param: recordData 记录数据
     */
    const $td = $origTr.find('td');
    $td.each(function (index) {
        // 更新链接数据第一栏中的链接 URL 以及链接名
        if (index === 0) {
            const aTag = this.firstElementChild;

            aTag.setAttribute('href', recordData.url);
            aTag.innerText = recordData.name;
        }
        // 更新标签
        if (index === 1) {
            let tagName;
            switch (recordData.tag) {
                case 'weixin': tagName = '微信';
                break;
                case 'weibo': tagName = '微博';
                break;
                case 'zhihu': tagName = '知乎';
                break;
                case 'douban': tagName = '豆瓣';
                break;
                case 'google': tagName = '谷歌';
                break;
                case 'linkedin': tagName = '领英';
                break;
                case 'twitter': tagName = '推特';
                break;
                case 'facebook': tagName = '脸书';
                break;
                case 'github': tagName = 'Github';
                break;
                case 'telegram': tagName = 'Telegram';
                break;
                case 'other': tagName = '其它';
                break;
                case 'friendLink': tagName = '友情链接';
            }
            this.innerText = tagName;
        }
    })
}

(function ($) {
    // 动态选中链接标签的原始选项
    $(document).on('editFormCreated', function () {
        const $editLinkTag = $('#editLinkTag');
        if ($editLinkTag) {
            const selectedValue = $editLinkTag.data('selectedvalue');
            $editLinkTag.find('option').each(function () {
                const $this = $(this);
                if ($this.val() === selectedValue) {
                    $this.attr('selected', true);
                }
            })
        }
    })
})(Zepto);