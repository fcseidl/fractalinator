
// Get canvas and context elements
let canvas = document.getElementById('canvas');
canvas.width = window.innerWidth - 30
canvas.height = window.innerHeight - 30
let ctx = canvas.getContext('2d');

// Initialize artwork and paint to canvas
async function main() {
  let pyodide = await loadPyodide({
    packages: ["numpy", "matplotlib"]
  });
  await pyodide.loadPackage(window.location.origin + "/dist/fractalinator-1.0-py3-none-any.whl");
  let pixelData = new Uint8ClampedArray(
    pyodide.runPython(`
      from fractalinator import Artwork
      from fractalinator.util import createUint8ClampedArray
      art = Artwork(shape=(${canvas.width}, ${canvas.height}), cmap_name="jet", brush_strength=90)
      createUint8ClampedArray(art.rgb)
    `).toJs()
  );
  imageData = new ImageData(pixelData, canvas.width)
  ctx.putImageData(imageData, 0, 0);
  console.log("main() complete")
  return pyodide;
}
pyodideReadyPromise = main();

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
    
    // update canvas
    let pixelData = new Uint8ClampedArray(raw);
    let brush_radius = (Math.sqrt(pixelData.length / 4) - 1) / 2;
    imageData = new ImageData(pixelData, 2 * brush_radius + 1);
    ctx.putImageData(imageData, x - brush_radius, y - brush_radius);
  }
});


// apply new kwargs when apply button is pressed
async function onApplyClick() {
    let pyodide = await pyodideReadyPromise;
    pyodide.runPython(`
        new_art = Artwork(shape=(${canvas.width}, ${canvas.height}), ${kwargs.value})
        new_art.buffered_intensity = art.buffered_intensity
        art = new_art    
    `)

}
document.getElementById("apply-button").setAttribute("onclick", "onApplyClick()");

