/**
 * Employee's "current shift" display.
 */

class CurrentShift extends React.Component {

    /**
     * Constructor for component.
     */
    constructor(props) {
        super(props);

        // State variables.
        this.state = {
            current_time: new Date(),
            shift_hours: -1,
            shift_minutes: -1,
            shift_seconds: -1,
        };

        // Static variables.
        this.one_second = 1000;
        this.one_minute = 60 * this.one_second;
        this.one_hour = 60 * this.one_minute;
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
        if (this.props.clock_out == null) {

            var shift_total = new Date() - new Date(this.props.clock_in);
            var shift_hours = Math.trunc(shift_total / this.one_hour);
            var shift_minutes = Math.trunc((shift_total - (shift_hours * this.one_hour)) / this.one_minute);
            var shift_seconds = Math.trunc( (shift_total - (shift_hours * this.one_hour) - (shift_minutes * this.one_minute)) / this.one_second );

            // Update time difference trackers.
            this.setState({
                shift_hours: shift_hours,
                shift_minutes: shift_minutes,
                shift_seconds: shift_seconds,
            });

        } else {
            // Reset all trackers if currently set.
            this.setState({
                shift_hours: -1,
                shift_minutes: -1,
                shift_seconds: -1,
            })
        }
    }

    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
        var clock_in;
        var clock_out;
        var time_display;
        var submit_value;

        // Handle display differently if clocked in or clocked out.
        if (this.props.clock_out == null) {
            clock_in = new Date(this.props.clock_in);
            clock_out = new Date(this.props.clock_out);
            time_display = <div className="time-display">
                <p>Clocked in: { clock_in.toLocaleDateString('en-US', this.props.date_string_options) }</p>
                <p>
                    Shift Length: &nbsp;
                    { this.state.shift_hours.toString() } Hours &nbsp;
                    { this.state.shift_minutes.toString() } Minutes &nbsp;
                    { this.state.shift_seconds.toString() } Seconds &nbsp;
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
