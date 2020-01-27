;(function ($) {

    const $mainNavbar = $('#mainNavbar');    // 获取主导航栏
    const $window = $.globalVal.$window;     // 从 globalVal 取出 $window 对象

    // 滚动高度超过 100 显示导航栏背景，反之隐藏
    $window.scroll(function () {
        if ($window.scrollTop() > 100) {
            $mainNavbar.removeClass('navbar-transparent');
        } else {
            $mainNavbar.addClass('navbar-transparent');
        }
    });
})(jQuery);