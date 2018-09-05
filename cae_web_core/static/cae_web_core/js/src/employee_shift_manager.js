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
            shifts: json_shifts,
            last_shift: json_shifts[0],
        }
    }


    /**
     *Handle clock in/out button click.
     */
    handleClick() {

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
        }.bind(this);

        // Send message to socket.
        socket.onopen = function(event) {
            socket.send(JSON.stringify({
                'shift_submit': true,
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
                />
            );
        });

        // Elements to render for client.
        return (
            <div>
                <div>
                    <CurrentShift
                        key={ this.state.last_shift.pk }
                        clock_in={ this.state.last_shift.fields['clock_in'] }
                        clock_out={ this.state.last_shift.fields['clock_out'] }
                        onClick={() => this.handleClick() }
                    />
                </div>
                <hr /><hr />
                <table>
                    <tbody>
                    { shifts }
                    </tbody>
                </table>
            </div>
        )
    }
}


export default EmployeeShiftManager;
