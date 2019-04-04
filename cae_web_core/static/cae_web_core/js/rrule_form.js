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

function rruleSetFromFormData(formData) {
    // Fill out the form with given form data.
    // See cae_web_core/forms.py RRuleFormMixin.rrule_get_form_data().
    Object.keys(formData).map((key) => {
        const value = formData[key];
        if (key == "id_rrule_weekly_on") {
            // Checkboxes must be handled differently
            value.map(function(x) {
                $(`input[name="rrule_weekly_on"][value="${x}"]`).prop('checked', true).trigger('change');
            });
        } else if (key == "id_rrule_end") {
            // Radios must be handled differently
            $(`input[name="rrule_end"][value="${value}"]`).prop('checked', true).trigger('change');
        } else {
            $('#' + key).val(value).trigger('change');
        }
    });
}

$(function() {
    // Do initial check for visibility
    rruleCheckVisibility($('#id_rrule_repeat'));

    // Recheck for visibility on change
    $('#id_rrule_repeat').on('change', function() {
        rruleCheckVisibility($(this));
    });
});
