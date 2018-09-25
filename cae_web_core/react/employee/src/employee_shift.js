/**
 * A single employee shift.
 */

class Shift extends React.Component {

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
        var clock_in = null;
        var clock_out = null;
        var shift_total = 0;
        var shift_hours;
        var shift_minutes;
        var shift_time_display;

        // Check if valid clock in time. If none, is dummy shift.
        if (this.props.clock_in != null) {
            clock_in = new Date(this.props.clock_in);

            // Check for valid clock out time. If none, use passed prop paremeters.
            if (this.props.clock_out != null) {
                clock_out = new Date(this.props.clock_out);
                shift_total = clock_out.getTime() - clock_in.getTime();
                shift_hours = Math.trunc(shift_total / this.one_hour);
                shift_minutes = Math.trunc((shift_total - (shift_hours * this.one_hour)) / this.one_minute);
            } else {
                shift_hours = this.props.current_shift_hours;
                shift_minutes = this.props.current_shift_minutes;
            }
            shift_time_display = shift_hours + ' Hours ' + shift_minutes + ' Minutes';
        } else {
            shift_time_display = 'N/A';
        }

        return (
            <tr>
                { clock_in ? (
                        <td>{ clock_in.toLocaleDateString('en-US', this.props.date_string_options) }</td>
                    ) : (
                        <td>N/A</td>
                    )
                }
                { clock_out ? (
                        <td>{ clock_out.toLocaleDateString('en-US', this.props.date_string_options) }</td>
                    ) : (
                        <td>N/A</td>
                    )
                }
                <td>{ shift_time_display }</td>
            </tr>
        )
    }
}


export default Shift;
