
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

        resourceIdToColumn[resource.id] = i + 2;
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
        var column = i + 2;
        for (var j = 0; j < totalHours * 4; ++j) {
            var row = j + 2;
            var gridLineDiv = $('<div>', {
                'class': 'schedule-grid-line',
                'style': 'grid-column: ' + column + '; ' +
                    'grid-row: ' + row + ';',
            });
            container.append(gridLineDiv);
        }
    }

    // Add events
    var events = args.events || {};
    for (var i = 0; i < events.length; ++i) {
        var event = events[i];
        var start = moment(event.start);
        var end = moment(event.end);
        var column = resourceIdToColumn[event.resource];
        var rowStart = (start.hours() - startHour) * 4 + 2;

        var spanHours = end.diff(start, 'minute') / 60;
        var span15Min = Math.round(spanHours * 4);

        var eventDiv = $('<div>', {
            'class': 'schedule-event',
            'html': start.format('LT') + '<br>' + event.title + '<br>' +
                end.format('LT'),
            'title': event.description, // hover text
            'style': 'grid-column: ' + column + '; grid-row: ' + rowStart + ' / span ' + span15Min + ';',
        });
        container.append(eventDiv);
    }

    return this;
}
