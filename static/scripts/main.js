$(document).ready(function() {
    function setReturnToEdit() {
        setBackButton()
        $('.block.date').removeClass('hidden');
        showTimeBlockButton();
        showTimeBlock();
        hideConfirm();
    }

    function setBackButton(action='', href='', desc='') {
        const backButton = $('#back-button');

        if (action == 'redirect' || href) {
            backButton.attr('href', href)
            backButton.data('description', desc)
        }
        if (action == 'return-to-edit') {
            backButton.attr('href', '#')
            backButton.data('description', 'Return to edit')
            $(backButton).on('click', function (e) {
                e.preventDefault();
                setReturnToEdit();
            });
        }
        else {
            backButton.attr('href', 'https://seniwave.com')
            backButton.data('description', 'Back to SeniWave')
        }
    }

    let currentYear = window.calendarData.year;
    let currentMonth = window.calendarData.month;

    const monthNames = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    };
    
    $(document).on('click', '#calendar-arrow-left, #calendar-arrow-right', function() {
        const isLeft = $(this).attr('id') === 'calendar-arrow-left';
        
        if (isLeft) {
            currentMonth = currentMonth - 1;
            if (currentMonth < 1) {
                currentMonth = 12;
                currentYear--;
            }
        } else {
            currentMonth = currentMonth + 1;
            if (currentMonth > 12) {
                currentMonth = 1;
                currentYear++;
            }
        }
        
        $(this).closest('.head').find('h3').text(monthNames[currentMonth] + ' ' + currentYear);
        
        const daysContainer = $('.days');

        if (daysContainer.length > 0) {
            daysContainer.attr('hx-get', `/api/calendar/${currentYear}/${currentMonth}`);
            
            if (typeof htmx !== 'undefined') {
                htmx.trigger(daysContainer[0], 'calendarNav');
                //console.log('htmx trigger sent');
            } else {
                daysContainer.load(`/api/calendar/${currentYear}/${currentMonth}`);
                //console.log('fallback');
            }
        } else {
            //console.error('days container not found');
        }
    });

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
    }
    function hideConfirm(){
        $('.confirmation').addClass('hidden');
    }

    
    $(document).on('click', '.day:not(.empty):not([disabled])', function() {
        $('.day.selected').removeClass('selected');
        $(this).addClass('selected');

        hideTimeBlockButton();

        const date = $(this).data('date');
        updateConfirmBlock(date, '', '');

        //console.log('Selected date:', $(this).data('date'));
        
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
        
        // console.log('Selected time slot:', slotId, start, '-', end);
    });

    $(document).on('click', '#time-block-next button', function() {
        setBackButton(action='return-to-edit')
        $('.block.date').addClass('hidden');
        hideTimeBlock()
        showConfirm()
    });


    $(document).on('click', '#return-to-edit', function() {
        setReturnToEdit()
    });

    $(document).on('submit', '.confirmation', function(e) {
        e.preventDefault();
        
        const date = $('#hidden-date').val();
        const slot_id = $('#hidden-slot-id').val();
        
        if (!date || !slot_id) {
            alert('Please select date and time first');
            return false;
        }
        
         console.log('Form data:', {
            date: date,
            slot_id: slot_id,
            name: $('#name').val(),
            email: $('#email').val(),
            services: $('#services').val(),
            message: $('#message').val()
        });
        
        this.submit();
    });
});