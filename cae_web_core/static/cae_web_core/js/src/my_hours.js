/**
 * React logic for my_hours page.
 */

import EmployeeShiftManager from './employee_shift_manager';


// Start of React logic.
function App() {
    return (
        <EmployeeShiftManager />
    );
}


// Render to page.
ReactDOM.render(
    App(),
    document.getElementById('react-root')
);
