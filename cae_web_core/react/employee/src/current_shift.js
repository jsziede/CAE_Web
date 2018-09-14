/**
 * Employee's "current shift" display.
 */

class CurrentShift extends React.Component {

    /**
     * Rendering and last minute calculations for client display.
     */
    render() {
        return (
            <div>
                <div>
                    <p>{ this.props.clock_in }</p>
                    <p>{ this.props.clock_out }</p>
                </div>
                <input
                    id="shift-submit"
                    type="button"
                    value="Clock In/Out"
                    onClick={() => this.props.onClick() }
                />
            </div>
        )
    }
}


export default CurrentShift;
