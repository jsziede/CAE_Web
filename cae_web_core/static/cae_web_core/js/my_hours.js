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

        return _possibleConstructorReturn(this, (CurrentShift.__proto__ || Object.getPrototypeOf(CurrentShift)).call(this, props));
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(CurrentShift, [{
        key: "render",
        value: function render() {
            var _this2 = this;

            var clock_in;
            var time_display;
            var submit_value;

            // Handle display differently if clocked in or clocked out.
            if (this.props.clock_out == null) {
                clock_in = new Date(this.props.clock_in);
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
                        this.props.shift_hours.toString(),
                        " Hours \xA0",
                        this.props.shift_minutes.toString(),
                        " Minutes \xA0",
                        this.props.shift_seconds.toString(),
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
                        return _this2.props.onClick();
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

        // Static variables.
        var _this = _possibleConstructorReturn(this, (Shift.__proto__ || Object.getPrototypeOf(Shift)).call(this, props));

        _this.one_second = 1000;
        _this.one_minute = 60 * _this.one_second;
        _this.one_hour = 60 * _this.one_minute;
        return _this;
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(Shift, [{
        key: 'render',
        value: function render() {
            var clock_in = null;
            var clock_out = null;
            var shift_total = 0;
            var shift_hours;
            var shift_minutes;
            var shift_time_display;

            // Check if valid clock in time. If none, is dummy shift.
            if (this.props.clock_in != null) {
                clock_in = new Date(this.props.clock_in);

                // Check for valid clock out time. If none, use passed prop paremeters.
                if (this.props.clock_out != null) {
                    clock_out = new Date(this.props.clock_out);
                    shift_total = clock_out.getTime() - clock_in.getTime();
                    shift_hours = Math.trunc(shift_total / this.one_hour);
                    shift_minutes = Math.trunc((shift_total - shift_hours * this.one_hour) / this.one_minute);
                } else {
                    shift_hours = this.props.current_shift_hours;
                    shift_minutes = this.props.current_shift_minutes;
                }
                shift_time_display = shift_hours + ' Hours ' + shift_minutes + ' Minutes';
            } else {
                shift_time_display = 'N/A';
            }

            return React.createElement(
                'tr',
                null,
                clock_in ? React.createElement(
                    'td',
                    null,
                    clock_in.toLocaleDateString('en-US', this.props.date_string_options)
                ) : React.createElement(
                    'td',
                    null,
                    'N/A'
                ),
                clock_out ? React.createElement(
                    'td',
                    null,
                    clock_out.toLocaleDateString('en-US', this.props.date_string_options)
                ) : React.createElement(
                    'td',
                    null,
                    'N/A'
                ),
                React.createElement(
                    'td',
                    null,
                    shift_time_display
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

var _pay_period = require('./pay_period');

var _pay_period2 = _interopRequireDefault(_pay_period);

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
            current_time: new Date(),
            date_string_options: { month: "short", day: "2-digit", hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true },

            current_pay_period: json_pay_period[0],
            displayed_pay_period: json_pay_period[0],

            shifts: json_shifts,
            week_1_shifts: [],
            week_2_shifts: [],
            week_1_hours: 0,
            week_2_hours: 0,
            last_shift: json_last_shift[0],

            current_shift_hours: -1,
            current_shift_minutes: -1,
            current_shift_seconds: -1
        };

        // Static variables.
        _this.one_second = 1000;
        _this.one_minute = 60 * _this.one_second;
        _this.one_hour = 60 * _this.one_minute;
        return _this;
    }

    /**
     * Logic to run before component load.
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

            this.calculateWeeksInPayPeriod();
        }

        /**
         * Logic to run on component load.
         */

    }, {
        key: 'componentDidMount',
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
        key: 'componentWillUnmount',
        value: function componentWillUnmount() {
            clearInterval(this.intervalId);
        }

        /**
         * Functions to run on each tick.
         */

    }, {
        key: 'tick',
        value: function tick() {
            this.setState({
                current_time: new Date()
            });

            // Check if currently clocked in.
            if (this.state.last_shift.fields['clock_out'] == null) {

                // Calculate shift time trackers.
                var shift_total = this.state.current_time - new Date(this.state.last_shift.fields['clock_in']);
                var shift_hours = Math.trunc(shift_total / this.one_hour);
                var shift_minutes = Math.trunc((shift_total - shift_hours * this.one_hour) / this.one_minute);
                var shift_seconds = Math.trunc((shift_total - shift_hours * this.one_hour - shift_minutes * this.one_minute) / this.one_second);

                // Update shift time trackers.
                this.setState({
                    current_shift_hours: shift_hours,
                    current_shift_minutes: shift_minutes,
                    current_shift_seconds: shift_seconds
                });
            } else {
                // Reset all trackers if currently set.
                this.setState({
                    current_shift_hours: -1,
                    current_shift_minutes: -1,
                    current_shift_seconds: -1
                });
            }

            this.calculateHoursWorked();
        }

        /**
         *Handle clock in/out button click.
         */

    }, {
        key: 'handleShiftClick',
        value: function handleShiftClick() {
            // Establish socket connection.
            var socket = new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/');

            socket.beforeunload = function () {
                socket.close();
            };

            // Handle incoming socket message event. Note the bind(this) to access React object state within function.
            socket.onmessage = function (message) {
                var data = JSON.parse(message.data);
                this.setState({
                    shifts: JSON.parse(data.json_shifts),
                    ast_shift: JSON.parse(data.json_last_shift)[0],
                    displayed_pay_period: this.state.current_pay_period
                });
            }.bind(this);

            // Send message to socket.
            socket.onopen = function (event) {
                socket.send(JSON.stringify({
                    'shift_submit': true
                }));
            };
        }
    }, {
        key: 'handlePrevPeriodClick',
        value: function handlePrevPeriodClick() {
            this.getNewPayPeriod(this.state.displayed_pay_period.pk - 1);
        }
    }, {
        key: 'handleCurrPeriodClick',
        value: function handleCurrPeriodClick() {
            this.getNewPayPeriod(this.state.current_pay_period.pk);
        }
    }, {
        key: 'handleNextPeriodClick',
        value: function handleNextPeriodClick() {
            this.getNewPayPeriod(this.state.displayed_pay_period.pk + 1);
        }

        /**
         * Grab pay period of provided pk.
         */

    }, {
        key: 'getNewPayPeriod',
        value: function getNewPayPeriod(pay_period_index) {
            // Establish socket connection.
            var socket = new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/');

            socket.beforeunload = function () {
                socket.close();
            };

            // Handle incoming socket message event. Note the bind(this) to access React object state within function.
            socket.onmessage = function (message) {
                var data = JSON.parse(message.data);
                this.setState({
                    displayed_pay_period: JSON.parse(data.json_pay_period)[0],
                    shifts: JSON.parse(data.json_shifts)
                });
                this.calculateWeeksInPayPeriod();
            }.bind(this);

            // Send message to socket.
            socket.onopen = function (event) {
                socket.send(JSON.stringify({
                    'pay_period': pay_period_index
                }));
            };
        }

        /**
         * Sorts shifts based on week in pay period.
         */

    }, {
        key: 'calculateWeeksInPayPeriod',
        value: function calculateWeeksInPayPeriod() {

            var week_1_shifts = [];
            var week_2_shifts = [];
            var week_1_end = new Date(this.state.displayed_pay_period.fields['period_start']);

            week_1_end = week_1_end.setDate(week_1_end.getDate() + 7);

            this.state.shifts.forEach(function (shift) {
                if (new Date(shift.fields['clock_in']).getTime() < week_1_end) {
                    week_1_shifts.push(shift);
                } else {
                    week_2_shifts.push(shift);
                }
            });

            this.setState({
                week_1_shifts: week_1_shifts,
                week_2_shifts: week_2_shifts
            });

            this.calculateHoursWorked();
        }

        /**
         * Calculates total hours worked, by week.
         */

    }, {
        key: 'calculateHoursWorked',
        value: function calculateHoursWorked() {
            var _this3 = this;

            var shift_start;
            var shift_end;
            var total_time = 0;

            // Calculate for week 1.
            this.state.week_1_shifts.forEach(function (shift) {
                console.log(total_time);
                shift_start = new Date(shift.fields['clock_in']).getTime();
                if (shift.fields['clock_out'] != null) {
                    shift_end = new Date(shift.fields['clock_out']).getTime();
                } else {
                    shift_end = new Date(_this3.state.current_time);
                }
                total_time += shift_end - shift_start;
            });
            this.setState({ week_1_hours: total_time });
            total_time = 0;

            // Calculate for week 2.
            this.state.week_2_shifts.forEach(function (shift) {
                console.log(total_time);
                shift_start = new Date(shift.fields['clock_in']).getTime();
                if (shift.fields['clock_out'] != null) {
                    shift_end = new Date(shift.fields['clock_out']).getTime();
                } else {
                    shift_end = new Date(_this3.state.current_time);
                }
                total_time += shift_end - shift_start;
            });
            this.setState({ week_2_hours: total_time });
        }

        /**
         * Rendering and last minute calculations for client display.
         */

    }, {
        key: 'render',
        value: function render() {
            var _this4 = this;

            var pay_period_start_display = new Date(this.state.displayed_pay_period.fields['period_start']);
            var pay_period_end_display = new Date(this.state.displayed_pay_period.fields['period_end']);
            var pay_period_string_options = { month: "short", day: "2-digit", year: 'numeric' };

            var total_time = this.state.week_1_hours + this.state.week_2_hours;
            var total_hours = Math.trunc(total_time / this.one_hour);
            var total_minutes = Math.trunc((total_time - total_hours * this.one_hour) / this.one_minute);

            // Elements to render for client.
            return React.createElement(
                'div',
                { className: 'center' },
                React.createElement(_current_shift2.default, {
                    clock_in: this.state.last_shift.fields['clock_in'],
                    clock_out: this.state.last_shift.fields['clock_out'],
                    shift_hours: this.state.current_shift_hours,
                    shift_minutes: this.state.current_shift_minutes,
                    shift_seconds: this.state.current_shift_seconds,
                    date_string_options: this.state.date_string_options,
                    onClick: function onClick() {
                        return _this4.handleShiftClick();
                    }
                }),
                React.createElement(
                    'div',
                    { className: 'pay-period center' },
                    React.createElement(
                        'h2',
                        null,
                        'Pay Period of\xA0',
                        pay_period_start_display.toLocaleDateString('en-US', pay_period_string_options),
                        '\xA0Through\xA0',
                        pay_period_end_display.toLocaleDateString('en-US', pay_period_string_options)
                    ),
                    React.createElement(
                        'div',
                        null,
                        React.createElement('input', {
                            id: 'prev_pay_period_button',
                            type: 'button',
                            value: '\u23F4',
                            onClick: function onClick() {
                                return _this4.handlePrevPeriodClick();
                            }
                        }),
                        React.createElement('input', {
                            id: 'curr_pay_period_button',
                            type: 'button',
                            value: 'Current Pay Period',
                            onClick: function onClick() {
                                return _this4.handleCurrPeriodClick();
                            }
                        }),
                        React.createElement('input', {
                            id: 'next_pay_period_button', type: 'button',
                            value: '\u23F5',
                            onClick: function onClick() {
                                return _this4.handleNextPeriodClick();
                            }
                        })
                    ),
                    React.createElement(
                        'p',
                        null,
                        'Total Pay Period Hours: ',
                        total_hours,
                        ' Hours ',
                        total_minutes,
                        ' Minutes'
                    ),
                    React.createElement(_pay_period2.default, {
                        table_title: 'Week 1',
                        displayed_pay_period: this.state.displayed_pay_period,
                        shifts: this.state.week_1_shifts,
                        current_shift_hours: this.state.current_shift_hours,
                        current_shift_minutes: this.state.current_shift_minutes,
                        week_total: this.state.week_1_hours,
                        date_string_options: this.state.date_string_options
                    }),
                    React.createElement(_pay_period2.default, {
                        table_title: 'Week 2',
                        displayed_pay_period: this.state.displayed_pay_period,
                        shifts: this.state.week_2_shifts,
                        current_shift_hours: this.state.current_shift_hours,
                        current_shift_minutes: this.state.current_shift_minutes,
                        week_total: this.state.week_2_hours,
                        date_string_options: this.state.date_string_options
                    })
                )
            );
        }
    }]);

    return EmployeeShiftManager;
}(React.Component);

exports.default = EmployeeShiftManager;

},{"./current_shift":1,"./employee_shift":2,"./pay_period":5}],4:[function(require,module,exports){
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

},{"./employee_shift_manager":3}],5:[function(require,module,exports){
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

        // Static variables.
        var _this = _possibleConstructorReturn(this, (EmployeeShiftManager.__proto__ || Object.getPrototypeOf(EmployeeShiftManager)).call(this, props));

        _this.one_second = 1000;
        _this.one_minute = 60 * _this.one_second;
        _this.one_hour = 60 * _this.one_minute;
        return _this;
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(EmployeeShiftManager, [{
        key: 'render',
        value: function render() {
            var _this2 = this;

            // Calculate list of shifts.
            var shifts = [];
            if (this.props.shifts.length > 0) {
                this.props.shifts.forEach(function (shift) {
                    shifts.push(React.createElement(_employee_shift2.default, {
                        key: shift.pk,
                        clock_in: shift.fields['clock_in'],
                        clock_out: shift.fields['clock_out'],
                        current_shift_hours: _this2.props.current_shift_hours,
                        current_shift_minutes: _this2.props.current_shift_minutes,
                        date_string_options: _this2.props.date_string_options
                    }));
                });
            } else {
                shifts.push(React.createElement(_employee_shift2.default, {
                    key: 'N/A',
                    clock_in: null,
                    clock_out: null,
                    date_string_options: this.props.date_string_options
                }));
            }

            // Date to string display.
            var pay_period_display = new Date(this.props.displayed_pay_period.fields['period_start']);
            var pay_period_string_options = { month: "short", day: "2-digit", year: 'numeric' };

            // Calculate week hours.
            var week_hours = Math.trunc(this.props.week_total / this.one_hour);
            var week_minutes = Math.trunc((this.props.week_total - week_hours * this.one_hour) / this.one_minute);

            return React.createElement(
                'table',
                null,
                React.createElement(
                    'thead',
                    null,
                    React.createElement(
                        'tr',
                        null,
                        React.createElement(
                            'th',
                            { colspan: '3' },
                            this.props.table_title
                        )
                    ),
                    React.createElement(
                        'tr',
                        null,
                        React.createElement(
                            'th',
                            null,
                            'Clock In'
                        ),
                        React.createElement(
                            'th',
                            null,
                            'Clock Out'
                        ),
                        React.createElement(
                            'th',
                            null,
                            'Shift Length'
                        )
                    )
                ),
                React.createElement(
                    'tbody',
                    null,
                    shifts,
                    React.createElement(
                        'tr',
                        null,
                        React.createElement(
                            'td',
                            { colspan: '3' },
                            'Week Total: ',
                            week_hours,
                            ' Hours ',
                            week_minutes,
                            ' Minutes'
                        )
                    )
                )
            );
        }
    }]);

    return EmployeeShiftManager;
}(React.Component);

exports.default = EmployeeShiftManager;

},{"./current_shift":1,"./employee_shift":2}]},{},[4]);
