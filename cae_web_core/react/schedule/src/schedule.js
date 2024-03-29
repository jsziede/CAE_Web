/**
* React logic for my_hours page.
*/

// See ScheduleConsumer for these constants
const ACTION_GET_EVENTS = 'get-events'
const ACTION_SEND_EVENTS = 'send-events'

function Resource(props) {
  return (
    <div className="schedule-resource"
      dangerouslySetInnerHTML={{__html: props.resource.html}}
    />
  )
}

class Event extends React.Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <div
        className="schedule-event"
        title={this.props.event.description}
        style={{
          gridColumn: this.props.gridColumn,
          gridRow: '' + this.props.rowStart + ' / span ' + this.props.span15Min,
        }}
      >
        <div className="schedule-event-toolbar">
          <button type="button" title="Edit">&#9881;</button>
        </div>
        {moment(this.props.event.start).format('LT')}<br/>
        {this.props.event.title}<br/>
        {moment(this.props.event.end).format('LT')}
      </div>
    )
  }
}


class Schedule extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      start: props.start,
      end: props.end,
      events: [
        // Debug event
        {
          id: 1, resource: 1, description: "A db course", title: "CS 3500",
          start: "2018-09-08T17:00:00Z", end: "2018-09-08T19:30:00Z",
        },
      ],
      resources: [
        // Debug resources
        {
          id: 1, html: "C-122<br>36",
        },
        {
          id: 2, html: "C-123<br>42",
        },
        {
          id: 3, html: "C-124<br>34",
        },
      ],
      resourceIdToColumn: {},
    }

    props.socket.addEventListener('message', (message) => {
      var data = JSON.parse(message.data);
      if (data.action == ACTION_SEND_EVENTS) {
        this.setState({
          events: data.events,
        })
      }
    })
  }

  test() {
    const events = this.state.events.slice()
    events[0].title += "!"
    this.setState({
      events: events,
      //start: moment("2018-09-08 13:05:00"),
    })
  }

  createTimeHeadersAndGridLines() {
    const children = []

    // Add Time Headers
    const hour = this.state.start.clone()
    var totalHours = 0

    while (hour < this.state.end) {
      const key = "time-" + totalHours
      children.push(
        <div key={key} className="schedule-time">
          {hour.format('LT')}
        </div>
      )

      hour.add({ hours: 1})
      ++totalHours
    }

    // Add Grid Lines
    var gridLineKey = 0
    for (var i = 0; i < this.state.resources.length; ++i) {
      var column = i * 2 + 2
      for (var j = 0; j < totalHours * 4; ++j) {
        var row = j + 2
        const key="grid-line-" + gridLineKey++
        children.push(
          <div
            key={key}
            className="schedule-grid-line"
            style={{
              gridColumn: '' + column + ' / span 2',
              gridRow: row,
            }}
          />
        )
      }
    }

    return children
  }

  render() {
    const resourceIdToColumn = {}
    const resourceIdToEvents = {}

    const resources = this.state.resources.map((resource, column) => {
      resourceIdToColumn[resource.id] = column * 2 + 2
      return (
        <Resource key={resource.id} resource={resource}/>
      )
    })

    // keep track of events that have been processsed
    // we may need to update some before actually creating React elements
    const processedEvents = {}

    this.state.events.map((event) => {
      const start = moment(event.start)
      const end = moment(event.end)

      if (end < this.state.start || start > this.state.end) {
        // Event happens outside schedule, skip it
        console.log("Skipping event", event)
        return null
      }

      var column = resourceIdToColumn[event.resource]
      const startDiff = Math.round(start.diff(this.state.start, 'second') / 3600); // hours
      const endDiff = Math.round(end.diff(this.state.end, 'second') / 3600); // hours
      const rowStart = Math.max(0, startDiff) * 4 + 2;
      var spanHours = Math.round(end.diff(start, 'second') / 3600);
      if (startDiff < 0) {
          // Reduce span if we cut off the start (Add a negative)
          spanHours += startDiff;
      }
      if (endDiff > 0) {
          // Reduce span if we cut off the end
          spanHours -= endDiff;
      }
      const span15Min = Math.round(spanHours * 4);

      // Check for overlapping events
      const resourceEvents = resourceIdToEvents[event.resource] || {};
      var hasEventConflict = false;
      Object.keys(resourceEvents).map((i) => {
        const resourceEvent = resourceEvents[i];
        if (!start.isAfter(resourceEvent.event.end) &&
            !end.isBefore(resourceEvent.event.start)) {
            hasEventConflict = true;
            // shrink event to span only 1 column
            // (No longer includes the '/ span 2')
            resourceEvent.gridColumn = '' + column
        }
      })

      var columnSpan = 2;
      if (hasEventConflict) {
          ++column;
          columnSpan = 1;
      }

      const gridColumn = '' + column + ' / span ' + columnSpan

      const data = {
        event: event,
        gridColumn: gridColumn,
        rowStart: rowStart,
        span15Min: span15Min,
      }

      processedEvents[event.id] = data

      if (!hasEventConflict) {
        resourceEvents[event.id] = data
        resourceIdToEvents[event.resource] = resourceEvents
      }
    })

    // Now create event elements
    const events = [];
    Object.keys(processedEvents).map((i) => {
      const data = processedEvents[i];
      events.push(
        <Event
          key={data.event.id}
          event={data.event}
          gridColumn={data.gridColumn}
          rowStart={data.rowStart}
          span15Min={data.span15Min}
        />
      )
    })

    return (
      <div>
        <button onClick={() => this.test()}>Test</button>
        <div className="schedule-header">
          [put date selector here]
        </div>
        <div className="schedule-grid">
          <div className="schedule-header-spacer"></div>
          {resources}
          {this.createTimeHeadersAndGridLines()}
          {events}
        </div>
      </div>
    )
  }
}


// Start of React logic.
function App() {
  const reactRoot = document.getElementById('react-root')
  const start = moment(reactRoot.dataset.start)
  const end = moment(reactRoot.dataset.end)

  // Establish socket connection.
  var domain = window.location.hostname
  if (window.location.port) {
    domain += ":" + window.location.port
  }
  var socket = new WebSocket('ws://' + domain + '/ws/caeweb/schedule/');

  // Send message to socket.
  socket.onopen = function(event) {
    socket.send(JSON.stringify({
      'action': ACTION_GET_EVENTS,
      'start_time': start.format(),
      'end_time': end.format(),
      'notify': true,
    }))
  }

  return (
    <Schedule start={start} end={end} socket={socket}/>
  )
}


// Render to page.
ReactDOM.render(
  App(),
  document.getElementById('react-root')
)
