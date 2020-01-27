function createCategoryEditForm(recordData) {
    /**
     * 创建编辑表单
     * @param: recordData 记录数据
     */
    return `<tr id="formTr">
              <td colspan="5">
                <form action="#" method="post" id="editForm">
                  <input type="hidden" name='id' value="${recordData.id}">
                  <div class="form-row align-items-center">
                    <div class="col-sm-3 my-1">
                      <label class="sr-only" for="editInputName"></label>
                      <input type="text" class="form-control" id="editInputName" value="${recordData.name}" name='name' placeholder="分类名">
                    </div>
                    <div class="col-sm-3 my-1">
                      <label class="sr-only" for="editInputAlias"></label> 
                      <input type="text" class="form-control" id="editInputAlias" value="${recordData.alias ? recordData.alias : ''}" name='alias' placeholder="别名">
                    </div>
                    <div class="col-auto my-1">
                      <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="categoryShow" name="show" ${recordData.show ? 'checked' : ''}>
                          <label class="form-check-label" for="categoryShow">
                            显示
                          </label>
                      </div>
                    </div>
                      <button type="button" class="btn btn-light mx-2" id="cancelBtn">取消更新</button>
                      <button type="button" class="btn btn-info" id="confirmBtn">更新分类</button>
                  </div>
                </form>
                <div class="text-danger new-category-error small d-none inline-form-edit-error" id="editError"></div>
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