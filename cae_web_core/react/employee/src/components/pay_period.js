/**
 * Core of React rendering for my_hours page.
 */

import CurrentShift from './current_shift';
import PayPeriodRow from './pay_period_row';


class PayPeriod extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);

        // Static variables.
        this.one_second = 1000;
        this.one_minute = 60 * this.one_second;
        this.one_hour = 60 * this.one_minute;
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
        // Calculate list of shifts.
        const shifts = [];
        if (this.props.shifts.length > 0) {
            this.props.shifts.forEach((shift) => {
                shifts.push(
                    <PayPeriodRow
                        key={ shift.pk }
                        clock_in={ shift.fields['clock_in'] }
                        clock_out={ shift.fields['clock_out'] }
                        current_shift_hours={ this.props.current_shift_hours }
                        current_shift_minutes={ this.props.current_shift_minutes }
                        date_string_options={ this.props.date_string_options }
                    />
                );
            });
        } else {
            shifts.push(
                <PayPeriodRow
                    key='N/A'
                    clock_in={ null }
                    clock_out={ null }
                    date_string_options={ this.props.date_string_options }
                />
            );
        }

        // Date to string display.
        var pay_period_display = new Date(this.props.displayed_pay_period.fields['period_start']);
        var pay_period_string_options = { month: "short", day: "2-digit", year: 'numeric' };

        // Calculate week hours.
        var week_hours = Math.trunc(this.props.week_total / this.one_hour);
        var week_minutes = Math.trunc((this.props.week_total - (week_hours * this.one_hour)) / this.one_minute);

        return (
            <table>
                <thead>
                    <tr>
                        <th colSpan="3"><h3>{ this.props.table_title }</h3></th>
                    </tr>
                    <tr>
                        <th><h4>Clock In</h4></th>
                        <th><h4>Clock Out</h4></th>
                        <th><h4>Shift Length</h4></th>
                    </tr>
                </thead>
                <tbody>
                    { shifts }
                </tbody>
                <tfoot>
                    <tr>
                        <th colSpan="3"><h3>Week Total: { week_hours } Hours { week_minutes } Minutes</h3></th>
                    </tr>
                </tfoot>
            </table>
        )
    }
}


export default PayPeriod;
