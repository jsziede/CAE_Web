function scheduleUpdateEvents(container, events) {
    var resourceIdToEvents = {};

    var resourceIdToColumn = container.data('resource-id-to-column');
    var calendarStart = container.data('start');
    var calendarEnd = container.data('end');

    var scheduleGrid = container.children('.schedule-grid');

    // delete old events
    scheduleGrid.children('.schedule-event').remove();

    console.log(events);

    for (var i = 0; i < events.length; ++i) {
        var event = events[i];
        var start = moment(event.start);
        var end = moment(event.end);

        if (end < calendarStart || start > calendarEnd) {
            // Skip this event
            continue;
        }
        console.log("Have event!");

        var column = resourceIdToColumn[event.resource];
        var startDiff = start.diff(calendarStart, 'minute') / 60;
        var endDiff = end.diff(calendarEnd, 'minute') / 60;
        var rowStart = Math.max(0, startDiff) * 4 + 2;
        var spanHours = end.diff(start, 'minute') / 60;
        if (startDiff < 0) {
            // Reduce span if we cut off the start
            spanHours += startDiff;
        }
        if (endDiff > 0) {
            // Reduce span if we cut off the end
            spanHours -= endDiff;
        }
        var span15Min = Math.round(spanHours * 4);
        var eventDivId = 'id_schedule_event_' + event.id;

        var resourceEvents = resourceIdToEvents[event.resource] || {};
        var hasEventConflict = false;
        for (var eventId in resourceEvents) {
            if (!resourceEvents.hasOwnProperty(eventId)) {
                continue;
            }
            var resourceEvent = resourceEvents[eventId];
            if (!start.isAfter(resourceEvent.end) &&
                !end.isBefore(resourceEvent.start)) {
                hasEventConflict = true;
                // shrink event to span only 1 column
                $('#' + resourceEvent.divId).css({ 'grid-column': '' + column });
            }
        }

        var columnSpan = 2;
        if (hasEventConflict) {
            ++column;
            columnSpan = 1;
        } else {
            resourceEvents[event.id] = {
                'divId': eventDivId,
                'start': start,
                'end': end,
            }
            resourceIdToEvents[event.resource] = resourceEvents;
        }

        var eventToolbar = $('<div>', {
            'class': 'schedule-event-toolbar',
            'html': '<button type="button" title="Edit">&#9881;</button>',
        });

        var eventDiv = $('<div>', {
            'id': eventDivId,
            'class': 'schedule-event',
            'html': start.format('LT') + '<br>' + event.title + '<br>' +
                end.format('LT'),
            'title': event.description, // hover text
            'style': 'grid-column: ' + column + ' / span ' + columnSpan + '; grid-row: ' + rowStart + ' / span ' + span15Min + ';',
        });
        eventDiv.prepend(eventToolbar);
        scheduleGrid.append(eventDiv);
    }
}

jQuery.fn.scheduleUpdate = function(args) {
    var container = $(this[0]);

    // Add events
    // NOTE: Events must be sorted by start times to handle overlapping events

    var eventsURL = args.eventsURL || "";
    if (eventsURL) {
        console.log("Getting events by url");
        $.get(eventsURL, function(data) {
            scheduleUpdateEvents(container, data.events);
            console.log("Got events by url");
        }, "json");
    } else {
        var events = args.events || {};
        if (events) {
            scheduleUpdateEvents(container, events);
        }
    }


    return this;
}

jQuery.fn.schedule = function(args) {
    var container = $(this[0]);

    // Add main header
    var scheduleHeader = $('<div>', {
        'class': 'schedule-header',
    });
    container.append(scheduleHeader);

    // TODO: Add header bar with button to go to 'Today', 'Back', 'Forward'
    // And list selected day, like old version.
    //scheduleHeader.html("<");

    // Add Grid
    var scheduleGrid = $('<div>', {
        'class': 'schedule-grid',
    });
    container.append(scheduleGrid);

    // Spacer for top left, between left and top grid headers
    scheduleGrid.append('<div class="schedule-header-spacer"></div>');

    var resourceIdToColumn = {};

    // Add resource headers
    var resources = args.resources || {};
    for (var i = 0; i < resources.length; ++i) {
        var resource = resources[i];
        var resourceDiv = $('<div>', {
            'class': 'schedule-resource',
            'html': resource.html,
        });
        scheduleGrid.append(resourceDiv);

        resourceIdToColumn[resource.id] = i * 2 + 2;
    }


    // Add time headers
    // start and end are actual times with timezone info
    var start = moment(args.start);
    var end = moment(args.end);
    var hour = moment(args.start);
    var totalHours = 0;
    while (hour < end) {
        var timeDiv = $('<div>', {
            'class': 'schedule-time',
            'text': hour.format('LT'),
        });
        hour.add({ hours: 1 });
        scheduleGrid.append(timeDiv);
        ++totalHours;
    }

    // Add grid lines
    for (var i = 0; i < resources.length; ++i) {
        var column = i * 2 + 2;
        for (var j = 0; j < totalHours * 4; ++j) {
            var row = j + 2;
            var gridLineDiv = $('<div>', {
                'class': 'schedule-grid-line',
                'style': 'grid-column: ' + column + '/ span 2; ' +
                    'grid-row: ' + row + ';',
            });
            scheduleGrid.append(gridLineDiv);
        }
    }

    container.data('resource-id-to-column', resourceIdToColumn);
    container.data('start', start);
    container.data('end', end);

    this.scheduleUpdate(args);

    return this;
}
