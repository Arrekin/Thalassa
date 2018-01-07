var ThalassaEvent = function (sender) {
    this._sender = sender;
    this._listeners = [];
}

ThalassaEvent.prototype = {

    attach: function (listener) {
        this._listeners.push(listener);
    },

    notify: function (args) {
        for (var i = 0; i < this._listeners.length; i += 1) {
            this._listeners[i](this._sender, args);
        }
    }

};