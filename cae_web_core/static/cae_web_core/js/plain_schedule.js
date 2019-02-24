var createSchedule = function(container) {
    // See ScheduleConsumer for these constants
    const ACTION_GET_EVENTS = 'get-events'
    const ACTION_SEND_EVENTS = 'send-events'

    var container = $(container);
    var start = moment(container.data('start'));
    var end = moment(container.data('end'));
    var resources = container.data('resources');

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
                // TODO: have click event figure out where to add event (resource and time)
                // and then open event dialog.
                gridLineDivs += `<div class="schedule-grid-line" style="grid-area: ${row} / ${column} / auto / span 2"></div>`
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
            const startDiff = Math.round(eventStart.diff(start, 'second') / 3600); // hours
            const endDiff = Math.round(eventEnd.diff(end, 'second') / 3600); // hours
            const rowStart = Math.max(0, startDiff) * 4 + 2;
            var spanHours = Math.round(eventEnd.diff(eventStart, 'second') / 3600);
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
                if (!eventStart.isAfter(resourceEvent.event.end) &&
                    !eventEnd.isBefore(resourceEvent.event.start)) {
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
            // TODO: Only show edit button if user can edit events
            const toolbar = `<div class="schedule-event-toolbar"><button title="edit"><i class="fas fa-pencil-alt"></i></button></div>`;
            const contents = `
                ${moment(data.event.start).format('LT')}<br/>
                ${data.event.title}<br/>
                ${moment(data.event.end).format('LT')}`;
            eventDivs += `<div class="schedule-event" title="${data.event.description}" style="${style}">${toolbar}${contents}</div>`;
        }

        grid.append(eventDivs);
    }

    // Initialize
    container.empty();
    var header = createHeader();
    var grid = createGrid();

    container.append(header);
    container.append(grid);

    return {
        dummy: function() {
            console.log("dummy");
        },
    }
};

$(function() {
    //schedule.initAll();
    $('.schedule-container').each(function() {
        var schedule = createSchedule(this);
    });

    // Run flatpickr for all date inputs
    $('.schedule-txt-date').flatpickr({
        altInput: true,
        altFormat: "F j, Y",
    });
});
