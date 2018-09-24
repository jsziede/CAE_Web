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
        var clock_in = new Date(this.props.clock_in);
        var clock_out = null;
        var shift_total = null;

        if (this.props.clock_out != null) {
            clock_out = new Date(this.props.clock_out);
            shift_total = clock_out.getTime() - clock_in.getTime();
        } else {
            shift_total = (new Date()).getTime() - clock_in.getTime();
        }

        var shift_hours = Math.trunc(shift_total / this.one_hour);
        var shift_minutes = Math.trunc((shift_total - (shift_hours * this.one_hour)) / this.one_minute);

        return (
            <tr>
                <td>{ clock_in.toLocaleDateString('en-US', this.props.date_string_options) }</td>
                { clock_out ? (
                        <td>{ clock_out.toLocaleDateString('en-US', this.props.date_string_options) }</td>
                    ) : (
                        <td>N/A</td>
                    )
                }
                <td>{ shift_hours } Hours { shift_minutes } Minutes</td>
            </tr>
        )
    }
}


export default Shift;
