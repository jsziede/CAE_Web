var schedule = (function() {
    var x = 23;

    function createHeader(container) {
        // <div class="buttons"><button>Today</button><button>🞀</button><button>🞂</button></div>
        console.log(container);

        var buttons = '<div class="buttons"><button class="schedule-btn-today">Today</button><button class="schedule-btn-prev"><i class="fas fa-angle-left"></i></button><button class="schedule-btn-next"><i class="fas fa-angle-right"></i></button></div>';
        var calendarButton = '<button class="schedule-btn-calendar"><i class="fas fa-calendar-alt"></i></button>';
        var dateInput = '<input type="text" class="schedule-txt-date">';

        header = $('<div>', {
            class: "schedule-header",
            html: `${buttons}${calendarButton}${dateInput}`,
        });

        return header;
    }

    function createGrid(container) {
        var start = container.data('start');
        var end = container.data('end');
        var resources = container.data('resources');

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

        gridLineDivs += '<div class="schedule-grid-line" style="grid-area: 2 / 2 / auto / span 2;"></div>';

        grid = $('<div>', {
            class: "schedule-grid",
            html: `<div class="schedule-header-spacer"></div>${resourcesDivs}${timeDivs}${gridLineDivs}`,
        });

        return grid;
    }

    return {
        initAll: function() {
            $('.schedule-container').each(function() {
                var container = $(this);
                var start = moment(container.data('start'));
                var end = moment($(this).data('end'));
                container.data('start', start);
                container.data('end', end);


                container.empty();
                var header = createHeader(container);
                var grid = createGrid(container);

                container.append(header);
                container.append(grid);

            });

            // Run flatpickr for all date inputs
            $('.schedule-txt-date').flatpickr({
                altInput: true,
                altFormat: "F j, Y",
            });
        },
    }
})();

$(function() {
    schedule.initAll();
});