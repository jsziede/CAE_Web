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
                    <EmployeeShift
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
                <EmployeeShift
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

        return (
            <div className="pay-period center">
                <h2>Pay Period starting on { pay_period_display.toLocaleDateString('en-US', pay_period_string_options) }</h2>
                <div>
                    <input
                        id="prev_pay_period_button"
                        type="button"
                        value="&#9204;"
                        onClick={() => this.props.handlePrevPeriodClick() }
                    />
                    <input
                        id="curr_pay_period_button"
                        type="button"
                        value="Current Pay Period"
                        onClick={() => this.props.handleCurrPeriodClick() }
                    />
                    <input
                        id="next_pay_period_button" type="button"
                        value="&#9205;"
                        onClick={() => this.props.handleNextPeriodClick() }
                    />
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Clock In</th>
                            <th>Clock Out</th>
                            <th>Shift Length</th>
                        </tr>
                    </thead>
                    <tbody>
                        { shifts }
                    </tbody>
                </table>
            </div>
        )
    }
}


export default EmployeeShiftManager;
