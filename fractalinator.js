
// Get canvas and context elements
let canvas = document.getElementById('canvas');
canvas.width = window.innerWidth - 30
canvas.height = window.innerHeight - 30
let ctx = canvas.getContext('2d');

// Initialize artwork and paint to canvas
async function main(params) {
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

document.addEventListener("mousedown", (event) => {
  if (event.button === 0) { 
    drawing = true; 
  }
});
document.addEventListener("mouseup", (event) => {
  if (event.button === 0) {
    drawing = false;
  } 
});

// recalculate frame when mouse is moved
canvas.addEventListener("mousemove", async (event) => {
  if (drawing) {
    let pyodide = await pyodideReadyPromise;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    let proxy = pyodide.runPython(`
      rgb = art.paint_stroke(${x}, ${y})
      createUint8ClampedArray(rgb)
    `)
    
    let pixelData = new Uint8ClampedArray(proxy.toJs());
    let brush_radius = (Math.sqrt(pixelData.length / 4) - 1) / 2

    imageData = new ImageData(pixelData, 2 * brush_radius + 1)
    ctx.putImageData(imageData, x - brush_radius, y - brush_radius);
  }
});
