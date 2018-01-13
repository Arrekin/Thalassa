var WorldModel = function (thalassa) {
    this.thalssa = thalassa;

    this.islands = null;

    // Events handlers
    this.islandsDataChangedEvent = new ThalassaEvent(this);

    this.initialize();
};

WorldModel.prototype = {

    initialize: function () {
        // Get basic world data
        //$.get("world/data", (raw_data, status) => {
        $.ajax({
            type: "get", url: "world/data",
            success: (raw_data, status) => {
                let data = JSON.parse(raw_data)

                // Load islands data
                this.islands = {}
                for (let i = 0; i < data.islands.length; ++i) {
                    let current_island = data.islands[i];
                    this.islands[current_island.id] = current_island;
                }
                //alert(JSON.stringify(this.islands, null, 4))
                this.islandsDataChangedEvent.notify();
            },
            error: (request, status, error) => {
                if (request.status == 401) {
                    window.location.href = '/login';
                    return;
                }
                else {
                    alert("R: " + request.status + "\nS: " + status + "\nE: " + error);
                }
            }
        });
    },
};