(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/**
 * Employee's "current shift" display.
 */

var CurrentShift = function (_React$Component) {
    _inherits(CurrentShift, _React$Component);

    /**
     * Constructor for component.
     */
    function CurrentShift(props) {
        _classCallCheck(this, CurrentShift);

        // State variables.
        var _this = _possibleConstructorReturn(this, (CurrentShift.__proto__ || Object.getPrototypeOf(CurrentShift)).call(this, props));

        _this.state = {
            current_time: new Date(),
            hour_difference: -1,
            minute_difference: -1,
            second_difference: -1
        };

        // Static variables.
        _this.one_second = 1000;
        _this.one_minute = 60 * _this.one_second;
        _this.one_hour = 60 * _this.one_minute;
        return _this;
    }

    /**
     * Logic to run on component load.
     */


    _createClass(CurrentShift, [{
        key: "componentDidMount",
        value: function componentDidMount() {
            var _this2 = this;

            // Ensure that the page processes a tick immediately on load.
            this.tick();

            // Set component to run an update tick every second.
            this.intervalId = setInterval(function () {
                return _this2.tick();
            }, 1000);
        }

        /**
         * Logic to run on component unload.
         */

    }, {
        key: "componentWillUnmount",
        value: function componentWillUnmount() {
            clearInterval(this.intervalId);
        }

        /**
         * Functions to run on each tick.
         */

    }, {
        key: "tick",
        value: function tick() {
            this.setState({
                current_time: new Date()
            });

            // Check if currently clocked in.
            if (this.props.clock_out == null) {

                var time_difference = new Date() - new Date(this.props.clock_in);
                var hour_difference = Math.trunc(time_difference / this.one_hour);
                var minute_difference = Math.trunc((time_difference - hour_difference * this.one_hour) / this.one_minute);
                var second_difference = Math.trunc((time_difference - hour_difference * this.one_hour - minute_difference * this.one_minute) / this.one_second);

                // Update time difference trackers.
                this.setState({
                    hour_difference: hour_difference,
                    minute_difference: minute_difference,
                    second_difference: second_difference
                });
            } else {
                // Reset all trackers if currently set.
                this.setState({
                    hour_difference: -1,
                    minute_difference: -1,
                    second_difference: -1
                });
            }
        }

        /**
         * Rendering and last minute calculations for client display.
         */

    }, {
        key: "render",
        value: function render() {
            var _this3 = this;

            var clock_in;
            var clock_out;
            var time_display;
            var submit_value;

            // Handle display differently if clocked in or clocked out.
            if (this.props.clock_out == null) {
                clock_in = new Date(this.props.clock_in);
                clock_out = new Date(this.props.clock_out);
                time_display = React.createElement(
                    "div",
                    { className: "time-display" },
                    React.createElement(
                        "p",
                        null,
                        "Clocked in: ",
                        clock_in.toLocaleDateString('en-US', this.props.date_string_options)
                    ),
                    React.createElement(
                        "p",
                        null,
                        "Shift Length: \xA0",
                        this.state.hour_difference.toString(),
                        " Hours \xA0",
                        this.state.minute_difference.toString(),
                        " Minutes \xA0",
                        this.state.second_difference.toString(),
                        " Seconds \xA0"
                    )
                );
                submit_value = "Clock Out";
            } else {
                time_display = React.createElement("div", { className: "time-display" });
                submit_value = "Clock In";
            }

            return React.createElement(
                "div",
                { className: "current-shift" },
                React.createElement(
                    "h2",
                    null,
                    "Current Shift"
                ),
                time_display,
                React.createElement("input", {
                    id: "shift-submit",
                    type: "button",
                    value: submit_value,
                    onClick: function onClick() {
                        return _this3.props.onClick();
                    }
                })
            );
        }
    }]);

    return CurrentShift;
}(React.Component);

exports.default = CurrentShift;

},{}],2:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/**
 * A single employee shift.
 */

var Shift = function (_React$Component) {
    _inherits(Shift, _React$Component);

    /**
     * Constructor for component.
     */
    function Shift(props) {
        _classCallCheck(this, Shift);

        return _possibleConstructorReturn(this, (Shift.__proto__ || Object.getPrototypeOf(Shift)).call(this, props));
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(Shift, [{
        key: 'render',
        value: function render() {
            var clock_in = new Date(this.props.clock_in);
            var clock_out = null;

            if (this.props.clock_out != null) {
                clock_out = new Date(this.props.clock_out);
            }

            return React.createElement(
                'tr',
                null,
                React.createElement(
                    'td',
                    null,
                    clock_in.toLocaleDateString('en-US', this.props.date_string_options)
                ),
                clock_out && // If statement. Only displays if clock_out is not null.
                React.createElement(
                    'td',
                    null,
                    clock_out.toLocaleDateString('en-US', this.props.date_string_options)
                )
            );
        }
    }]);

    return Shift;
}(React.Component);

exports.default = Shift;

},{}],3:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _current_shift = require('./current_shift');

