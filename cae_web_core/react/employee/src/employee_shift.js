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
        return (
            <tr>
                <td>{ this.props.clock_in }</td>
                <td>{ this.props.clock_out }</td>
            </tr>
        )
    }
}


export default Shift;
