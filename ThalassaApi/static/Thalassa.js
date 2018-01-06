$(function () {
    let type = "WebGL";
    if (!PIXI.utils.isWebGLSupported()) {
        type = "canvas";
    }

    PIXI.utils.sayHello(type)

    //Aliases
    Application = PIXI.Application;
    loader = PIXI.loader;
    resources = PIXI.loader.resources;
    Sprite = PIXI.Sprite;

    //Create a Pixi Application
    Thalassa = new Application({
        width: 1024,
        height: 1024,
        antialias: true,
        transparent: false,
    });

    Thalassa.renderer.backgroundColor = 0xb7c0d3;
    Thalassa.renderer.view.style.position = "absolute";
    Thalassa.renderer.view.style.display = "block";
    Thalassa.renderer.autoResize = true;
    Thalassa.renderer.resize(window.innerWidth, window.innerHeight);

    //Add the canvas that Pixi automatically created for you to the HTML document
    document.body.appendChild(Thalassa.view);

    // Load all the resources
    loader
        .add("static/images/island_icon.png")
        .load(OnGameLoaded);
})

function OnGameLoaded() {
    let island1 = new Sprite(resources["static/images/island_icon.png"].texture);
    Thalassa.stage.addChild(island1);
}