var _current_shift2 = _interopRequireDefault(_current_shift);

var _employee_shift = require('./employee_shift');

var _employee_shift2 = _interopRequireDefault(_employee_shift);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Core of React rendering for my_hours page.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var EmployeeShiftManager = function (_React$Component) {
    _inherits(EmployeeShiftManager, _React$Component);

    /**
     * Constructor for component.
     */
    function EmployeeShiftManager(props) {
        _classCallCheck(this, EmployeeShiftManager);

        var _this = _possibleConstructorReturn(this, (EmployeeShiftManager.__proto__ || Object.getPrototypeOf(EmployeeShiftManager)).call(this, props));

        _this.state = {
            date_string_options: { month: "short", day: "2-digit", year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true },
            all_shifts: json_shifts,
            last_shift: json_shifts[0]
        };
        return _this;
    }

    /**
     * Logic to run on component load.
     */


    _createClass(EmployeeShiftManager, [{
        key: 'componentWillMount',
        value: function componentWillMount() {
            // If no shiffts are defined yet for this pay period, create a dummy "last shift" to prevent render errors.
            if (this.state.last_shift == null) {

                this.setState({
                    last_shift: {
                        pk: -1,
                        fields: {
                            "clock_in": new Date(),
                            "clock_out": new Date()
                        }
                    }
                });
            }
        }

        /**
         *Handle clock in/out button click.
         */

    }, {
        key: 'handleClick',
        value: function handleClick() {
            // Establish socket connection.
            var socket = new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/');

            socket.beforeunload = function () {
                socket.close();
            };

            // Handle incoming socket message event. Note the bind(this) to access React object state within function.
            socket.onmessage = function (message) {
                var data = JSON.parse(message.data);
                this.setState({ all_shifts: JSON.parse(data.json_shifts) });
                this.setState({ last_shift: this.state.all_shifts[0] });
            }.bind(this);

            // Send message to socket.
            socket.onopen = function (event) {
                socket.send(JSON.stringify({
                    'shift_submit': true
                }));
            };
        }

        /**
         * Handle message from socket.
         */

    }, {
        key: 'handleData',
        value: function handleData(data) {
            result = JSON.parse(data);
        }

        /**
         * Rendering and last minute calculations for client display.
         */

    }, {
        key: 'render',
        value: function render() {
            var _this2 = this;

            // Calculate list of shifts.
            var shifts = [];
            this.state.all_shifts.forEach(function (shift) {
                shifts.push(React.createElement(_employee_shift2.default, {
                    key: shift.pk,
                    clock_in: shift.fields['clock_in'],
                    clock_out: shift.fields['clock_out'],
                    date_string_options: _this2.state.date_string_options
                }));
            });

            // Elements to render for client.
            return React.createElement(
                'div',
                { className: 'center' },
                React.createElement(
                    'div',
                    null,
                    React.createElement(_current_shift2.default, {
                        key: this.state.last_shift.pk,
                        clock_in: this.state.last_shift.fields['clock_in'],
                        clock_out: this.state.last_shift.fields['clock_out'],
                        date_string_options: this.state.date_string_options,
                        onClick: function onClick() {
                            return _this2.handleClick();
                        }
                    })
                ),
                React.createElement('hr', null),
                React.createElement('hr', null),
                React.createElement(
                    'table',
                    null,
                    React.createElement(
                        'tbody',
                        null,
                        shifts
                    )
                )
            );
        }
    }]);

    return EmployeeShiftManager;
}(React.Component);

exports.default = EmployeeShiftManager;

},{"./current_shift":1,"./employee_shift":2}],4:[function(require,module,exports){
'use strict';

var _employee_shift_manager = require('./employee_shift_manager');

var _employee_shift_manager2 = _interopRequireDefault(_employee_shift_manager);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

// Start of React logic.
function App() {
    return React.createElement(_employee_shift_manager2.default, null);
}

// Render to page.
/**
 * React logic for my_hours page.
 */

ReactDOM.render(App(), document.getElementById('react-root'));

},{"./employee_shift_manager":3}]},{},[4]);
