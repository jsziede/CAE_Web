/**
 * Employee's "current shift" display.
 */

class CurrentShift extends React.Component {

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
        var clock_in;
        var time_display;
        var submit_value;

        // Handle display differently if clocked in or clocked out.
        if (this.props.clock_out == null) {
            clock_in = new Date(this.props.clock_in);
            time_display = <div className="time-display">
                <p>Clocked in: { clock_in.toLocaleDateString('en-US', this.props.date_string_options) }</p>
                <p>
                    Shift Length: &nbsp;
                    { this.props.shift_hours.toString() } Hours &nbsp;
                    { this.props.shift_minutes.toString() } Minutes &nbsp;
                    { this.props.shift_seconds.toString() } Seconds &nbsp;
                </p>
            </div>;
            submit_value = "Clock Out";
        } else {
            time_display = <div className="time-display"></div>;
            submit_value = "Clock In";
        }

        return (
            <div className="current-shift">
                <h2>Current Shift</h2>
                { time_display }
                <input
                    id="shift-submit"
                    type="button"
                    value={ submit_value }
                    onClick={() => this.props.onClick() }
                />
            </div>
        )
    }
}


export default CurrentShift;
