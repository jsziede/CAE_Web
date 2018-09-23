/**
 * Core of React rendering for my_hours page.
 */

import CurrentShift from './current_shift';
import EmployeeShift from './employee_shift';


class EmployeeShiftManager extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);

        this.state = {
            date_string_options: { month: "short", day: "2-digit", year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true, },
            current_pay_period: json_pay_period[0],
            displayed_pay_period: json_pay_period[0],
            shifts: json_shifts,
            last_shift: json_shifts[0],
        }
    }


    /**
     * Logic to run on component load.
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
            this.setState({ shifts: JSON.parse(data.json_shifts) });
            this.setState({ last_shift: this.state.shifts[0] });
            this.setState({ displayed_pay_period: this.state.current_pay_period });
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
            this.setState({ displayed_pay_period: JSON.parse(data.json_pay_period)[0] });
            this.setState({ shifts: JSON.parse(data.json_shifts) });
        }.bind(this);

        // Send message to socket.
        socket.onopen = function(event) {
            socket.send(JSON.stringify({
                'pay_period': pay_period_index,
            }));
        }
    }


    /**
     * Handle message from socket.
     */
    handleData(data) {
        result = JSON.parse(data);
    }


    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
        // Calculate list of shifts.
        const shifts = [];
        this.state.shifts.forEach((shift) => {
            shifts.push(
                <EmployeeShift
                    key={ shift.pk }
                    clock_in={ shift.fields['clock_in'] }
                    clock_out={ shift.fields['clock_out'] }
                    date_string_options={ this.state.date_string_options }
                />
            );
        });

        var pay_period_display = new Date(this.state.displayed_pay_period.fields['period_start']);
        var pay_period_string_options = { month: "short", day: "2-digit", year: 'numeric' };

        // Elements to render for client.
        return (
            <div className="center">
                <div>
                    <CurrentShift
                        key={ this.state.last_shift.pk }
                        clock_in={ this.state.last_shift.fields['clock_in'] }
                        clock_out={ this.state.last_shift.fields['clock_out'] }
                        date_string_options={ this.state.date_string_options }
                        onClick={() => this.handleShiftClick() }
                    />
                </div>
                <hr /><hr />
                <div>
                    <h2>Pay Period starting on { pay_period_display.toLocaleDateString('en-US', pay_period_string_options) }</h2>
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
                    <table>
                        <tbody>
                        { shifts }
                        </tbody>
                    </table>
                </div>
            </div>
        )
    }
}


export default EmployeeShiftManager;
