
// Set up mouseover menu
const menu = document.getElementById('menu');
hamburger.addEventListener('mouseenter', () => {
  menu.style.display = 'block';
});
menu.addEventListener('mouseleave', () => {
  menu.style.display = 'none';
});

// Get canvas and context elements
let canvas = document.getElementById('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
let ctx = canvas.getContext('2d');

// set up Python
async function getPythonEnv() {
    console.log("Loading convolved noise...")
    let pyodide = await loadPyodide({packages: ["numpy", "matplotlib"]});
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("convolved-noise");
    if (window.location.origin == "https://fcseidl.github.io"){
      await pyodide.loadPackage("https://fcseidl.github.io/fractalinator/fractalinator-1.0-py3-none-any.whl");
    } else {
      await pyodide.loadPackage(window.location.origin + "/docs/fractalinator-1.0-py3-none-any.whl");
    }
    pyodide.runPython(`
      from fractalinator import Artwork
      from fractalinator.util import createUint8ClampedArray
    `)
    return pyodide;
}
var pyodideReadyPromise = getPythonEnv();

// get a random colormap
async function setRandomCmap() {
  let pyodide = await pyodideReadyPromise;
  cmap = pyodide.runPython(`
    import numpy as np
    import matplotlib.pyplot as plt
    str(np.random.choice(plt.colormaps()))
  `);
  let cmapInput = document.getElementById("cmap_name");
  cmapInput.setAttribute("value", cmap);
}
setRandomCmap();

// update entire canvas for new settings or on page load
async function updateCanvas() {
    let pyodide = await pyodideReadyPromise;
    let pixelData = new Uint8ClampedArray(
        pyodide.runPython(`createUint8ClampedArray(art.rgb)`).toJs()
    );
    let imageData = new ImageData(pixelData, canvas.width);
    ctx.putImageData(imageData, 0, 0);
}

// get user-specified arguments
function getMenuArgs() {
  menuArgs = ""
  for (const id of ["bailout_radius", "brush_radius", "cmap_name", "cmap_period", "max_it", "noise_seed", "noise_sig", "power"]) {
    let elt = document.getElementById(id);
    let val = elt.id == "cmap_name" ? `'${elt.value}'` : elt.value;
    menuArgs += `${elt.id}=${val}, `;
  }
  console.log(menuArgs);
  return menuArgs;
}

// Initialize artwork and paint to canvas
async function initializeCanvas() {
    let pyodide = await pyodideReadyPromise;
    pyodide.runPython(`
        art = Artwork(${getMenuArgs()}shape=(${canvas.width}, ${canvas.height}))
    `);
    updateCanvas();
    loading.style.display = "none";
}
initializeCanvas();

// Track mouse to only draw when left button is down
let drawing = false;
canvas.addEventListener("mousedown", (event) => {
  if (event.button === 0) { 
    drawing = true; 
  }
});
document.addEventListener("mouseup", (event) => {
  if (event.button === 0) {
    drawing = false;
  } 
});


function clamp(value, lo, hi) {
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

// recalculate frame when mouse is moved
canvas.addEventListener("mousemove", async (event) => {
  if (drawing) {
    // get motion location
    const rect = canvas.getBoundingClientRect();
    let x = Math.round(event.clientX - rect.left);
    let y = Math.round(event.clientY - rect.top);
    x = clamp(x, 0, canvas.width);
    y = clamp(y, 0, canvas.height);

    // call Python to modify image
    let pyodide = await pyodideReadyPromise;
    let raw = pyodide.runPython(`
      rgb = art.paint_stroke(${x}, ${y})
      createUint8ClampedArray(rgb)
    `).toJs();
    
    // update only a segment of the canvas
    let pixelData = new Uint8ClampedArray(raw);
    let brush_radius = (Math.sqrt(pixelData.length / 4) - 1) / 2;
    let imageData = new ImageData(pixelData, 2 * brush_radius + 1);
    ctx.putImageData(imageData, x - brush_radius, y - brush_radius);
  }
});

// apply new kwargs when apply button is pressed, or enter is pressed
async function onApplyClick() {
    let pyodide = await pyodideReadyPromise;
    pyodide.runPython(`art = Artwork(${getMenuArgs()}intensity=art.intensity)`);
    updateCanvas();
}
document.getElementById("apply-button").addEventListener("click", onApplyClick);
document.addEventListener("keyup", event => {
  if ((event.key == "Enter") && (menu.style.display != "none")) {
    menu.style.display = "none";
    onApplyClick();
  }
});

// bind save buttons
async function saveArt(sf) {
  // call Python to get high res image
  let pyodide = await pyodideReadyPromise;
  let raw = pyodide.runPython(`
    rgb = art.high_res(${sf})
    h, w, _ = rgb.shape
    createUint8ClampedArray(rgb)
  `).toJs();

  // create temp canvas
  let saveCanvas = document.createElement("canvas");
  saveCanvas.width = pyodide.runPython(`w`);
  saveCanvas.height = pyodide.runPython(`h`);
  const saveCtx = saveCanvas.getContext("2d");

  // save image to save-canvas
  let pixelData = new Uint8ClampedArray(raw);
  let imageData = new ImageData(pixelData, saveCanvas.width);
  saveCtx.putImageData(imageData, 0, 0);

  // perform download with temp link
  const saveLink = document.createElement("a");
  saveLink.href = saveCanvas.toDataURL();
  saveLink.download = "fractalination.png";
  saveLink.click();
  saveLink.remove();
  saveCanvas.remove();
}
document.getElementById("save-1").addEventListener("click", () => {
  saveArt(1);
});
document.getElementById("save-2").addEventListener("click", () => {
  saveArt(2);
});
document.getElementById("save-3").addEventListener("click", () => {
  saveArt(3);
});
