/**
 * React logic for my_hours page.
 */


import { Fragment } from 'react';


import CurrentShift from './components/current_shift';
import PayPeriod from './components/pay_period';


const ACTION_GET_EVENTS = 'get-events';
const ACTION_SEND_EVENTS = 'send-events';


class MyHoursManager extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);

        this.state = {
            // Socket management variables.
            socket: new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/'),
            awaiting_socket_data: true,

            // Date management variables.
            current_time: new Date(),
            date_string_options: { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true, },

            // Passed socket variables.
            current_pay_period: null,
            displayed_pay_period: null,
            shifts: null,
            last_shift: null,

            // Calculated variables.
            week_1_shifts: [],
            week_2_shifts: [],
            week_1_hours: 0,
            week_2_hours: 0,
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
     * Logic for component initializing.
     * Runs before component load in.
     */
    componentWillMount() {
        // Set base socket event handler functions.
        var socket = this.state.socket;

        /**
         * Socket start.
         */
        this.state.socket.onopen = function(event) {
            // console.log('Socket opened.');

            // Send message to socket.
            this.state.socket.send(JSON.stringify({
                'action': ACTION_GET_EVENTS,
                'notify': true,
            }));

            // console.log('Initialization data sent.');
        }.bind(this)

        /**
         * Get socket message.
         */
        this.state.socket.onmessage = function(event) {
            // console.log('Recieved socket message.');
            var data = JSON.parse(event.data);

            // Save values from data as state.
            if (this.state.current_pay_period == null) {
                this.setState({
                    current_pay_period: JSON.parse(data['pay_period'])[0],
                });
            }

            try {
                var last_shift = JSON.parse(data['last_shift'])[0];
            } catch(err) {
                var current_time = this.state.current_time;
                var last_shift = {
                    pk: -1,
                    fields: {
                        'clock_in': current_time,
                        'clock_out': current_time,
                    }
                };
            }

            this.setState({
                displayed_pay_period: JSON.parse(data['pay_period'])[0],
                shifts: JSON.parse(data['shifts']),
                last_shift: last_shift,
            });

            if (this.state.awaiting_socket_data == false ) {
                this.calculatePayPeriodWeeks();
            }
        }.bind(this);

        /**
         * Socket error.
         */
        this.state.socket.onerror = function(event) {
            // console.log('An error occured.');
            // console.log(event);
        }

        /**
         * Socket terminated.
         */
        this.state.socket.onclose = function(event) {
            // console.log('Socket closed.');
            // console.log(event);
        }
    }


    /**
     * Logic for component post-initialization.
     * Runs after component load in.
     */
    componentDidMount() {
        // Ensure that the page processes a tick immediately on load.
        this.loadTimerTick();

        // Set component to run an update tick every second.
        this.intervalId = setInterval(
            () => this.loadTimerTick(),
            1000
        );
    }


    /**
     * Logic for component deconstruction.
     * Runs just before component destruction.
     */
    componentWillUnmount() {
        clearInterval(this.intervalId);
    }


    /**
     * Tick to check for data from socket on page load.
     */
    loadTimerTick() {
        // Tick and do nothing until state data is populated.
        if (this.state.current_pay_period != null && this.state.shifts != null) {
            // Clear tick timer.
            clearInterval(this.intervalId);

            // Process recieved data.
            this.processSocketData();

            this.setState({
                awaiting_socket_data: false,
            });

            this.calculatePayPeriodWeeks();

            // Set new tick timer for app run.
            this.intervalId = setInterval(
                () => this.runAppTick(),
                1000
            );
        }
    }


    /**
     * Tick to manage and run app.
     */
    runAppTick() {
        // Update current time.
        this.setState({
            current_time: new Date(),
        })

        // Recalculate hours worked.
        this.processSocketData()
    }


    /**
     * Calculate values based on passed data.
     */
    processSocketData() {
        if (this.state.last_shift.length == 0) {
            // No shifts exist for user in pay period. Create dummy shift.
            var current_time = this.state.current_time;
            this.setState({
                last_shift: {
                    pk: -1,
                    fields: {
                        'clock_in': current_time,
                        'clock_out': current_time,
                    },
                },
            });
        }

        this.calculateCurrentShift();
        this.calculateTotalHoursWorked();
    }


    /**
     * Sorts shifts based on week in pay period.
     */
    calculatePayPeriodWeeks() {

        var week_1_shifts = [];
        var week_2_shifts = [];

        // Calculate end of first week.
        var week_1_end = new Date(this.state.displayed_pay_period.fields['date_start']);
        week_1_end = week_1_end.setDate(week_1_end.getDate() + 7);

        // Loop through all shifts. Determine which week they belong to.
        this.state.shifts.forEach((shift) => {
            if (new Date(shift.fields['clock_in']).getTime() < week_1_end) {
                week_1_shifts.push(shift);
            } else {
                week_2_shifts.push(shift);
            }
        });

        // Save weeks as state.
        this.setState({
            week_1_shifts: week_1_shifts,
            week_2_shifts: week_2_shifts,
        });

        this.calculateCurrentShift();
        this.calculateTotalHoursWorked();
    }


    /**
     * Calculates total hours worked, by week.
     */
    calculateTotalHoursWorked() {
        var shift_start;
        var shift_end;
        var total_time = 0;

        // Calculate for week 1.
        this.state.week_1_shifts.forEach((shift) => {
            shift_start = new Date(shift.fields['clock_in']).getTime();

            // If clockout is null, use current time as calculation.
            if (shift.fields['clock_out'] != null) {
                shift_end = new Date(shift.fields['clock_out']).getTime();
            } else {
                shift_end = new Date(this.state.current_time);
            }

            total_time += (shift_end - shift_start);
        });

        this.setState({ week_1_hours: total_time });

        // Calculate for week 2.
        total_time = 0;
        this.state.week_2_shifts.forEach((shift) => {
            shift_start = new Date(shift.fields['clock_in']).getTime();

            // If clockout is null, use current time as calculation.
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
     * Calculates total hours in current shift.
     */
    calculateCurrentShift() {
        // Check if currently clocked in.
        if (this.state.last_shift.fields['clock_out'] == null) {

            // Clocked in. Calculate current_shift time trackers.
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
            // Not clocked in. Reset all current_shift trackers if currently set.
            this.setState({
                current_shift_hours: 0,
                current_shift_minutes: 0,
                current_shift_seconds: 0,
            })
        }
    }


    /**
     * Grab pay period of provided pk.
     */
    getNewPayPeriod(pay_period_index) {
        // Send message to socket.
        this.state.socket.send(JSON.stringify({
            'action': ACTION_SEND_EVENTS,
            'pay_period_pk': pay_period_index,
            'notify': true,
        }));
    }


    /**
     * Gets and displays previous period.
     * Note that this intentionally blocks until response is received.
     */
    handlePrevPeriodClick() {
        this.getNewPayPeriod(this.state.displayed_pay_period.pk - 1);
    }


    /**
     * Gets and displays current pay period.
     */
    handleCurrPeriodClick() {
        this.getNewPayPeriod(this.state.current_pay_period.pk);
    }


    /**
     * Gets and displays next pay period.
     */
    handleNextPeriodClick() {
        this.getNewPayPeriod(this.state.displayed_pay_period.pk + 1);
    }


    /**
     *Handle clock in/out button click.
     */
    handleShiftClick() {
        // Send message to socket.
        this.state.socket.send(JSON.stringify({
            'action': ACTION_SEND_EVENTS,
            'submit_shift': true,
            'notify': true,
        }));
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {

        // Elements to render for client.
        if (this.state.awaiting_socket_data) {
            return (
                <h2>Loading, please wait...</h2>
            )
        } else {
            var pay_period_start_display = new Date(this.state.displayed_pay_period.fields['date_start']);
            var pay_period_end_display = new Date(this.state.displayed_pay_period.fields['date_end']);
            var pay_period_string_options = { month: 'short', day: '2-digit', year: 'numeric' };

            var total_time = this.state.week_1_hours + this.state.week_2_hours;
            var total_hours = Math.trunc(total_time / this.one_hour);
            var total_minutes = Math.trunc((total_time - (total_hours * this.one_hour)) / this.one_minute);

            return (
                <Fragment className="center">
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
                </Fragment>
            )
        }
    }
}


// Start of React logic.
function App() {
    return (
        <MyHoursManager />
    );
}


// Render to page.
ReactDOM.render(
    App(),
    document.getElementById('react-root')
);
