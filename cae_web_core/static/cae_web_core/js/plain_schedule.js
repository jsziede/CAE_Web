var dialogEventStart = null;
var dialogEventEnd = null;

var createSchedule = function(container) {
    // See ScheduleConsumer for these constants
    const ACTION_GET_EVENTS = 'get-events';
    const ACTION_SEND_EVENTS = 'send-events';

    // Storage Constants
    const STORAGE_KEY_MODE = 'schedule-mode';

    var container = $(container);
    var start = moment(container.data('start'));
    var end = moment(container.data('end'));
    var resources = container.data('resources');
    var roomTypeSlug = container.data('room-type-slug');
    var employeeType = container.data('employee-type');
    var eventMode = container.data('event-mode');
    var mode = container.data('mode');
    var modeAllowChange = container.data('mode-allow-change');

    // validate mode
    if (mode == 'week') {
        // pass
    } else if (mode == 'day') {
        // pass
    } else {
        mode = 'day'; // default to single day
    }

    // validate modeAllowChange to a boolean
    if (modeAllowChange) {
        modeAllowChange = true;
        // Check if user previously chose a mode.
        // We use sessionStorage instead of localStorage because it's not paramount
        // to remember it for very long.
        mode = sessionStorage.getItem(STORAGE_KEY_MODE) || mode;
    } else {
        modeAllowChange = false;
    }

    // Establish socket connection.
    var domain = window.location.hostname
    if (window.location.port) {
        domain += ":" + window.location.port
    }
    var socket = new WebSocket('ws://' + domain + '/ws/caeweb/schedule/');

    // Send message to socket.
    socket.onopen = function(event) {
        changeDate(start);
    };

    socket.addEventListener('message', (message) => {
        var data = JSON.parse(message.data);
        if (data.error) {
            console.log(data.error);
        }
        if (data.action == ACTION_SEND_EVENTS) {
            updateEvents(data.events);
        }
    });

    function createHeader() {
        var buttons = '<div class="buttons"><button class="schedule-btn-today">Today</button><button class="schedule-btn-prev"><i class="fas fa-angle-left"></i></button><button class="schedule-btn-next"><i class="fas fa-angle-right"></i></button></div>';
        var calendarButton = '<button class="schedule-btn-calendar"><i class="fas fa-calendar-alt"></i></button>';
        var dateInput = `<input type="text" class="schedule-txt-date" value="${start.format('YYYY-MM-DD')}">`;
        var modeChange = '';
        if (modeAllowChange) {
            var dayClass = '';
            var weekClass = '';
            if (mode == 'week') {
                weekClass = 'primary';
            } else if (mode == 'day') {
                dayClass = 'primary';
            }
            modeChange = `<div class="buttons"><button class="${dayClass} schedule-btn-mode" data-mode="day">Day</button><button class="${weekClass} schedule-btn-mode" data-mode="week">Week</button></div>`;
        }

        header = $('<div>', {
            class: "schedule-header",
            html: `<div>${buttons}<div class="input-group">${calendarButton}${dateInput}</div></div>${modeChange}`,
        });

        return header;
    }

    function createGrid() {
        var weekdayDivs = '';
        var resourcesDivs = '';
        var gridLineDivs = '';
        var rowOffset = 0;
        var weekdays = [
            // iso number, text
            [7, "Sunday"],
            [1, "Monday"],
            [2, "Tuesday"],
            [3, "Wednesday"],
            [4, "Thursday"],
            [5, "Friday"],
            [6, "Saturday"],
        ];

        if (mode == 'week') {
            // Create top day headers if mode is week
            rowOffset = 1; // most things must be moved down 1
            weekdays.map((weekday) => {
                weekdayDivs += `<div class="schedule-weekday" data-day="${weekday[0]}" style="grid-column-end: span ${resources.length * 2}">${weekday[1]}</div>`;

                // Create top resources header for each day
                for (var i = 0; i < resources.length; ++i) {
                    var resource = resources[i];

                    resourcesDivs += `<div class="schedule-resource" data-pk=${resource.id} data-day="${weekday[0]}" data-i="${i}">
                        <div class="vertical">${resource.html}</div>
                    </div>`;
                }
            })
        } else {
            // Create top resources header
            for (var i = 0; i < resources.length; ++i) {
                var resource = resources[i];

                resourcesDivs += `<div class="schedule-resource" data-pk=${resource.id}>${resource.html}</div>`;
            }
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
        var gridLineCount = (mode == 'week') ? 7 : 1;
        var gridLineColumnOffset = 0;
        for (var x = 0; x < gridLineCount; ++x) {
            var isoNumber = weekdays[x][0];
            for (var i = 0; i < resources.length; ++i) {
                var column = i * 2 + 2 + gridLineColumnOffset;
                for (var j = 0; j < totalHours * 4; ++j) {
                    var row = j + 2 + rowOffset;
                    var resourceIndex = i;
                    var timeOffset = j;
                    gridLineDivs += `<div
                        class="schedule-grid-line"
                        style="grid-area: ${row} / ${column} / auto / span 2"
                        data-resource-index=${resourceIndex}
                        data-time-offset=${timeOffset}
                        data-day=${isoNumber}
                    ></div>`
                }
            }
            gridLineColumnOffset += resources.length * 2;
        }

        grid = $('<div>', {
            class: `schedule-grid mode-${mode}`,
            html: `<div class="schedule-header-spacer"></div>${weekdayDivs}${resourcesDivs}${timeDivs}${gridLineDivs}`,
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

        end_time = end.clone();
        if (mode == 'week') {
            // Get a week's worth
            end_time.add(6, 'days');
        }

        events.map((event) => {
            const eventStart = moment(event.start);
            const eventEnd = moment(event.end);

            if (eventEnd < start || eventStart > end_time) {
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

            // Calculate that day's start and end time to figure out where in the grid it goes
            var dayStart = start.clone();
            var dayEnd = end.clone();

            if (mode == 'week') {
                // move dayStart and dayEnd into selected day
                while (dayStart.isoWeekday() != eventStart.isoWeekday()) {
                    dayStart.add(1, 'days');
                    dayEnd.add(1, 'days');
                }

                // Update column to correct day
                if (eventStart.isoWeekday() != 7) {
                    column += resources.length * 2 * eventStart.isoWeekday();
                }
            }

            const startDiff = Number((eventStart.diff(dayStart, 'second') / 3600).toFixed(2)); // hours
            const endDiff = Number((eventEnd.diff(dayEnd, 'second') / 3600).toFixed(2)); // hours
            var rowStart = Math.round(Math.max(0, startDiff) * 4 + 2); // +2 for header
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

            if (mode == "week") {
                rowStart += 1; // Because of extra header
            }

            const data = {
                event: event,
                column: column,
                columnSpan: columnSpan,
                rowStart: rowStart,
                span15Min: span15Min,
            };

            // TODO: RRule events may appear multiple times!
            var eventId = event.id;
            if (event.rrule) {
                eventId = `${eventId}-${event.rrule_index}`;
            }
            processedEvents[eventId] = data;

            if (!hasEventConflict) {
                resourceEvents[eventId] = data;
                resourceIdToEvents[event.resource] = resourceEvents;
            }
        })

        // Clear out old events
        grid.children('.schedule-event').remove();

        // Now create event elements
        var eventDivs = '';
        for (var eventId in processedEvents) {
            const data = processedEvents[eventId];
            const colors = `color: ${data.event.event_type.fg_color}; background-color: ${data.event.event_type.bg_color};`;
            const style = `grid-area: ${data.rowStart} / ${data.column} / span ${data.span15Min} / span ${data.columnSpan}; ${colors}`;
            const eventStart = moment(data.event.start).format('LT');
            const eventEnd = moment(data.event.end).format('LT');
            var title = '';
            if (data.event.title) {
                title = `${data.event.title}<br>`
            }
            const contents = `
                ${eventStart}<br/>
                ${title}
                ${eventEnd}`;
            eventDivs += `<div class="schedule-event" title="${data.event.title || ''} (${eventStart} - ${eventEnd})&#10;${data.event.description || ''}" style="${style}" data-event="${escape(JSON.stringify(data.event))}">${contents}</div>`;
        }

        grid.append(eventDivs);

        // Add event handler for click action
        container.find('.schedule-event').on('click', onEventClicked);
    }


    function changeDate(dateString) {
        var inputDate = moment(dateString)
        if (mode == 'week') {
            // convert inputDate to earliest Sunday
            while (inputDate.isoWeekday() != 7) {
                inputDate.subtract(1, 'days');
            }
        }
        // .clone().startOf('day') strips the time for a more accurate day diff
        var daysDiff = inputDate.clone().startOf('day').diff(start.clone().startOf('day'), 'days');
        start.add(daysDiff, 'days');
        end.add(daysDiff, 'days');

        history.replaceState({}, start.format('L'), '?date=' + start.format('YYYY-MM-DD'));

        dateFlatpickr.setDate(start.format('YYYY-MM-DD'));

        end_time = end.clone();
        if (mode == 'week') {
            // Get a week's worth
            end_time.add(6, 'days');
        }

        // Fetch events
        socket.send(JSON.stringify({
          'action': ACTION_GET_EVENTS,
          'start_time': start.format(),
          'end_time': end_time.format(),
          'mode': eventMode,
          'room_type_slug': roomTypeSlug,
          'employee_type': employeeType,
          'notify': true,
        }))

        if (mode == 'week') {
            // Update headers
            var weekday = start.clone();
            $('.schedule-weekday[data-day="7"]').html("Sun " + weekday.format("M/D"));
            weekday.add(1, "days");
            $('.schedule-weekday[data-day="1"]').html("Mon " + weekday.format("M/D"));
            weekday.add(1, "days");
            $('.schedule-weekday[data-day="2"]').html("Tue " + weekday.format("M/D"));
            weekday.add(1, "days");
            $('.schedule-weekday[data-day="3"]').html("Wed " + weekday.format("M/D"));
            weekday.add(1, "days");
            $('.schedule-weekday[data-day="4"]').html("Thu " + weekday.format("M/D"));
            weekday.add(1, "days");
            $('.schedule-weekday[data-day="5"]').html("Fri " + weekday.format("M/D"));
            weekday.add(1, "days");
            $('.schedule-weekday[data-day="6"]').html("Sat " + weekday.format("M/D"));
        }
    }

    function onBtnTodayClicked(event) {
        changeDate(moment().toDate());
    }

    function onBtnPrevClicked(event) {
        var current = start.clone();
        var days = (mode == 'week') ? 7 : 1;
        current.subtract(days, 'days');
        changeDate(current.toDate());
    }

    function onBtnNextClicked(event) {
        var current = start.clone();
        var days = (mode == 'week') ? 7 : 1;
        current.add(days, 'days');
        changeDate(current.toDate());
    }

    function onBtnCalendarClicked(event) {
        dateFlatpickr.open();
    }

    function onBtnModeClicked(event) {
        var newMode = $(event.target).data('mode');
        if (newMode != 'day' && newMode != 'week') {
            console.log("Unknown mode", newMode);
            return; // ignore for now
        } else if (mode == newMode) {
            return; // nothing to do
        }

        // Now we change modes
        mode = newMode;
        sessionStorage[STORAGE_KEY_MODE] = mode;

        // Reload with new mode.
        // NOTE: We have to redraw the entire schedule, so a page reload isn't too bad
        location.reload();
    }

    function onEventClicked(event) {
        var event = JSON.parse(unescape($(event.target).closest('.schedule-event').data('event')));
        console.log(event);

        dialogEventStart.setDate(moment(event.start).format('YYYY-MM-DD HH:mm'));
        dialogEventEnd.setDate(moment(event.end).format('YYYY-MM-DD HH:mm'));
        $('#id_event_type').val(event.event_type.pk);
        // Show delete button
        $('#btn_delete').show();

        if (eventMode == 'rooms') {
            $('#id_room_event_pk').val(event.id);
            $('#id_title').val(event.title);
            $('#id_description').val(event.description);
            $('#id_room').val(event.resource);
        } else if (eventMode == 'availability') {
            $('#id_availability_event_pk').val(event.id);
            $('#id_employee').val(event.resource);
        }

        if (event.rrule) {
            // Update form with rrule data
            rruleSetFromFormData(event.rrule);

            // store original start and end in case series is edited
            $('#id_start_time').data('rrule-original', event.orig_start);
            $('#id_end_time').data('rrule-original', event.orig_end);

            // Show dialog asking if should edit occurence or series
            showRRuleDialog();
        } else {
            showEventDialog();
        }
    }

    function onGridLineDblClicked(event) {
        var gridLine = $(event.target);
        var resourceIndex = gridLine.data('resource-index');
        var resource = resources[resourceIndex];
        var timeOffset = gridLine.data('time-offset');
        var dayIsoNumber = gridLine.data('day');

        var eventStart = start.clone();

        for (var i = 0; i < timeOffset; ++i) {
            eventStart.add(15, 'minutes');
        }

        if (mode == 'week') {
            // move eventStart into selected day
            while (eventStart.isoWeekday() != dayIsoNumber) {
                eventStart.add(1, 'days');
            }
        }

        var eventEnd = eventStart.clone();
        eventEnd.add(1, 'hours');

        dialogEventStart.setDate(eventStart.format('YYYY-MM-DD HH:mm'));
        dialogEventEnd.setDate(eventEnd.format('YYYY-MM-DD HH:mm'));
        //$('#id_event_type').val(); // Just use whatever last value was
        // Hide delete button
        $('#btn_delete').hide();

        if (eventMode == 'rooms') {
            $('#id_room_event_pk').val('');
            $('#id_title').val('New Event');
            $('#id_description').val('New Event Description');
            $('#id_room').val(resource.id);
        } else if (eventMode == 'availability') {
            $('#id_availability_event_pk').val('');
            $('#id_employee').val(resource.id);
        }

        showEventDialog();
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
    container.find('.schedule-btn-mode').on('click', onBtnModeClicked);

    // Setup flatpickr
    var dateFlatpickr = container.find('.schedule-txt-date').flatpickr({
        altInput: true,
        altFormat: "l, F j, Y",
        onChange: function(selectedDates) {
            changeDate(selectedDates[0]);
        },
    });

    // RRule Dialog Events
    $('#btn_rrule_occurrence').on('click', function() {
        // Remove pk so a new event will be created
        if (eventMode == 'rooms') {
            $('#id_parent_pk').val($('#id_room_event_pk').val());
            $('#id_room_event_pk').val('');
        } else if (eventMode == 'availability') {
            $('#id_parent_pk').val($('#id_availability_event_pk').val());
            $('#id_availability_event_pk').val('');
        }
        // Record what datetime to exclude in the original series
        $('#id_exclusion').val($('#id_start_time').val());
        // Turn off repeat
        rruleTurnOff();
        showEventDialog();
    });
    $('#btn_rrule_series').on('click', function() {
        // Change start and end to their original values
        var eventStart = moment($('#id_start_time').data('rrule-original'));
        var eventEnd = moment($('#id_end_time').data('rrule-original'));
        dialogEventStart.setDate(eventStart.format('YYYY-MM-DD HH:mm'));
        dialogEventEnd.setDate(eventEnd.format('YYYY-MM-DD HH:mm'));
        showEventDialog();
    });

    return {
        dummy: function() {
            console.log("dummy");
        },
    }
};

function showEventDialog() {
    $('#div_event_dialog').show();
    $('#div_rrule_dialog').hide();
    show_overlay_modal();
}

function showRRuleDialog() {
    $('#div_event_dialog').hide();
    $('#div_rrule_dialog').show();
    $('#overlay-modal').addClass('no-margin');
    show_overlay_modal();
}

$(function() {
    $('.schedule-container').each(function() {
        var schedule = createSchedule(this);
    });

    // Move event dialog into modal dialog and show by default
    $('#div_event_dialog').appendTo('#overlay-modal').show();
    // Move rrule dialog into modal dialog
    $('#div_rrule_dialog').appendTo('#overlay-modal');
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
    dialogEventEndOn = $('#id_rrule_end_on').flatpickr({
        altInput: true,
        dateFormat: "Y-m-d",
        altFormat: "F j, Y",
    })

    // Close dialog when cancel clicked
    $('#btn_cancel,#btn_rrule_cancel').on('click', function() {
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
        showEventDialog();
    }
});
