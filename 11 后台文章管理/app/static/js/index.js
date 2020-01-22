;(function ($) {
    // 首页独有

    const $jumbotron = $('#indexJumbotron'); // 获取首页巨幕
    const $window = $.globalVal.$window;     // 从 globalVal 取出 $window 对象
    const height = $.globalVal.height;       // 从 globalVal 取出窗口高度

    // 打开网页时首页设置巨幕的高度等于窗口高度
    $jumbotron.height(height);

    // 浏览器窗口尺寸改变时动态改变首页巨幕高度
    $window.on('resize', function () {
        const height = $window.height();
        $jumbotron.height(height)
    });
})(jQuery);