function positionPopup(popup, trigger) {
    if (!popup || !trigger) return;
    const $popup = $(popup);
    const $trigger = $(trigger);
    const popupWidth = $popup.outerWidth();
    const spaceLeft = $trigger.offset().left;
    
    if (spaceLeft >= (popupWidth - 30)) {
        $popup.css({ left: '', right: '0', transformOrigin: 'bottom right' });
    } else {
        $popup.css({ left: '0', right: '', transformOrigin: 'bottom left' });
    }
}

$(document).ready(function() {
    $('.action-button').each(function() {
        const $button = $(this);
        const $popup = $button.next('.action-content');
        
        $button.on('click', function() {
            setTimeout(() => positionPopup($popup[0], this), 10);
        });
        
        $(window).on('resize', function() {
            if ($popup.hasClass('open')) {
                positionPopup($popup[0], $button[0]);
            }
        });
    });
});

window.PopupPositioning = { positionPopup };
