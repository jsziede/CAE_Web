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
            date_string_options: { month: "short", day: "2-digit", year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true, },
            current_time: new Date(),
            hour_difference: -1,
            minute_difference: -1,
            second_difference: -1,
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

            var time_difference = new Date() - new Date(this.props.clock_in);
            var hour_difference = Math.trunc(time_difference / this.one_hour);
            var minute_difference = Math.trunc((time_difference - (hour_difference * this.one_hour)) / this.one_minute);
            var second_difference = Math.trunc( (time_difference - (hour_difference * this.one_hour) - (minute_difference * this.one_minute)) / this.one_second );

            // Update time difference trackers.
            this.setState({
                hour_difference: hour_difference,
                minute_difference: minute_difference,
                second_difference: second_difference,
            });

        } else {
            // Reset all trackers if currently set.
            this.setState({
                hour_difference: -1,
                minute_difference: -1,
                second_difference: -1,
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
                <p>Clocked in: { clock_in.toLocaleDateString('en-US', this.state.date_string_options) }</p>
                <p>
                    ShiftLength: &nbsp;
                    { this.state.hour_difference.toString() } Hours &nbsp;
                    { this.state.minute_difference.toString() } Minutes &nbsp;
                    { this.state.second_difference.toString() } Seconds &nbsp;
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
