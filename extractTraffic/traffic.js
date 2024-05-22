(function () {
    var createObjectURL = window.URL.createObjectURL;
    var createElement = document.createElement;
    var oldFunctions = new Map()
    var oldFetch = fetch;
    var offscreen2d = OffscreenCanvasRenderingContext2D;
    var internalCanvas = new OffscreenCanvas(1,1);
    var ctx = internalCanvas.getContext('2d')
    function call(type, name) {
        return oldFunctions.get(type).get(name)
    }
    function download_img(canvas) {
        canvas.convertToBlob().then(async (blob) => {
            var url = window.URL.createObjectURL(blob);
            var a_elm = document.createElement('a');
            a_elm.href = url;
            a_elm.setAttribute('download', 'map');
            document.body.appendChild(a_elm);
            a_elm.click();
            document.body.removeChild(a_elm);
        });
    }
    var drawMap = false;
    var skipDraw = 1;// the first drawing is the grid background not the map
    var canvasrenderingcontext2d = new Map([
        ['drawImage', function(obj, args) {
            if(args[0].width >= 256 && args[0].height >= 256 && args[0].width == args[0].height) {
                if (internalCanvas.width == 1 && 
                        internalCanvas.height == 1) {
                    internalCanvas.width = obj.canvas.width;
                    internalCanvas.height = obj.canvas.height;
                }
                call(offscreen2d, "drawImage").apply(ctx, args);
                drawMap = true;
            } else {
                if(drawMap) {
                    if(skipDraw == null || skipDraw == 0) { 
                        download_img(internalCanvas);
                        skipDraw = null;
                    } else {
                        if(skipDraw != null) {
                            skipDraw --;
                        }
                    }
                    drawMap = false;
                }
            }
        }],
        ['rotate', function(obj, args) {
            call(offscreen2d, "rotate").apply(ctx, args);
        }],
        ['scale', function(obj, args) {
            call(offscreen2d, "scale").apply(ctx, args);
        }],
        ['translate', function(obj, args) {
            call(offscreen2d, "translate").apply(ctx, args);
        }],
        ['transform', function(obj, args) {
            call(offscreen2d, "transform").apply(ctx, args);
        }],
        ['setTransform', function(obj, args) {
            call(offscreen2d, "setTransform").apply(ctx, args);
        }],
        ['resetTransform', function(obj, args) {
            call(offscreen2d, "resetTransform").apply(ctx, args);
        }],
        ['save', function(obj, args) {
            call(offscreen2d, "save").apply(ctx, args);
        }],
        ['restore', function(obj, args) {
            call(offscreen2d, "restore").apply(ctx, args);
        }],
    ]);

    var canvas = new Map([
        ['getContext', function(obj, args) {
            if(args[0] == "webgl" || args[0] == "experimental-webgl" || args[0] == "webgl2" || args[0] == "moz-webgl") {return true;}
        }]
    ]);

    function wrapper(func, wrapped_func) {
        return function() {
            try {
                if (func(this, arguments) == true) {
                    return null;
                }
            } catch(err) {
                console.log(err);
            }
            return wrapped_func.apply(this, arguments);
        }
    }
    function wrapObject(obj, functions) {
        var names = Object.getOwnPropertyNames(obj.prototype);
        for (name of names) {
            try {
                if (functions.has(name)) {
                    var wrapped_func = obj.prototype[name];
                    if (!oldFunctions.has(obj)) {
                        oldFunctions.set(obj, new Map());
                    }
                    oldFunctions.get(obj).set(name, wrapped_func);
                    obj.prototype[name] = wrapper(functions.get(name), wrapped_func);
                }
            } catch(err) {console.log(err)}
        }
    }
    wrapObject(CanvasRenderingContext2D, canvasrenderingcontext2d);
    wrapObject(OffscreenCanvasRenderingContext2D, canvasrenderingcontext2d);
    wrapObject(HTMLCanvasElement, canvas);
    wrapObject(OffscreenCanvas, canvas);
}())
