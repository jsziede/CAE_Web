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
                { className: "panel current-shift" },
                React.createElement(
                    "div",
                    { className: "header center" },
                    React.createElement(
                        "h2",
                        null,
                        "Current Shift"
                    )
                ),
                React.createElement(
                    "div",
                    { className: "body" },
                    time_display,
                    React.createElement("input", {
                        id: "shift-submit",
                        type: "button",
                        value: submit_value,
                        onClick: function onClick() {
                            return _this2.props.onClick();
                        }
                    })
                )
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

var _current_shift = require('./current_shift');

var _current_shift2 = _interopRequireDefault(_current_shift);

var _pay_period_row = require('./pay_period_row');

var _pay_period_row2 = _interopRequireDefault(_pay_period_row);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * Core of React rendering for my_hours page.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var PayPeriod = function (_React$Component) {
    _inherits(PayPeriod, _React$Component);

    /**
     * Constructor for component.
     */
    function PayPeriod(props) {
        _classCallCheck(this, PayPeriod);

        // Static variables.
        var _this = _possibleConstructorReturn(this, (PayPeriod.__proto__ || Object.getPrototypeOf(PayPeriod)).call(this, props));

        _this.one_second = 1000;
        _this.one_minute = 60 * _this.one_second;
        _this.one_hour = 60 * _this.one_minute;
        return _this;
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(PayPeriod, [{
        key: 'render',
        value: function render() {
            var _this2 = this;

            // Calculate list of shifts.
            var shifts = [];
            if (this.props.shifts.length > 0) {
                this.props.shifts.forEach(function (shift) {
                    shifts.push(React.createElement(_pay_period_row2.default, {
                        key: shift.pk,
                        clock_in: shift.fields['clock_in'],
                        clock_out: shift.fields['clock_out'],
                        current_shift_hours: _this2.props.current_shift_hours,
                        current_shift_minutes: _this2.props.current_shift_minutes,
                        date_string_options: _this2.props.date_string_options
                    }));
                });
            } else {
                shifts.push(React.createElement(_pay_period_row2.default, {
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
                            { colSpan: '3' },
                            React.createElement(
                                'h3',
                                null,
                                this.props.table_title
                            )
                        )
                    ),
                    React.createElement(
                        'tr',
                        null,
                        React.createElement(
                            'th',
                            null,
                            React.createElement(
                                'h4',
                                null,
                                'Clock In'
                            )
                        ),
                        React.createElement(
                            'th',
                            null,
                            React.createElement(
                                'h4',
                                null,
                                'Clock Out'
                            )
                        ),
                        React.createElement(
                            'th',
                            null,
                            React.createElement(
                                'h4',
                                null,
                                'Shift Length'
                            )
                        )
                    )
                ),
                React.createElement(
                    'tbody',
                    null,
                    shifts
                ),
                React.createElement(
                    'tfoot',
                    null,
                    React.createElement(
                        'tr',
                        null,
                        React.createElement(
                            'th',
                            { colSpan: '3' },
                            React.createElement(
                                'h3',
                                null,
                                'Week Total: ',
                                week_hours,
                                ' Hours ',
                                week_minutes,
                                ' Minutes'
                            )
                        )
                    )
                )
            );
        }
    }]);

    return PayPeriod;
}(React.Component);

exports.default = PayPeriod;

},{"./current_shift":1,"./pay_period_row":3}],3:[function(require,module,exports){
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

var PayPeriodRow = function (_React$Component) {
    _inherits(PayPeriodRow, _React$Component);

    /**
     * Constructor for component.
     */
    function PayPeriodRow(props) {
        _classCallCheck(this, PayPeriodRow);

        // Static variables.
        var _this = _possibleConstructorReturn(this, (PayPeriodRow.__proto__ || Object.getPrototypeOf(PayPeriodRow)).call(this, props));

        _this.one_second = 1000;
        _this.one_minute = 60 * _this.one_second;
        _this.one_hour = 60 * _this.one_minute;
        return _this;
    }

    /**
     * Rendering and last minute calculations for client display.
     */


    _createClass(PayPeriodRow, [{
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
                    React.createElement(
                        'a',
                        { href: '' },
                        clock_in.toLocaleDateString('en-US', this.props.date_string_options)
                    )
                ) : React.createElement(
                    'td',
                    null,
                    React.createElement(
                        'a',
                        { href: '' },
                        'N/A'
                    )
                ),
                clock_out ? React.createElement(
                    'td',
                    null,
                    React.createElement(
                        'a',
                        { href: '' },
                        clock_out.toLocaleDateString('en-US', this.props.date_string_options)
                    )
                ) : React.createElement(
                    'td',
                    null,
                    React.createElement(
                        'a',
                        { href: '' },
                        'N/A'
                    )
                ),
                React.createElement(
                    'td',
                    null,
                    React.createElement(
                        'a',
                        { href: '' },
                        shift_time_display
                    )
                )
            );
        }
    }]);

    return PayPeriodRow;
}(React.Component);

