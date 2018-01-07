var WorldIslandView = function (id, worldView) {
	this.id = id;
	this.worldView = worldView;

	this.name = null;
	this.x = null;
	this.y = null;

	this.UpdateData();
}

WorldIslandView.prototype = {

	UpdateData: function () {
		let model = this.worldView.worldModel;
		island_model = model.island[this.id];
		this.name = island_model.name;
		this.x = island_model.x;
		this.y = island_model.y;
	}
}

var WorldView = function (worldModel) {

	this.worldModel = worldModel;

	this.islandsDataChangedHandler = this.OnIslandsDataChanged.bind(this);
	this.worldModel.islandsDataChangedEvent.attach(this.islandsDataChangedHandler);
}

WorldView.prototype = {

	OnIslandsDataChanged: function () {
		alert("New islands data!");
	}
}