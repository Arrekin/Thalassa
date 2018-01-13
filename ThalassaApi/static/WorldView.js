var WorldIslandView = function (id, worldView) {
	this.id = id;
	this.worldView = worldView;

	// Model data
	this.name = null;
	this.x = null;
	this.y = null;

	// View data
	this.sprite = null;
}

WorldIslandView.prototype = {

	UpdateData: function () {
		let model = this.worldView.GetWorldModel();
		islandModel = model.islands[this.id];
		this.name = islandModel.name;
		this.x = islandModel.x;
		this.y = islandModel.y;

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
	    this.worldView.RegisterSprite(this.sprite);
	}
}

var WorldView = function (thalassaApp) {

	this.thalassa = thalassaApp;

	this.islands = {};

	this.islandsDataChangedHandler = this.OnIslandsDataChanged.bind(this);
	this.GetWorldModel().islandsDataChangedEvent.attach(this.islandsDataChangedHandler);
}

WorldView.prototype = {

	GetWorldModel: function () {
		return this.thalassa.worldModel;
	},

	OnIslandsDataChanged: function () {
		//alert("New islands data!");
		let islandsModels = this.GetWorldModel().islands;
		for (var islandId in islandsModels) {
			if (islandsModels.hasOwnProperty(islandId)) {
				if (!this.islands.hasOwnProperty(islandId)) {
					// This island do not exist in the view. Add it.
					this.islands[islandId] = new WorldIslandView(islandId, this);
				}
				// Let the island view update itself
				this.islands[islandId].UpdateData();
			}
		}
	},

	RegisterSprite: function (sprite) {
	    this.thalassa.stage.addChild(sprite);
	}
}