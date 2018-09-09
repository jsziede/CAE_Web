(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/**
* React logic for my_hours page.
*/

// See ScheduleConsumer for these constants
var ACTION_GET_EVENTS = 'get-events';
var ACTION_SEND_EVENTS = 'send-events';

function Resource(props) {
  return React.createElement('div', { className: 'schedule-resource',
    dangerouslySetInnerHTML: { __html: props.resource.html }
  });
}

var Event = function (_React$Component) {
  _inherits(Event, _React$Component);

  function Event(props) {
    _classCallCheck(this, Event);

    var _this = _possibleConstructorReturn(this, (Event.__proto__ || Object.getPrototypeOf(Event)).call(this, props));

    _this.state = {
      gridColumn: props.gridColumn
    };
    return _this;
  }

  _createClass(Event, [{
    key: 'render',
    value: function render() {
      return React.createElement(
        'div',
        {
          className: 'schedule-event',
          title: this.props.event.description,
          style: {
            gridColumn: this.state.gridColumn,
            gridRow: '' + this.props.rowStart + ' / span ' + this.props.span15Min
          }
        },
        moment(this.props.event.start).format('LT'),
        React.createElement('br', null),
        this.props.event.title,
        React.createElement('br', null),
        moment(this.props.event.end).format('LT')
      );
    }
  }]);

  return Event;
}(React.Component);

var Schedule = function (_React$Component2) {
  _inherits(Schedule, _React$Component2);

  function Schedule(props) {
    _classCallCheck(this, Schedule);

    var _this2 = _possibleConstructorReturn(this, (Schedule.__proto__ || Object.getPrototypeOf(Schedule)).call(this, props));

    _this2.state = {
      start: props.start,
      end: props.end,
      events: [
      // Debug event
      {
        id: 1, resource: 1, description: "A db course", title: "CS 3500",
        start: "2018-09-08T17:00:00Z", end: "2018-09-08T19:30:00Z"
      }],
      resources: [
      // Debug resources
      {
        id: 1, html: "C-122<br>36"
      }, {
        id: 2, html: "C-123<br>42"
      }, {
        id: 3, html: "C-124<br>34"
      }],
      resourceIdToColumn: {}
    };

    props.socket.addEventListener('message', function (message) {
      var data = JSON.parse(message.data);
      if (data.action == ACTION_SEND_EVENTS) {
        _this2.setState({
          events: data.events
        });
      }
    });
    return _this2;
  }

  _createClass(Schedule, [{
    key: 'test',
    value: function test() {
      var events = this.state.events.slice();
      events[0].title += "!";
      this.setState({
        events: events
        //start: moment("2018-09-08 13:05:00"),
      });
    }
  }, {
    key: 'createTimeHeadersAndGridLines',
    value: function createTimeHeadersAndGridLines() {
      var children = [];

      // Add Time Headers
      var hour = this.state.start.clone();
      var totalHours = 0;

      while (hour < this.state.end) {
        var key = "time-" + totalHours;
        children.push(React.createElement(
          'div',
          { key: key, className: 'schedule-time' },
          hour.format('LT')
        ));

        hour.add({ hours: 1 });
        ++totalHours;
      }

      // Add Grid Lines
      var gridLineKey = 0;
      for (var i = 0; i < this.state.resources.length; ++i) {
        var column = i * 2 + 2;
        for (var j = 0; j < totalHours * 4; ++j) {
          var row = j + 2;
          var _key = "grid-line-" + gridLineKey++;
          children.push(React.createElement('div', {
            key: _key,
            className: 'schedule-grid-line',
            style: {
              gridColumn: '' + column + ' / span 2',
              gridRow: row
            }
          }));
        }
      }

      return children;
    }
  }, {
    key: 'render',
    value: function render() {
      var _this3 = this;

      var resourceIdToColumn = {};
      var resourceIdToEvents = {};

      var resources = this.state.resources.map(function (resource, column) {
        resourceIdToColumn[resource.id] = column * 2 + 2;
        return React.createElement(Resource, { key: resource.id, resource: resource });
      });

      var events = this.state.events.map(function (event) {
        var start = moment(event.start);
        var end = moment(event.end);

        if (end < _this3.state.start || start > _this3.state.end) {
          // Event happens outside schedule, skip it
          console.log("Skipping event", event);
          return null;
        }

        var column = resourceIdToColumn[event.resource];
        var startDiff = Math.round(start.diff(_this3.state.start, 'second') / 3600); // hours
        var endDiff = Math.round(end.diff(_this3.state.end, 'second') / 3600); // hours
        var rowStart = Math.max(0, startDiff) * 4 + 2;
        var spanHours = Math.round(end.diff(start, 'second') / 3600);
        if (startDiff < 0) {
          // Reduce span if we cut off the start (Add a negative)
          spanHours += startDiff;
        }
        if (endDiff > 0) {
          // Reduce span if we cut off the end
          spanHours -= endDiff;
        }
        var span15Min = Math.round(spanHours * 4);

        // Check for overlapping events
        var resourceEvents = resourceIdToEvents[event.resource] || {};
        var hasEventConflict = false;
        Object.keys(resourceEvents).map(function (i) {
          var resourceEvent = resourceEvents[i];
          if (!start.isAfter(resourceEvent.end) && !end.isBefore(resourceEvent.start)) {
            hasEventConflict = true;
            // shrink event to span only 1 column
            // (No longer includes the '/ span 2')
            console.log(resourceEvent.element);
            resourceEvent.element.setState({
              gridColumn: '' + column
            });
          }
        });

        var columnSpan = 2;
        if (hasEventConflict) {
          ++column;
          columnSpan = 1;
        }

        var gridColumn = '' + column + ' / span ' + columnSpan;

        var eventElement = React.createElement(
          Event,
          {
            key: event.id,
            event: event,
            gridColumn: gridColumn,
            rowStart: rowStart,
            span15Min: span15Min
          },
          React.createElement(
            'div',
            { className: 'schedule-event-toolbar' },
            React.createElement(
              'button',
              { type: 'button', title: 'Edit' },
              '\u2699'
            )
          )
        );

        if (!hasEventConflict) {
          resourceEvents[event.id] = {
            element: eventElement,
            start: start,
            end: end
          };
          resourceIdToEvents[event.resource] = resourceEvents;
        }

        return eventElement;
      });

      return React.createElement(
        'div',
        null,
        React.createElement(
          'button',
          { onClick: function onClick() {
              return _this3.test();
            } },
          'Test'
        ),
        React.createElement(
          'div',
          { className: 'schedule-header' },
          '[put date selector here]'
        ),
        React.createElement(
          'div',
          { className: 'schedule-grid' },
          React.createElement('div', { className: 'schedule-header-spacer' }),
          resources,
          this.createTimeHeadersAndGridLines(),
          events
        )
      );
    }
  }]);

  return Schedule;
}(React.Component);

// Start of React logic.


function App() {
  var reactRoot = document.getElementById('react-root');
  var start = moment(reactRoot.dataset.start);
  var end = moment(reactRoot.dataset.end);

  // Establish socket connection.
  var domain = window.location.hostname;
  if (window.location.port) {
    domain += ":" + window.location.port;
  }
  var socket = new WebSocket('ws://' + domain + '/ws/caeweb/schedule/');

  // Send message to socket.
  socket.onopen = function (event) {
    socket.send(JSON.stringify({
      'action': ACTION_GET_EVENTS,
      'start_time': start.format(),
      'end_time': end.format(),
      'notify': true
    }));
  };

  return React.createElement(Schedule, { start: start, end: end, socket: socket });
}

// Render to page.
ReactDOM.render(App(), document.getElementById('react-root'));

},{}]},{},[1]);
