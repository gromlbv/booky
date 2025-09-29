$(document).ready(function() {
    function setReturnToEdit() {
        setBackButton()
        $('.block.date').removeClass('hidden');
        showTimeBlockButton();
        showTimeBlock();
        hideConfirm();
    }

    function setBackButton(action='', href='', desc='', arrow='') {
        const backButton = $('#back-button');
        backButton.removeClass('arrow-top')
            .off('click');

        if (action == 'redirect' || href) {
            backButton.attr('href', href)
                .data('description', desc)
        } else if (action == 'return-to-edit') {
            backButton.addClass('arrow-top')
                .attr('href', '#')
                .data('description', 'Return to edit')
                .on('click', function (e) {
                    e.preventDefault();
                    setReturnToEdit();
                });
        } else {
            backButton.attr('href', 'https://seniwave.com')
                .data('description', 'Back to SeniWave')
        }
    }

    if (!window.calendarData) return;
    
    let currentYear = window.calendarData.year;
    let currentMonth = window.calendarData.month;

    const monthNames = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    };

    function updateConfirmBlock(date, time, slotId) {
        if (date) {
            $('#confirm-date').text(date);
            $('#hidden-date').val(date);
        }
        if (time) {
            $('#confirm-time').html(time);
            $('#hidden-slot-id').val(slotId);
        }
    }

    function showTimeBlockButton(){
        $('#time-block-next p').removeClass('visible');
        $('#time-block-next button').addClass('visible');
    }
    function hideTimeBlockButton(){
        $('#time-block-next p').addClass('visible');
        $('#time-block-next button').removeClass('visible');
    }
    function hideTimeBlock(){
        $('.block.time').addClass('hidden');
        $('#time-block-next p').removeClass('visible');
        $('#time-block-next button').removeClass('visible');
    }
    function showTimeBlock(){
        $('.block.time').removeClass('hidden');
    }

    function showConfirm(){
        $('.confirmation').removeClass('hidden');
        $('header').addClass('confirmation-open');
    }
    function hideConfirm(){
        $('.confirmation').addClass('hidden');
        $('header').removeClass('confirmation-open');
    }

    
    $(document).on('click', '.day:not(.empty):not([disabled])', function() {
        $('.day.selected').removeClass('selected');
        $(this).addClass('selected');

        hideTimeBlockButton();

        const date = $(this).data('date');
        updateConfirmBlock(date, '', '');
        
        const timeBlock = $('#time-block');
        if (timeBlock.length > 0) {
            timeBlock.attr('hx-get', `/api/time-slots/${date}`);
            htmx.ajax('GET', `/api/time-slots/${date}`, {target: '#time-block', swap: 'innerHTML'});
        }
    });
    
    $(document).on('click', '.time-slot', function() {
        $('.time-slot.selected').removeClass('selected');
        $(this).addClass('selected');

        showTimeBlockButton();

        const slotId = $(this).data('slot-id');
        const start = $(this).data('start');
        const end = $(this).data('end');
        
        const selectedDate = $('.day.selected').data('date');
        const timeText = `${start}<br>${end}`;
        updateConfirmBlock(selectedDate, timeText, slotId);
    });

    $(document).on('click', '#time-block-next button', function() {
        setBackButton(action='return-to-edit')
        $('.block.date').addClass('hidden');
        hideTimeBlock()
        showConfirm()
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });


    $(document).on('click', '#return-to-edit', function() {
        setReturnToEdit()
        setTimeout(() => {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }, 60);
    });

    $(document).on('submit', '.confirmation', function(e) {
        e.preventDefault();
        
        const date = $('#hidden-date').val();
        const slot_id = $('#hidden-slot-id').val();
        
        if (!date || !slot_id) {
            alert('Please select date and time first');
            return false;
        }
        
        this.submit();
    });

    // header scrolling animation
    $(window).scroll(function () {
        const scrollTop = $(this).scrollTop();
        const isScrolled = scrollTop > 0;
        const isScrolled110 = scrollTop > 110;
        $('header').toggleClass('scrolled', isScrolled);
        $('header').toggleClass('scrolled-110', isScrolled110);
    });

    // calendar navigation animation
    $(document).on('click', '#calendar-arrow-left, #calendar-arrow-right', function() {
        const isLeft = $(this).attr('id') === 'calendar-arrow-left';
        if (isLeft) {
            $('.days').addClass('removing left');
        } else {
            $('.days').addClass('removing right');
        }
    });
});
