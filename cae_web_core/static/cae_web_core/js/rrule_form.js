/* Used by RRuleFormMixin */
// Constants from python class
const RRULE_REPEAT_NEVER = 0;
const RRULE_REPEAT_DAILY = 1;
const RRULE_REPEAT_WEEKLY = 2;

function rruleShowWeekly(visible) {
    if (visible) {
        $('#id_rrule_weekly_on').prev().show();
        $('#id_rrule_weekly_on').show();
        $('.rrule-interval-day').hide();
        $('.rrule-interval-week').show();
    } else {
        $('#id_rrule_weekly_on').prev().hide();
        $('#id_rrule_weekly_on').hide();
        $('.rrule-interval-day').show();
        $('.rrule-interval-week').hide();
    }
}

function rruleShowAll(visible) {
    if (visible) {
        $('.rrule-interval').show();
        $('label[for="id_rrule_end_0"]').show();
        $('.rrule-end').show();
        // Caller must explicily call rruleShowWeekly(true);
    } else {
        $('.rrule-interval').hide();
        $('label[for="id_rrule_end_0"]').hide();
        $('.rrule-end').hide();
        rruleShowWeekly(false); // Hide this too
    }
}

function rruleCheckVisibility(element) {
    var repeat = element.val();
    if (repeat == RRULE_REPEAT_NEVER) {
        rruleShowAll(false);
    } else {
        rruleShowAll(true);
        rruleShowWeekly(repeat == RRULE_REPEAT_WEEKLY);
    }
}

$(function() {
    // Do initial check for visibility
    rruleCheckVisibility($('#id_rrule_repeat'));

    // Recheck for visibility on change
    $('#id_rrule_repeat').on('change', function() {
        rruleCheckVisibility($(this));
    });
});
