(function ($) {

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

    $.extend({
        scrollAnimation: scrollAnimation
    })
})(jQuery);