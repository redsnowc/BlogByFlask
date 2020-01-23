;(function ($) {
    // 全局通用的变量和功能

    const $window = $(window);        // 获取 jq window 对象
    const height = $window.height();  // 获取当前窗口高度

    // 将 $window 和窗口高度存入 globalVal 对象
    const globalVal = {
        $window: $window,
        height: height
    };

    function scrollAnimation(targetY) {
        /**
         * 处理页面滚动至某一高度的平滑过渡效果
         * @param: targetY 目标高度
         */
        const timer = setInterval(function () {
            const currentY = document.documentElement.scrollTop || document.body.scrollTop;
            const distance = targetY > currentY ? targetY - currentY : currentY - targetY;
            const speed = Math.ceil(distance / 10);
            if (currentY === targetY) {
                clearInterval(timer)
            } else {
                scrollTo(0, targetY > currentY ? currentY + speed : currentY - speed)
            }
        }, 10);
    }

    // 获取时差
    const timeZoneOffset = new Date().getTimezoneOffset() / 60;

    function toLocalTime(dateStr) {
        /**
         * 将 UTC 时间转换为本地时间
         * @param: dateStr 需要转换的时间字符串，如 2020-1-1 19:45:54
         */
        const dateObj = new Date(dateStr.replace(/-/g, '/'));
        const origHours = dateObj.getHours();
        dateObj.setHours(origHours - timeZoneOffset);
        const year = dateObj.getFullYear();
        const month = dateObj.getMonth() + 1 < 10 ? '0' + (dateObj.getMonth() + 1) : dateObj.getMonth() + 1;
        const date = dateObj.getDate();
        const hours = dateObj.getHours();
        const minutes = dateObj.getMinutes();
        return `${year}-${month}-${date} ${hours}:${minutes}`
    }

    // 对外暴露，使全局可调用
    $.extend({
        scrollAnimation: scrollAnimation,
        toLocalTime: toLocalTime,
        globalVal: globalVal
    })
})(jQuery);