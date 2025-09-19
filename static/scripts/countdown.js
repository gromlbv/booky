function initCountdown() {
    const daysElement = document.querySelector('.countdown-days');
    const hoursElement = document.querySelector('.countdown-hours');
    const minutesElement = document.querySelector('.countdown-minutes');
    
    if (!daysElement || !hoursElement || !minutesElement) {
        console.log('Countdown elements not found');
        return;
    }
    
    const meetingDate = daysElement.getAttribute('data-meeting-date');
    const meetingTime = daysElement.getAttribute('data-meeting-time');
    
    if (!meetingDate || !meetingTime) {
        console.log('Meeting date/time not found');
        return;
    }
    
    const meetingDateTime = new Date(`${meetingDate}T${meetingTime}`);
    
    function updateCountdown() {
        const now = new Date();
        const timeDiff = meetingDateTime - now;
        
        if (timeDiff <= 0) {
            daysElement.textContent = '00';
            hoursElement.textContent = '00';
            minutesElement.textContent = '00';
            return;
        }
        
        const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
        
        daysElement.textContent = days.toString().padStart(2, '0');
        hoursElement.textContent = hours.toString().padStart(2, '0');
        minutesElement.textContent = minutes.toString().padStart(2, '0');
    }
    
    updateCountdown();
    setInterval(updateCountdown, 60000);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCountdown);
} else {
    initCountdown();
}
