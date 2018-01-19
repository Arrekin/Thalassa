var WorldModel = function (thalassa) {
    this.thalssa = thalassa;

    this.islands = null;
    this.fleets = null;

    // Events handlers
    this.islandsDataChangedEvent = new ThalassaEvent(this);
    this.fleetsDataChangedEvent = new ThalassaEvent(this);

    this.initialize();
};

WorldModel.prototype = {

    initialize: function () {
        // Get basic world data
        $.ajax({
            type: "get", url: "world/data",
            success: (raw_data, status) => {
                let data = JSON.parse(raw_data)

                // Load islands data
                this.islands = {}
                for (let i = 0; i < data.islands.length; ++i) {
                    let current_island = data.islands[i];
                    current_island.id = String(current_island.id)
                    this.islands[current_island.id] = current_island;
                }
                // Load fleets data
                this.fleets = {}
                for (let i = 0; i < data.fleets.length; ++i) {
                    let current_fleet = data.fleets[i];
                    current_fleet.id = String(current_fleet.id)
                    this.fleets[current_fleet.id] = current_fleet;
                }
                //alert(JSON.stringify(this.fleets, null, 4)+ (Date.now()/1000))
                this.islandsDataChangedEvent.notify();
                this.fleetsDataChangedEvent.notify();
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