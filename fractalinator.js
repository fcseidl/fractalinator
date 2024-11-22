
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
canvas.width = window.innerWidth
canvas.height = window.innerHeight
let ctx = canvas.getContext('2d');

// set up Python
async function getPythonEnv() {
    let pyodide = await loadPyodide({packages: ["numpy", "matplotlib"]});
    await pyodide.loadPackage(window.location.origin + "/dist/fractalinator-1.0-py3-none-any.whl");
    pyodide.runPython(`
      from fractalinator import Artwork
      from fractalinator.util import createUint8ClampedArray
    `)
    return pyodide;
}
var pyodideReadyPromise = getPythonEnv();

// update entire canvas for new settings or on page load
async function updateCanvas() {
    let pyodide = await pyodideReadyPromise;
    let pixelData = new Uint8ClampedArray(
        pyodide.runPython(`createUint8ClampedArray(art.rgb)`).toJs()
    );
    imageData = new ImageData(pixelData, canvas.width);
    ctx.putImageData(imageData, 0, 0);
}

// get user-specified arguments
function getMenuArgs() {
  menuArgs = ""
  for (const id of ["bailout_radius", "brush_radius", "cmap_name", "max_it", "noise_seed", "noise_sig", "power"]) {
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
    imageData = new ImageData(pixelData, 2 * brush_radius + 1);
    ctx.putImageData(imageData, x - brush_radius, y - brush_radius);
  }
});

// apply new kwargs when apply button is pressed
async function onApplyClick() {
    let pyodide = await pyodideReadyPromise;
    pyodide.runPython(`art = Artwork(${getMenuArgs()}intensity=art.intensity)`);
    updateCanvas();
}
document.getElementById("apply-button").setAttribute("onclick", "onApplyClick()");

