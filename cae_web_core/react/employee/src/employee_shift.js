/**
 * A single employee shift.
 */

class Shift extends React.Component {

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
        var clock_in = new Date(this.props.clock_in);
        var clock_out = null;

        if (this.props.clock_out != null) {
            clock_out = new Date(this.props.clock_out);
        }

        return (
            <tr>
                <td>{ clock_in.toLocaleDateString('en-US', this.props.date_string_options) }</td>
                {clock_out && // If statement. Only displays if clock_out is not null.
                    <td>{ clock_out.toLocaleDateString('en-US', this.props.date_string_options) }</td>
                }
            </tr>
        )
    }
}


export default Shift;
