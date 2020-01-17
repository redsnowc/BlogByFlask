;(function ($) {
    // 返回顶部功能

    const $toTop = $('#toTop');            // 返回顶部按钮
    const $window = $.globalVal.$window;   // 从 globalVal 取出 $window 对象
    const height = $.globalVal.height;     // 从 globalVal 取出窗口高度

    // 如果滚动超过一屏显示返回顶部按钮，反之隐藏
    $window.scroll(function () {
        if ($window.scrollTop() > height) {
            $toTop.removeClass('hide');
        } else {
            $toTop.addClass('hide');
        }
    });

    // 返回页面顶部
    $toTop.click(function () {
        $.scrollAnimation(0)
    })
})(jQuery);