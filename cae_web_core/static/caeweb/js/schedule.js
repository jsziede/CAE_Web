function scheduleUpdateEvents(container, events) {
    var resourceIdToEvents = {};

    var resourceIdToColumn = container.data('resource-id-to-column');
    var startHour = container.data('start-hour');

    // delete old events
    container.children('.schedule-event').remove();

    console.log(events);

    for (var i = 0; i < events.length; ++i) {
        var event = events[i];
        var start = moment(event.start);
        var end = moment(event.end);
        var column = resourceIdToColumn[event.resource];
        var rowStart = (start.hours() - startHour) * 4 + 2;
        var spanHours = end.diff(start, 'minute') / 60;
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
        container.append(eventDiv);
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
    container.addClass("schedule-container");

    container.append('<div class="schedule-header-spacer"></div>');

    var resourceIdToColumn = {};

    // Add resource headers
    var resources = args.resources || {};
    for (var i = 0; i < resources.length; ++i) {
        var resource = resources[i];
        var resourceDiv = $('<div>', {
            'class': 'schedule-resource',
            'html': resource.html,
        });
        container.append(resourceDiv);

        resourceIdToColumn[resource.id] = i * 2 + 2;
    }


    // Add time headers
    // hours are in 24 hour format, 0 and 24 are midnight
    var startHour = args.startHour || 8;
    var endHour = args.endHour || 24;
    var hour = moment({ hour: startHour });
    var totalHours = 0;
    for (var i = startHour; i < endHour; ++i) {
        var timeDiv = $('<div>', {
            'class': 'schedule-time',
            'text': hour.format('LT'),
        });
        hour.add({ hours: 1 });
        container.append(timeDiv);
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
            container.append(gridLineDiv);
        }
    }

    container.data('resource-id-to-column', resourceIdToColumn);
    container.data('start-hour', startHour);
    container.data('end-hour', endHour);

    this.scheduleUpdate(args);

    return this;
}
