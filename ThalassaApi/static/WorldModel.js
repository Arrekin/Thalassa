var WorldModel = function () {
    this.islands = null;

    this.initialize();
};

WorldModel.prototype = {

    initialize: function () {
        $.get("world/data", function (data, status) {
            alert("Data: " + data + "\nStatus: " + status);
            var obj = JSON.parse(data)
            alert(JSON.stringify(obj.islands, null, 4))
        });
    },
};