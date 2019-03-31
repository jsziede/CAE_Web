"""CAE Web Core Widgets"""
from django.forms import widgets


class RRuleWidget(widgets.MultiWidget):
    REPEAT_NEVER = 0
    REPEAT_DAILY = 1
    REPEAT_WEEKLY = 2
    REPEAT_CHOICES = (
        (REPEAT_NEVER, "Never"),
        (REPEAT_DAILY, "Daily"),
        (REPEAT_WEEKLY, "Weekly"),
    )
    def __init__(self, attrs=None):
        _widgets = (
            widgets.Select(attrs=attrs, choices=self.REPEAT_CHOICES),
            widgets.CheckboxInput(attrs=attrs),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        # Convert RRULE string into our form values
        if value:
            return [self.REPEAT_DAILY, True]
        return [self.REPEAT_NEVER, False]

    def value_from_datadict(self, data, files, name):
        # Convert our form values into RRULE string
        # datelist = [
        #     widget.value_from_datadict(data, files, name + '_%s' % i)
        #     for i, widget in enumerate(self.widgets)]
        # try:
        #     D = date(
        #         day=int(datelist[0]),
        #         month=int(datelist[1]),
        #         year=int(datelist[2]),
        #     )
        # except ValueError:
        #     return ''
        # else:
        #     return str(D)
        return ''