$(document).ready(function() {
    let tooltipTimeout;
    let currentTooltip = null;
    
    $(document).on('mouseenter', '[data-description]', function() {
        const $element = $(this);
        const description = $element.data('description');
        if (!description) return;
        clearTimeout(tooltipTimeout);
        tooltipTimeout = setTimeout(function() {
            showTooltip($element, description);
        }, 400);
    });
    
    $(document).on('mouseleave', '[data-description]', function() {
        clearTimeout(tooltipTimeout);
        hideTooltip();
    });
    
    function showTooltip($element, description) {
        hideTooltip();
        const $tooltip = $('<div class="tooltip">' + description + '</div>');
        $('body').append($tooltip);
        const elementRect = $element[0].getBoundingClientRect();
        $tooltip.css({
            position: 'fixed',
            left: elementRect.left + (elementRect.width / 2) - ($tooltip.outerWidth() / 2),
            top: elementRect.bottom + 4,
            opacity: 1,
            transform: 'scale(1)'
        });
                
        currentTooltip = $tooltip;
    }
    
    function hideTooltip() {
        if (currentTooltip) {
            currentTooltip.fadeOut(200, function() {
                $(this).remove();
            });
            currentTooltip = null;
        }
    }
});