exports.default = PayPeriodRow;

},{}],4:[function(require,module,exports){
'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _current_shift = require('./components/current_shift');

var _current_shift2 = _interopRequireDefault(_current_shift);

var _pay_period = require('./components/pay_period');

var _pay_period2 = _interopRequireDefault(_pay_period);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * React logic for my_hours page.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */

var ACTION_GET_EVENTS = 'get-events';
var ACTION_SEND_EVENTS = 'send-events';

var MyHoursManager = function (_React$Component) {
    _inherits(MyHoursManager, _React$Component);

    /**
     * Constructor for component.
     */
    function MyHoursManager(props) {
        _classCallCheck(this, MyHoursManager);

        var _this = _possibleConstructorReturn(this, (MyHoursManager.__proto__ || Object.getPrototypeOf(MyHoursManager)).call(this, props));

        _this.state = {
            // Socket management variables.
            socket: new WebSocket('ws://' + domain + '/ws/caeweb/employee/my_hours/'),
            awaiting_socket_data: true,

            // Date management variables.
            current_time: new Date(),
            date_string_options: { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true },

            // Passed socket variables.
            current_pay_period: null,
            displayed_pay_period: null,
            shifts: null,
            last_shift: null,

            // Calculated variables.
            week_1_shifts: [],
            week_2_shifts: [],
            week_1_hours: 0,
            week_2_hours: 0,
            current_shift_hours: 0,
            current_shift_minutes: 0,
            current_shift_seconds: 0
        };

        // Static variables.
        _this.one_second = 1000;
        _this.one_minute = 60 * _this.one_second;
        _this.one_hour = 60 * _this.one_minute;
        return _this;
    }

    /**
     * Logic for component initializing.
     * Runs before component load in.
     */


    _createClass(MyHoursManager, [{
        key: 'componentWillMount',
        value: function componentWillMount() {
            // Set base socket event handler functions.
            var socket = this.state.socket;

            /**
             * Socket start.
             */
            this.state.socket.onopen = function (event) {
                // console.log('Socket opened.');

                // Send message to socket.
                this.state.socket.send(JSON.stringify({
                    'action': ACTION_GET_EVENTS,
                    'notify': true
                }));

                // console.log('Initialization data sent.');
            }.bind(this);

            /**
             * Get socket message.
             */
            this.state.socket.onmessage = function (event) {
                // console.log('Recieved socket message.');
                var data = JSON.parse(event.data);

                // Save values from data as state.
                if (this.state.current_pay_period == null) {
                    this.setState({
                        current_pay_period: JSON.parse(data['pay_period'])[0]
                    });
                }

                this.setState({
                    displayed_pay_period: JSON.parse(data['pay_period'])[0],
                    shifts: JSON.parse(data['shifts']),
                    last_shift: JSON.parse(data['last_shift'])[0]
                });

                if (this.state.awaiting_socket_data == false) {
                    this.calculatePayPeriodWeeks();
                }
            }.bind(this);

            /**
             * Socket error.
             */
            this.state.socket.onerror = function (event) {}
            // console.log('An error occured.');
            // console.log(event);


            /**
             * Socket terminated.
             */
            ;this.state.socket.onclose = function (event) {
                // console.log('Socket closed.');
                // console.log(event);
            };
        }

        /**
         * Logic for component post-initialization.
         * Runs after component load in.
         */

    }, {
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this2 = this;

            // Ensure that the page processes a tick immediately on load.
            this.loadTimerTick();

            // Set component to run an update tick every second.
            this.intervalId = setInterval(function () {
                return _this2.loadTimerTick();
            }, 1000);
        }

        /**
         * Logic for component deconstruction.
         * Runs just before component destruction.
         */

    }, {
        key: 'componentWillUnmount',
        value: function componentWillUnmount() {
            clearInterval(this.intervalId);
        }

        /**
         * Tick to check for data from socket on page load.
         */

    }, {
        key: 'loadTimerTick',
        value: function loadTimerTick() {
            var _this3 = this;

            // Tick and do nothing until state data is populated.
            if (this.state.current_pay_period != null && this.state.shifts != null) {
                // Clear tick timer.
                clearInterval(this.intervalId);

                // Process recieved data.
                this.processSocketData();

                this.setState({
                    awaiting_socket_data: false
                });

                this.calculatePayPeriodWeeks();

                // Set new tick timer for app run.
                this.intervalId = setInterval(function () {
                    return _this3.runAppTick();
                }, 1000);
            }
        }

        /**
         * Tick to manage and run app.
         */

    }, {
        key: 'runAppTick',
        value: function runAppTick() {
            // Update current time.
            this.setState({
                current_time: new Date()
            });

            // Recalculate hours worked.
            this.processSocketData();
        }

        /**
         * Calculate values based on passed data.
         */

    }, {
        key: 'processSocketData',
        value: function processSocketData() {
            if (this.state.last_shift.length == 0) {
                // No shifts exist for user in pay period. Create dummy shift.
                var current_time = this.state.current_time;
                this.setState({
                    last_shift: {
                        pk: -1,
                        fields: {
                            'clock_in': current_time,
                            'clock_out': current_time
                        }
                    }
                });
            }

            this.calculateCurrentShift();
            this.calculateTotalHoursWorked();
        }

        /**
         * Sorts shifts based on week in pay period.
         */

    }, {
        key: 'calculatePayPeriodWeeks',
        value: function calculatePayPeriodWeeks() {

            var week_1_shifts = [];
            var week_2_shifts = [];

            // Calculate end of first week.
            var week_1_end = new Date(this.state.displayed_pay_period.fields['period_start']);
            week_1_end = week_1_end.setDate(week_1_end.getDate() + 7);

            // Loop through all shifts. Determine which week they belong to.
            this.state.shifts.forEach(function (shift) {
                if (new Date(shift.fields['clock_in']).getTime() < week_1_end) {
                    week_1_shifts.push(shift);
                } else {
                    week_2_shifts.push(shift);
                }
            });

            // Save weeks as state.
            this.setState({
                week_1_shifts: week_1_shifts,
                week_2_shifts: week_2_shifts
            });

            this.calculateCurrentShift();
            this.calculateTotalHoursWorked();
        }

        /**
         * Calculates total hours worked, by week.
         */

    }, {
        key: 'calculateTotalHoursWorked',
        value: function calculateTotalHoursWorked() {
            var _this4 = this;

            var shift_start;
            var shift_end;
            var total_time = 0;

            // Calculate for week 1.
            this.state.week_1_shifts.forEach(function (shift) {
                shift_start = new Date(shift.fields['clock_in']).getTime();

                // If clockout is null, use current time as calculation.
                if (shift.fields['clock_out'] != null) {
                    shift_end = new Date(shift.fields['clock_out']).getTime();
                } else {
                    shift_end = new Date(_this4.state.current_time);
                }

                total_time += shift_end - shift_start;
            });

            this.setState({ week_1_hours: total_time });

            // Calculate for week 2.
            total_time = 0;
            this.state.week_2_shifts.forEach(function (shift) {
                shift_start = new Date(shift.fields['clock_in']).getTime();

                // If clockout is null, use current time as calculation.
                if (shift.fields['clock_out'] != null) {
                    shift_end = new Date(shift.fields['clock_out']).getTime();
                } else {
                    shift_end = new Date(_this4.state.current_time);
                }

                total_time += shift_end - shift_start;
            });

            this.setState({ week_2_hours: total_time });
        }

        /**
         * Calculates total hours in current shift.
         */

    }, {
        key: 'calculateCurrentShift',
        value: function calculateCurrentShift() {
            // Check if currently clocked in.
            if (this.state.last_shift.fields['clock_out'] == null) {

                // Clocked in. Calculate current_shift time trackers.
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
                // Not clocked in. Reset all current_shift trackers if currently set.
                this.setState({
                    current_shift_hours: 0,
                    current_shift_minutes: 0,
                    current_shift_seconds: 0
                });
            }
        }

        /**
         * Grab pay period of provided pk.
         */

    }, {
        key: 'getNewPayPeriod',
        value: function getNewPayPeriod(pay_period_index) {
            // Send message to socket.
            this.state.socket.send(JSON.stringify({
                'action': ACTION_SEND_EVENTS,
                'pay_period_pk': pay_period_index,
                'notify': true
            }));
        }

        /**
         * Gets and displays previous period.
         * Note that this intentionally blocks until response is received.
         */

    }, {
        key: 'handlePrevPeriodClick',
        value: function handlePrevPeriodClick() {
            this.getNewPayPeriod(this.state.displayed_pay_period.pk - 1);
        }

        /**
         * Gets and displays current pay period.
         */

    }, {
        key: 'handleCurrPeriodClick',
        value: function handleCurrPeriodClick() {
            this.getNewPayPeriod(this.state.current_pay_period.pk);
        }

        /**
         * Gets and displays next pay period.
         */

    }, {
        key: 'handleNextPeriodClick',
        value: function handleNextPeriodClick() {
            this.getNewPayPeriod(this.state.displayed_pay_period.pk + 1);
        }

        /**
         *Handle clock in/out button click.
         */

    }, {
        key: 'handleShiftClick',
        value: function handleShiftClick() {
            // Send message to socket.
            this.state.socket.send(JSON.stringify({
                'action': ACTION_SEND_EVENTS,
                'submit_shift': true,
                'notify': true
            }));
        }

        /**
         * Rendering and last minute calculations for client display.
         */

    }, {
        key: 'render',
        value: function render() {
            var _this5 = this;

            // Elements to render for client.
            if (this.state.awaiting_socket_data) {
                return React.createElement(
                    'h2',
                    null,
                    'Loading, please wait...'
                );
            } else {
                var pay_period_start_display = new Date(this.state.displayed_pay_period.fields['period_start']);
                var pay_period_end_display = new Date(this.state.displayed_pay_period.fields['period_end']);
                var pay_period_string_options = { month: 'short', day: '2-digit', year: 'numeric' };

                var total_time = this.state.week_1_hours + this.state.week_2_hours;
                var total_hours = Math.trunc(total_time / this.one_hour);
                var total_minutes = Math.trunc((total_time - total_hours * this.one_hour) / this.one_minute);

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
                            return _this5.handleShiftClick();
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
                                    return _this5.handlePrevPeriodClick();
                                }
                            }),
                            React.createElement('input', {
                                id: 'curr_pay_period_button',
                                type: 'button',
                                value: 'Current Pay Period',
                                onClick: function onClick() {
                                    return _this5.handleCurrPeriodClick();
                                }
                            }),
                            React.createElement('input', {
                                id: 'next_pay_period_button', type: 'button',
                                value: '\u23F5',
                                onClick: function onClick() {
                                    return _this5.handleNextPeriodClick();
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
        }
    }]);

    return MyHoursManager;
}(React.Component);

// Start of React logic.


function App() {
    return React.createElement(MyHoursManager, null);
}

// Render to page.
ReactDOM.render(App(), document.getElementById('react-root'));

},{"./components/current_shift":1,"./components/pay_period":2}]},{},[4]);
