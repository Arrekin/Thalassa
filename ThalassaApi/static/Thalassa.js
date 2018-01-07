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

    Thalassa.worldModel = new WorldModel(Thalassa);
    Thalassa.worldView = new WorldView(Thalassa);
}