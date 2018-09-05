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

    function CurrentShift() {
        _classCallCheck(this, CurrentShift);

        return _possibleConstructorReturn(this, (CurrentShift.__proto__ || Object.getPrototypeOf(CurrentShift)).apply(this, arguments));
    }

    _createClass(CurrentShift, [{
        key: "render",


        /**
         * Rendering and last minute calculations for client display.
         */
        value: function render() {
            var _this2 = this;

            return React.createElement(
                "div",
                null,
                React.createElement(
                    "div",
                    null,
                    React.createElement(
                        "p",
                        null,
                        this.props.clock_in
                    ),
                    React.createElement(
                        "p",
                        null,
                        this.props.clock_out
                    )
                ),
                React.createElement("input", {
                    id: "shift-submit",
                    type: "button",
                    value: "Clock In/Out",
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
"use strict";

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
        key: "render",
        value: function render() {
            return React.createElement(
                "tr",
                null,
                React.createElement(
                    "td",
                    null,
                    this.props.clock_in
                ),
                React.createElement(
                    "td",
                    null,
                    this.props.clock_out
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
            shifts: json_shifts,
            last_shift: json_shifts[0]
        };
        return _this;
    }

    /**
     *Handle clock in/out button click.
     */


    _createClass(EmployeeShiftManager, [{
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
                this.setState({ shifts: JSON.parse(data.json_shifts) });
                this.setState({ last_shift: this.state.shifts[0] });
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
            this.state.shifts.forEach(function (shift) {
                shifts.push(React.createElement(_employee_shift2.default, {
                    key: shift.pk,
                    clock_in: shift.fields['clock_in'],
                    clock_out: shift.fields['clock_out']
                }));
            });

            // Elements to render for client.
            return React.createElement(
                'div',
                null,
                React.createElement(
                    'div',
                    null,
                    React.createElement(_current_shift2.default, {
                        key: this.state.last_shift.pk,
                        clock_in: this.state.last_shift.fields['clock_in'],
                        clock_out: this.state.last_shift.fields['clock_out'],
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
