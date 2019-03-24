var dialogEventStart = null;
var dialogEventEnd = null;

var createSchedule = function(container) {
    // See ScheduleConsumer for these constants
    const ACTION_GET_EVENTS = 'get-events'
    const ACTION_SEND_EVENTS = 'send-events'

    var container = $(container);
    var start = moment(container.data('start'));
    var end = moment(container.data('end'));
    var resources = container.data('resources');
    var roomTypeSlug = container.data('room-type-slug');

    // Establish socket connection.
    var domain = window.location.hostname
    if (window.location.port) {
        domain += ":" + window.location.port
    }
    var socket = new WebSocket('ws://' + domain + '/ws/caeweb/schedule/');

    // Send message to socket.
    socket.onopen = function(event) {
        socket.send(JSON.stringify({
            'action': ACTION_GET_EVENTS,
            'start_time': start.format(),
            'end_time': end.format(),
            'room_type_slug': roomTypeSlug,
            'notify': true,
        }));
    };

    socket.addEventListener('message', (message) => {
        var data = JSON.parse(message.data);
        if (data.action == ACTION_SEND_EVENTS) {
            updateEvents(data.events);
        }
    });

    function createHeader() {
        var buttons = '<div class="buttons"><button class="schedule-btn-today">Today</button><button class="schedule-btn-prev"><i class="fas fa-angle-left"></i></button><button class="schedule-btn-next"><i class="fas fa-angle-right"></i></button></div>';
        var calendarButton = '<button class="schedule-btn-calendar"><i class="fas fa-calendar-alt"></i></button>';
        var dateInput = `<input type="text" class="schedule-txt-date" value="${start.format('YYYY-MM-DD')}">`;

        header = $('<div>', {
            class: "schedule-header",
            html: `${buttons}${calendarButton}${dateInput}`,
        });

        return header;
    }

    function createGrid() {
        // Create top resources header
        var resourcesDivs = '';
        for (var i = 0; i < resources.length; ++i) {
            var resource = resources[i];

            resourcesDivs += `<div class="schedule-resource" data-pk=${resource.id}>${resource.html}</div>`;
        }

        // Create left time header
        var timeDivs = '';
        var hour = start.clone();
        var totalHours = 0;

        while (hour < end) {
            timeDivs += `<div class="schedule-time">${hour.format('LT')}</div>`;

            hour.add({ hours: 1});
            ++totalHours;
        }

        // Create grid lines
        var gridLineDivs = '';
        for (var i = 0; i < resources.length; ++i) {
            var column = i * 2 + 2;
            for (var j = 0; j < totalHours * 4; ++j) {
                var row = j + 2
                var resourceIndex = i;
                var timeOffset = j;
                gridLineDivs += `<div
                    class="schedule-grid-line"
                    style="grid-area: ${row} / ${column} / auto / span 2"
                    data-resource-index=${resourceIndex}
                    data-time-offset=${timeOffset}
                ></div>`
            }
        }

        grid = $('<div>', {
            class: "schedule-grid",
            html: `<div class="schedule-header-spacer"></div>${resourcesDivs}${timeDivs}${gridLineDivs}`,
        });

        return grid;
    }

    function updateEvents(events) {
        const resourceIdToColumn = {};
        const resourceIdToEvents = {};

        resources.map((resource, column) => {
            resourceIdToColumn[resource.id] = column * 2 + 2;
        });

        // keep track of events that have been processsed
        // we may need to update some before actually creating React elements
        const processedEvents = {};

        events.map((event) => {
            const eventStart = moment(event.start);
            const eventEnd = moment(event.end);

            if (eventEnd < start || eventStart > end) {
                // Event happens outside schedule, skip it
                console.log("Skipping event", event);
                return null;
            }

            var column = resourceIdToColumn[event.resource];
            if (column == undefined) {
                console.log(resourceIdToColumn);
                console.log(event);
                throw "Unknown resource!";
            }
            const startDiff = Number((eventStart.diff(start, 'second') / 3600).toFixed(2)); // hours
            const endDiff = Number((eventEnd.diff(end, 'second') / 3600).toFixed(2)); // hours
            const rowStart = Math.round(Math.max(0, startDiff) * 4 + 2); // +2 for header
            var spanHours = Number((eventEnd.diff(eventStart, 'second') / 3600).toFixed(2));
            if (startDiff < 0) {
                // Reduce span if we cut off the start (Add a negative)
                spanHours += startDiff;
            }
            if (endDiff > 0) {
                // Reduce span if we cut off the end
                spanHours -= endDiff;
            }
            const span15Min = Math.round(spanHours * 4);

            // Check for overlapping events
            const resourceEvents = resourceIdToEvents[event.resource] || {};
            var hasEventConflict = false;
            Object.keys(resourceEvents).map((i) => {
                const resourceEvent = resourceEvents[i];
                if (!(eventStart.isAfter(resourceEvent.event.end) || eventStart.isSame(resourceEvent.event.end)) &&
                    !(eventEnd.isBefore(resourceEvent.event.start) || eventEnd.isSame(resourceEvent.event.start))) {
                    hasEventConflict = true;
                    // shrink event to span only 1 column
                    resourceEvent.columnSpan = 1;
                }
            })

            var columnSpan = 2;
            if (hasEventConflict) {
                ++column;
                columnSpan = 1;
            }

            const data = {
                event: event,
                column: column,
                columnSpan: columnSpan,
                rowStart: rowStart,
                span15Min: span15Min,
            };

            processedEvents[event.id] = data;

            if (!hasEventConflict) {
                resourceEvents[event.id] = data;
                resourceIdToEvents[event.resource] = resourceEvents;
            }
        })

        // Clear out old events
        grid.children('.schedule-event').remove();

        // Now create event elements
        var eventDivs = '';
        for (var eventId in processedEvents) {
            const data = processedEvents[eventId];
            const style = `grid-area: ${data.rowStart} / ${data.column} / span ${data.span15Min} / span ${data.columnSpan}`;
            const eventStart = moment(data.event.start).format('LT');
            const eventEnd = moment(data.event.end).format('LT');
            const contents = `
                ${eventStart}<br/>
                ${data.event.title}<br/>
                ${eventEnd}`;
            eventDivs += `<div class="schedule-event" title="${data.event.title} (${eventStart} - ${eventEnd})&#10;${data.event.description}" style="${style}" data-event="${escape(JSON.stringify(data.event))}">${contents}</div>`;
        }

        grid.append(eventDivs);

        // Add event handler for click action
        container.find('.schedule-event').on('click', onEventClicked);
    }


    function changeDate(dateString) {
        var inputDate = moment(dateString)
        // .clone().startOf('day') strips the time for a more accurate day diff
        var daysDiff = inputDate.clone().startOf('day').diff(start.clone().startOf('day'), 'days');
        start.add(daysDiff, 'days');
        end.add(daysDiff, 'days');

        history.replaceState({}, start.format('L'), '?date=' + start.format('YYYY-MM-DD'));

        dateFlatpickr.setDate(start.format('YYYY-MM-DD'));

        // Fetch events
        socket.send(JSON.stringify({
          'action': ACTION_GET_EVENTS,
          'start_time': start.format(),
          'end_time': end.format(),
          'room_type_slug': roomTypeSlug,
          'notify': true,
        }))
      }

    function onBtnTodayClicked(event) {
        changeDate(moment().toDate());
    }

    function onBtnPrevClicked(event) {
        var current = start.clone()
        current.subtract(1, 'days');
        changeDate(current.toDate());
    }

    function onBtnNextClicked(event) {
        var current = start.clone()
        current.add(1, 'days');
        changeDate(current.toDate());
    }

    function onBtnCalendarClicked(event) {
        dateFlatpickr.open();
    }

    function onEventClicked(event) {
        var event = JSON.parse(unescape($(event.target).closest('.schedule-event').data('event')));
        console.log(event);
        $('#id_room_event_pk').val(event.id);
        $('#id_title').val(event.title);
        dialogEventStart.setDate(moment(event.start).format('YYYY-MM-DD HH:mm'));
        dialogEventEnd.setDate(moment(event.end).format('YYYY-MM-DD HH:mm'));
        $('#id_description').val(event.description);
        $('#id_event_type').val(event.event_type);
        $('#id_room').val(event.resource);

        show_overlay_modal();
    }

    function onGridLineDblClicked(event) {
        var gridLine = $(event.target);
        var resourceIndex = gridLine.data('resource-index');
        var resource = resources[resourceIndex];
        var timeOffset = gridLine.data('time-offset');

        var eventStart = start.clone();

        for (var i = 0; i < timeOffset; ++i) {
            eventStart.add(15, 'minutes');
        }

        var eventEnd = eventStart.clone();
        eventEnd.add(1, 'hours');

        $('#id_room_event_pk').val('');
        $('#id_title').val('New Event');
        dialogEventStart.setDate(eventStart.format('YYYY-MM-DD HH:mm'));
        dialogEventEnd.setDate(eventEnd.format('YYYY-MM-DD HH:mm'));
        $('#id_description').val('New Event Description');
        //$('#id_event_type').val(); // Just use whatever last value was
        $('#id_room').val(resource.id);

        show_overlay_modal();
    }

    // Initialize
    container.empty();
    var header = createHeader();
    var grid = createGrid();

    container.append(header);
    container.append(grid);

    // Add event handlers
    container.find('.schedule-btn-today').on('click', onBtnTodayClicked);
    container.find('.schedule-btn-prev').on('click', onBtnPrevClicked);
    container.find('.schedule-btn-next').on('click', onBtnNextClicked);
    container.find('.schedule-btn-calendar').on('click', onBtnCalendarClicked);
    container.find('.schedule-grid-line').on('dblclick', onGridLineDblClicked);

    // Setup flatpickr
    var dateFlatpickr = container.find('.schedule-txt-date').flatpickr({
        altInput: true,
        altFormat: "l, F j, Y",
        onChange: function(selectedDates) {
            changeDate(selectedDates[0]);
        },
    });

    return {
        dummy: function() {
            console.log("dummy");
        },
    }
};

$(function() {
    $('.schedule-container').each(function() {
        var schedule = createSchedule(this);
    });

    // Move event dialog into modal dialog
    $('#div_event_dialog').appendTo('#overlay-modal').show();
    dialogEventStart = $('#id_start_time').flatpickr({
        enableTime: true,
        altInput: true,
        dateFormat: "Y-m-d H:i",
        altFormat: "l, F j, Y h:i K",
    });
    dialogEventEnd = $('#id_end_time').flatpickr({
        enableTime: true,
        altInput: true,
        dateFormat: "Y-m-d H:i",
        altFormat: "l, F j, Y h:i K",
    });

    // Close dialog when cancel clicked
    $('#btn_cancel').on('click', function() {
        hide_overlay_modal();
    });

    // Set height of schedule based on viewport
    var top = $('.schedule-container').position().top;
    var bottom = document.body.scrollHeight - (top + $('.schedule-container').height());

    $('.schedule-container').css({
        height: `calc(100vh - ${top + bottom + 1}px`,
    });

    // Check if we have errors from previous POST
    if ($('#div_event_dialog[data-errors]').length) {
        show_overlay_modal();
    }
});
