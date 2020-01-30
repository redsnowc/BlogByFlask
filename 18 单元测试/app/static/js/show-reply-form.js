function ShowReplyForm(option) {
    /*
    * 显示回复表单
    * */
    this.$ = jQuery;
    this.$replyLinks = this.$('.reply-link');
    this.$mainCommentForm = this.$('#commentForm');
    this.$document = this.$(document);

    this.is_authenticated = option.is_authenticated;
    this.formAction = option.formAction;
    this.adminFormHtmlStr = option.adminFormHtmlStr;
    this.commonFormHtmlStr = option.commonFormHtmlStr;

    this.replyId = '';
    this.$replyForm = null;
    this.$closeBtn = null;

    // 绑定事件
    this._bindEvent = function () {
        this.$replyLinks.on('click', (event) => {

            if (this.$replyForm) {
                this.$replyForm.remove();
            }

            const $target = $(event.target);
            this.formAction += `?reply_id=${$target.data('id')}`;

            if (this.is_authenticated) {
                this.$replyForm = $(this.adminFormHtmlStr.replace('$formAction', this.formAction))
            } else {
                this.$replyForm = $(this.commonFormHtmlStr.replace('$formAction', this.formAction))
            }

            this.$mainCommentForm.hide();
            $target.after(this.$replyForm);
            this.$document.trigger('formCreated');
        });

        this.$document.on('formCreated', () => {
            this.$closeBtn = $('#closeBtn');
            this.$closeBtn.on('click', () => {
                this.$mainCommentForm.show();
                this.$replyForm.remove();
            })
        })
    };

    this._bindEvent()
}