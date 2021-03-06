var WorldIslandView = function (id, worldView) {
	this.id = id;
	this.worldView = worldView;

	// Model data
	this.name = null;
	this.x = null;
	this.y = null;

	// View data
    this.sprite = null;
    this.resourcesText = null;
}

WorldIslandView.prototype = {

	UpdateData: function () {
		let model = this.worldView.GetWorldModel();
		islandModel = model.islands[this.id];
		this.name = islandModel.name;
		this.x = islandModel.x;
        this.y = islandModel.y;

        if (this.resourcesText) {
            this.resourcesText.setText(`Wood: ${islandModel.wood}\nWheat: ${islandModel.wheat}\nWine: ${islandModel.wine}`);
        }

		this.Render();
	},

	Render: function () {
		if (this.sprite == null) {
		    this._CreateSprite();
		}

		this.sprite.x = this.x;
		this.sprite.y = this.y;
	},

	_CreateSprite: function () {
	    let thalassa = this.worldView.thalassa;
	    this.sprite = new Sprite(thalassa.resources["static/images/island_icon.png"].texture);
	    this.sprite.scale.x = 0.1;
        this.sprite.scale.y = 0.1;
        this.sprite.anchor.set(0.5);
        this.sprite.interactive = true;
        //this.sprite.hitArea = new PIXI.Circle(this.sprite.x, this.sprite.y, 30);
        this.sprite.mouseover = this._OnMouseEnter.bind(this);
        this.sprite.mouseout = this._OnMouseExit.bind(this);
        this.worldView.RegisterSprite(this.sprite);

        // Resources text setup
        this.resourcesText = new PIXI.Text("Wood: ## \nWheat: ##\nWine: ##");
        this.resourcesText.x = 0;
        this.resourcesText.y = 0;
        this.resourcesText.visible = false;
        this.worldView.RegisterSprite(this.resourcesText);
    },

    _OnMouseEnter: function () {
        this.resourcesText.visible = true;
    },

    _OnMouseExit: function () {
        this.resourcesText.visible = false;
    },
}

var WorldFleetView = function (id, worldView) {
    this.id = id;
    this.worldView = worldView;

    // Model data
    this.owner = null;
    this.verticalSpeed = null;
    this.horizontalSpeed = null;
    this.modelX = null;
    this.modelY = null;
    this.timestamp = null;

    // View data
    this.x = null;
    this.y = null;
    this.sprite = null;
}

WorldFleetView.prototype = {

    UpdateData: function () {
        let model = this.worldView.GetWorldModel();
        fleetModel = model.fleets[this.id];
        this.owner = fleetModel.owner;
        this.horizontalSpeed = fleetModel.horizontal_speed;
        this.verticalSpeed = fleetModel.vertical_speed;
        this.modelX = fleetModel.x;
        this.modelY = fleetModel.y;
        this.timestamp = fleetModel.timestamp;
        this.Render();
    },

    Render: function () {
        if (this.sprite == null) {
            this._CreateSprite();
        }

        let timeElapsed = this.worldView.thalassa.timestamp - this.timestamp;
        this.sprite.x = this.modelX + timeElapsed * this.horizontalSpeed;
        this.sprite.y = this.modelY + timeElapsed * this.verticalSpeed;
        this.sprite.rotation = Math.atan2(this.verticalSpeed, this.horizontalSpeed);
    },

    _CreateSprite: function () {
        this.sprite = new PIXI.Graphics();
        this.sprite.beginFill(0xFFFFFF);
        this.sprite.drawRect(0, 0, 32, 8);
        this.sprite.endFill();
        this.sprite.pivot.set(16, 4);
        this.worldView.RegisterSprite(this.sprite);
    }
}

var WorldView = function (thalassaApp) {

	this.thalassa = thalassaApp;

	this.islands = {};
	this.fleets = {};

	this.islandsDataChangedHandler = this.OnIslandsDataChanged.bind(this);
	this.GetWorldModel().islandsDataChangedEvent.attach(this.islandsDataChangedHandler);

	this.fleetsDataChangedHandler = this.OnFleetsDataChanged.bind(this);
	this.GetWorldModel().fleetsDataChangedEvent.attach(this.fleetsDataChangedHandler);
}

WorldView.prototype = {

	GetWorldModel: function () {
		return this.thalassa.worldModel;
	},

	OnIslandsDataChanged: function () {
		let islandsModels = this.GetWorldModel().islands;
		for (var islandId in islandsModels) {
			if (islandsModels.hasOwnProperty(islandId)) {
				if (!this.islands.hasOwnProperty(islandId)) {
					// This island does not exist in the view. Add it.
                    this.islands[islandId] = new WorldIslandView(islandId, this);
				}
				// Let the island view update itself
				this.islands[islandId].UpdateData();
			}
		}
	},

    OnFleetsDataChanged: function () {
        /////// !!!!!!!!! REWORK THIS
        for (var fleetId in this.fleets) {
            this.thalassa.stage.removeChild(this.fleets[fleetId].sprite)
            delete this.fleets[fleetId]
        }
	    let fleetsModels = this.GetWorldModel().fleets;
	    for (var fleetId in fleetsModels) {
	        if (fleetsModels.hasOwnProperty(fleetId)) {
	            if (!this.fleets.hasOwnProperty(fleetId)) {
	                // This fleet does not exist in the view. Add it.
	                this.fleets[fleetId] = new WorldFleetView(fleetId, this);
	            }
	            // Let the island view update itself
                this.fleets[fleetId].UpdateData();
	        }
	    }
	},

	RegisterSprite: function (sprite) {
	    this.thalassa.stage.addChild(sprite);
	},

	Update: function () {
	    for (var fleetId in this.fleets) {
	        if (this.fleets.hasOwnProperty(fleetId)) {
	            fleet = this.fleets[fleetId];
	            fleet.Render();
	        }
	    }
	}
}