/**
* React logic for my_hours page.
*/

function Square(props) {
  return (
    <button
      className="square"
    >
      {props.value}
    </button>
  );
}


// Start of React logic.
function App() {
  return (
    <div>
      <h1>Test</h1>
      <Square value="Hello"/>
      <Square value="There"/>
    </div>
    );
  }


  // Render to page.
  ReactDOM.render(
    App(),
    document.getElementById('react-root')
    );
