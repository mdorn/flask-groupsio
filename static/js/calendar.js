$(function() {

  $('#calendar').fullCalendar({
    themeSystem: 'bootstrap4',
    timeZone: 'UTC',
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'month,listMonth'
    },
    eventLimit: true, // allow "more" link when too many events
    // events: 'https://fullcalendar.io/demo-events.json'
    events: JSON.parse(document.getElementById('calData').innerText),
  });

});
