/**
 * Core of React rendering for my_hours page.
 */

import CurrentShift from './current_shift';
import EmployeeShift from './employee_shift';
import PayPeriod from './pay_period';


class EmployeeShiftManager extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);

        this.state = {
            current_time: new Date(),
            date_string_options: { month: "short", day: "2-digit", hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true, },

            current_pay_period: json_pay_period[0],
            displayed_pay_period: json_pay_period[0],

            shifts: json_shifts,
            week_1_shifts: [],
            week_2_shifts: [],
            week_1_hours: 0,
            week_2_hours: 0,
            last_shift: json_last_shift[0],

            current_shift_hours: 0,
            current_shift_minutes: 0,
            current_shift_seconds: 0,
        };

        // Static variables.
        this.one_second = 1000;
        this.one_minute = 60 * this.one_second;
        this.one_hour = 60 * this.one_minute;
    }


    /**
     * Logic to run before component load.
     */
    componentWillMount() {
        // If no shiffts are defined yet for this pay period, create a dummy "last shift" to prevent render errors.
        if (this.state.last_shift == null) {

            this.setState({
                last_shift: {
                    pk: -1,
                    fields: {
                        "clock_in": new Date(),
                        "clock_out": new Date(),
                    },
                }
            });
        }

        this.calculateWeeksInPayPeriod();
    }


    /**
     * Logic to run on component load.
     */
    componentDidMount() {
        // Ensure that the page processes a tick immediately on load.
        this.tick();

        // Set component to run an update tick every second.
        this.intervalId = setInterval(
            () => this.tick(),
            1000
        );
    }


    /**
     * Logic to run on component unload.
     */
    componentWillUnmount() {
        clearInterval(this.intervalId);
    }


    /**
     * Functions to run on each tick.
     */
    tick() {
        this.setState({
            current_time: new Date(),
        });

        // Check if currently clocked in.
        if (this.state.last_shift.fields['clock_out'] == null) {

            // Calculate shift time trackers.
            var shift_total = this.state.current_time - new Date(this.state.last_shift.fields['clock_in']);
            var shift_hours = Math.trunc(shift_total / this.one_hour);
            var shift_minutes = Math.trunc((shift_total - (shift_hours * this.one_hour)) / this.one_minute);
            var shift_seconds = Math.trunc( (shift_total - (shift_hours * this.one_hour) - (shift_minutes * this.one_minute)) / this.one_second );

            // Update shift time trackers.
            this.setState({
                current_shift_hours: shift_hours,
                current_shift_minutes: shift_minutes,
                current_shift_seconds: shift_seconds,
            });

        } else {
            // Reset all trackers if currently set.
            this.setState({
                current_shift_hours: 0,
                current_shift_minutes: 0,
                current_shift_seconds: 0,
            })
        }

        this.calculateWeeksInPayPeriod();
    }


    /**
     *Handle clock in/out button click.
     */
    handleShiftClick() {
        // Establish socket connection.
        var socket = new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/');

        socket.beforeunload = function() {
            socket.close();
        }

        // Handle incoming socket message event. Note the bind(this) to access React object state within function.
        socket.onmessage = function(message) {
            var data = JSON.parse(message.data);
            this.setState({
                shifts: JSON.parse(data.json_shifts),
                last_shift: JSON.parse(data.json_last_shift)[0],
                displayed_pay_period: this.state.current_pay_period,
            });
        }.bind(this);

        // Send message to socket.
        socket.onopen = function(event) {
            socket.send(JSON.stringify({
                'shift_submit': true,
            }));
        }
    }


    handlePrevPeriodClick() {
        this.getNewPayPeriod(this.state.displayed_pay_period.pk - 1);
    }


    handleCurrPeriodClick() {
        this.getNewPayPeriod(this.state.current_pay_period.pk);
    }


    handleNextPeriodClick() {
        this.getNewPayPeriod(this.state.displayed_pay_period.pk + 1);
    }


    /**
     * Grab pay period of provided pk.
     */
    getNewPayPeriod(pay_period_index) {
        // Establish socket connection.
        var socket = new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/');

        socket.beforeunload = function() {
            socket.close();
        }

        // Handle incoming socket message event. Note the bind(this) to access React object state within function.
        socket.onmessage = function(message) {
            var data = JSON.parse(message.data);
            this.setState({
                displayed_pay_period: JSON.parse(data.json_pay_period)[0],
                shifts: JSON.parse(data.json_shifts)
            });
            this.calculateWeeksInPayPeriod();
        }.bind(this);

        // Send message to socket.
        socket.onopen = function(event) {
            socket.send(JSON.stringify({
                'pay_period': pay_period_index,
            }));
        }
    }


    /**
     * Sorts shifts based on week in pay period.
     */
    calculateWeeksInPayPeriod() {

        var week_1_shifts = [];
        var week_2_shifts = [];
        var week_1_end = new Date(this.state.displayed_pay_period.fields['period_start']);

        week_1_end = week_1_end.setDate(week_1_end.getDate() + 7);

        this.state.shifts.forEach((shift) => {
            if (new Date(shift.fields['clock_in']).getTime() < week_1_end) {
                week_1_shifts.push(shift);
            } else {
                week_2_shifts.push(shift);
            }
        });

        this.setState({
            week_1_shifts: week_1_shifts,
            week_2_shifts: week_2_shifts,
        });

        this.calculateHoursWorked();
    }


    /**
     * Calculates total hours worked, by week.
     */
    calculateHoursWorked() {
        var shift_start;
        var shift_end;
        var total_time = 0;

        // Calculate for week 1.
        this.state.week_1_shifts.forEach((shift) => {
            shift_start = new Date(shift.fields['clock_in']).getTime();
            if (shift.fields['clock_out'] != null) {
                shift_end = new Date(shift.fields['clock_out']).getTime();
            } else {
                shift_end = new Date(this.state.current_time);
            }
            total_time += (shift_end - shift_start);
        });
        this.setState({ week_1_hours: total_time });
        total_time = 0;

        // Calculate for week 2.
        this.state.week_2_shifts.forEach((shift) => {
            shift_start = new Date(shift.fields['clock_in']).getTime();
            if (shift.fields['clock_out'] != null) {
                shift_end = new Date(shift.fields['clock_out']).getTime();
            } else {
                shift_end = new Date(this.state.current_time);
            }
            total_time += (shift_end - shift_start);
        });
        this.setState({ week_2_hours: total_time });
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {

        var pay_period_start_display = new Date(this.state.displayed_pay_period.fields['period_start']);
        var pay_period_end_display = new Date(this.state.displayed_pay_period.fields['period_end']);
        var pay_period_string_options = { month: "short", day: "2-digit", year: 'numeric' };

        var total_time = this.state.week_1_hours + this.state.week_2_hours;
        var total_hours = Math.trunc(total_time / this.one_hour);
        var total_minutes = Math.trunc((total_time - (total_hours * this.one_hour)) / this.one_minute);

        // Elements to render for client.
        return (
            <div className="center">
                <CurrentShift
                    clock_in={ this.state.last_shift.fields['clock_in'] }
                    clock_out={ this.state.last_shift.fields['clock_out'] }
                    shift_hours={ this.state.current_shift_hours }
                    shift_minutes={ this.state.current_shift_minutes }
                    shift_seconds={ this.state.current_shift_seconds }
                    date_string_options={ this.state.date_string_options }
                    onClick={() => this.handleShiftClick() }
                />
                <div className="pay-period center">
                    <h2>
                        Pay Period of&nbsp;
                        { pay_period_start_display.toLocaleDateString('en-US', pay_period_string_options) }
                        &nbsp;Through&nbsp;
                        { pay_period_end_display.toLocaleDateString('en-US', pay_period_string_options) }
                    </h2>
                    <div>
                        <input
                            id="prev_pay_period_button"
                            type="button"
                            value="&#9204;"
                            onClick={() => this.handlePrevPeriodClick() }
                        />
                        <input
                            id="curr_pay_period_button"
                            type="button"
                            value="Current Pay Period"
                            onClick={() => this.handleCurrPeriodClick() }
                        />
                        <input
                            id="next_pay_period_button" type="button"
                            value="&#9205;"
                            onClick={() => this.handleNextPeriodClick() }
                        />
                    </div>
                    <p>Total Pay Period Hours: { total_hours } Hours { total_minutes } Minutes</p>
                    <PayPeriod
                        table_title='Week 1'
                        displayed_pay_period={ this.state.displayed_pay_period }
                        shifts={ this.state.week_1_shifts }
                        current_shift_hours={ this.state.current_shift_hours }
                        current_shift_minutes={ this.state.current_shift_minutes }
                        week_total={ this.state.week_1_hours }
                        date_string_options={ this.state.date_string_options }
                    />
                    <PayPeriod
                        table_title='Week 2'
                        displayed_pay_period={ this.state.displayed_pay_period }
                        shifts={ this.state.week_2_shifts }
                        current_shift_hours={ this.state.current_shift_hours }
                        current_shift_minutes={ this.state.current_shift_minutes }
                        week_total={ this.state.week_2_hours }
                        date_string_options={ this.state.date_string_options }
                    />
                </div>
            </div>
        )
    }
}


export default EmployeeShiftManager;
