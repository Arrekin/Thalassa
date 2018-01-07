var WorldModel = function () {
    this.island = null;

    // Events handlers
    this.islandsDataChangedEvent = new ThalassaEvent(this);

    this.initialize();
};

WorldModel.prototype = {

    initialize: function () {
        // Get basic world data
        $.get("world/data", (raw_data, status) => {
            //alert("Data: " + data + "\nStatus: " + status);
            let data = JSON.parse(raw_data)

            // Load islands data
            this.island = {}
            for (let i = 0; i < data.islands.length; ++i) {
                let current_island = data.islands[i];
                this.island[current_island.id] = current_island;
            }
            alert(JSON.stringify(this.island, null, 4))
            this.islandsDataChangedEvent.notify();

        });
    },
};