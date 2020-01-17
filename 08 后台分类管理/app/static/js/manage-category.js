function createCategoryEditForm(recordData) {
    /**
     * 创建编辑表单
     * @param: recordData 记录数据
     */
    return `<tr id="formTr">
              <td colspan="5">
                <form class="form-inline d-flex align-items-center category-form" action="#" method="post" id="editForm">
                  <input type="hidden" name='id' value="${recordData.id}">
                  <div class="form-group">
                    <label>
                      <input type="text" class="form-control" id="editInputName" value="${recordData.name}" name='name' placeholder="分类名">
                    </label>
                  </div>
                  <div class="form-group mx-sm-3">
                    <label>
                      <input type="text" class="form-control" id="editInputAlias" value="${recordData.alias ? recordData.alias : ''}" name='alias' placeholder="别名">
                    </label>
                  </div>
                  <div class="form-group mx-2">
                    <label class="form-check-label">
                      <input type="checkbox" class="form-check-inline" ${recordData.show ? 'checked' : ''} name='show'>
                    </label>显示
                  </div>
                  <button type="button" class="btn btn-light mb-auto mx-sm-3" id="cancelBtn">取消更新</button>
                  <button type="button" class="btn btn-info mb-auto mx-3" id="confirmBtn">更新分类</button>
                </form>
                <div class="text-danger new-category-error small d-none edit-error" id="editError"></div>
              </td>
            </tr>`
}

function rebuildCategoryOrigTr($origTr, recordData) {
    /**
     * 重建数据展示的列
     * @param: $origTr 初始的数据展示列
     * @param: recordData 记录数据
     */
    const $td = $origTr.find('td');
    $td.each(function (index) {
        // 更新分类数据第一栏中的链接以及分类名
        if (index === 0) {
            const aTag = this.firstElementChild;
            let hrefArr = aTag.getAttribute('href').split('/');

            if (recordData.alias) {
                hrefArr[2] = recordData.alias;
            } else {
                hrefArr[2] = recordData.name;
            }

            aTag.setAttribute('href', hrefArr.join('/'));
            aTag.innerText = recordData.name;
        }
        // 更新别名
        if (index === 1) {
            this.innerText = recordData.alias ? recordData.alias : '';
        }
        // 更新显示状态
        if (index === 2) {
            this.innerHTML = recordData.show ? '是' : '<span class="text-muted">否</span>'
        }
    })
}