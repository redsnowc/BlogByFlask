(function ($) {
    const $jumbotron = $('#indexJumbotron');
    const $toTop = $('#toTop');
    const height = $(window).height();

    // 打开网页时首页设置巨幕的高度
    $jumbotron.height(height);

    // 浏览器窗口尺寸改变时动态改变首页巨幕高度
    $(window).on('resize', function () {
        const height = $(window).height();
        $jumbotron.height(height)
    });

    // 根据滚动高度显示或隐藏导航栏背景、返回顶部按钮
    $(window).scroll(function () {
        if ($(window).scrollTop() > 100) {
            $(".navbar").removeClass('navbar-transparent');
            $toTop.removeClass('hide');
        } else {
            $(".navbar").addClass('navbar-transparent');
            $toTop.addClass('hide')
        }
    });

    // 返回页面顶部
    $toTop.click(function () {
        $.scrollAnimation(0)
    })
})(jQuery);