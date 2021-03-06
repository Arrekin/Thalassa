$(function () {
    let type = "WebGL";
    if (!PIXI.utils.isWebGLSupported()) {
        type = "canvas";
    }

    PIXI.utils.sayHello(type)

    //Create a Pixi Application
    Thalassa = new PIXI.Application({
        width: 1024,
        height: 1024,
        antialias: true,
        transparent: false,
    });

    //Aliases
    Thalassa.resources = PIXI.loader.resources;
    Sprite = PIXI.Sprite;

    Thalassa.renderer.backgroundColor = 0xb7c0d3;
    Thalassa.renderer.view.style.position = "absolute";
    Thalassa.renderer.view.style.display = "block";
    Thalassa.renderer.autoResize = true;
    Thalassa.renderer.resize(window.innerWidth, window.innerHeight);

    //Add the canvas that Pixi automatically created for you to the HTML document
    document.body.appendChild(Thalassa.view);

    // Load all the resources
    PIXI.loader
        .add("static/images/island_icon.png")
        .load(OnGameLoaded);
})

function OnGameLoaded() {
    Thalassa.delta = 0;
    Thalassa.timestamp = Date.now() / 1000;

    Thalassa.stage.hitArea = new PIXI.Rectangle(0, 0, 600, 600);
    Thalassa.stage.interactive = true;
    Thalassa.stage.click = function (event) {
        let target = event.data.getLocalPosition(Thalassa.stage);
        console.log(target); // 'click', PIXI.DisplayObject {}
        $.ajax({
            method: "post",
            url: "world/cmd_move_fleet",
            data: { fleet_id: 1, x: target.x, y: target.y },
            success: (raw_data, status) => {
                console.log(status);
            }
        });
    };

    Thalassa.worldModel = new WorldModel(Thalassa);
    Thalassa.worldView = new WorldView(Thalassa);

    Thalassa.ticker.add(delta => OnGameStep(delta));
}

function OnGameStep(delta) {
    Thalassa.delta = delta;
    Thalassa.timestamp = Date.now() / 1000;
    Thalassa.worldView.Update();
}