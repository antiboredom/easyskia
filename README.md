# EasySkia

A quick, very very work-in-progress redux of p5py. Lets you draw with Skia in Python in a Processing-style way, with many functions borrowed from p5py's skia renderer. You probably shouldn't use this yet.

## Goals & Non-Goals:

### Goals

- simple, p5/processing-like api for skia
- more "pythony" than p5py, and exposes more skia stuff
- good for exporting animation as video files, images, and pdfs suitable for printing
- can be headless

### Non-Goals

- user interaction (mouse/keyboard/etc)
- audio


# Basic Examples

Drawing

```python
from easyskia import Canvas
c = Canvas(width=600, height=600, show=True)
x = 0
while c.animate():
    c.background(1, 1, 1)
    c.fill(1, 0, 0)
    c.stroke(0, 1, 0)
    c.ellipse(x, 100, 50, 50)
    x = x + 1
```

Saving videos

```python
from easyskia import Canvas
c = Canvas(width=600, height=600, show=False)
c.save_video("testing.mp4", frames=200)
x = 0
while c.animate():
    c.background(1, 1, 1)
    c.fill(1, 0, 0)
    c.stroke(0, 1, 0)
    c.ellipse(x, 100, 50, 50)
    x = x + 1
```

Exporting PDFs

```python
from easyskia import Canvas
c = Canvas(width=600, height=600, renderer="PDF", output="testing.pdf")
c.background(1, 1, 1)
c.rect(100, 100, 120, 150)
c.add_page()
c.rect(200, 200, 90, 90)
c.save_pdf()
```

# Docs

* [easyskia.canvas](#easyskia.canvas)
  * [Canvas](#easyskia.canvas.Canvas)
    * [\_\_init\_\_](#easyskia.canvas.Canvas.__init__)
    * [setup\_raster](#easyskia.canvas.Canvas.setup_raster)
    * [setup\_pdf](#easyskia.canvas.Canvas.setup_pdf)
    * [setup\_gl](#easyskia.canvas.Canvas.setup_gl)
    * [background](#easyskia.canvas.Canvas.background)
    * [clear](#easyskia.canvas.Canvas.clear)
    * [fill](#easyskia.canvas.Canvas.fill)
    * [stroke](#easyskia.canvas.Canvas.stroke)
    * [stroke\_weight](#easyskia.canvas.Canvas.stroke_weight)
    * [no\_fill](#easyskia.canvas.Canvas.no_fill)
    * [no\_stroke](#easyskia.canvas.Canvas.no_stroke)
    * [text\_font](#easyskia.canvas.Canvas.text_font)
    * [text\_size](#easyskia.canvas.Canvas.text_size)
    * [text\_style](#easyskia.canvas.Canvas.text_style)
    * [line](#easyskia.canvas.Canvas.line)
    * [ellipse](#easyskia.canvas.Canvas.ellipse)
    * [circle](#easyskia.canvas.Canvas.circle)
    * [quad](#easyskia.canvas.Canvas.quad)
    * [rect](#easyskia.canvas.Canvas.rect)
    * [triangle](#easyskia.canvas.Canvas.triangle)
    * [text](#easyskia.canvas.Canvas.text)
    * [load\_font](#easyskia.canvas.Canvas.load_font)
    * [load\_image](#easyskia.canvas.Canvas.load_image)
    * [image](#easyskia.canvas.Canvas.image)
    * [animate](#easyskia.canvas.Canvas.animate)
    * [add\_page](#easyskia.canvas.Canvas.add_page)
    * [render](#easyskia.canvas.Canvas.render)
    * [push](#easyskia.canvas.Canvas.push)
    * [pop](#easyskia.canvas.Canvas.pop)
    * [translate](#easyskia.canvas.Canvas.translate)
    * [rotate](#easyskia.canvas.Canvas.rotate)
    * [scale](#easyskia.canvas.Canvas.scale)
    * [save](#easyskia.canvas.Canvas.save)
    * [save\_frame](#easyskia.canvas.Canvas.save_frame)
    * [save\_pdf](#easyskia.canvas.Canvas.save_pdf)
    * [save\_video](#easyskia.canvas.Canvas.save_video)
    * [save\_video\_frame](#easyskia.canvas.Canvas.save_video_frame)
    * [finish\_video](#easyskia.canvas.Canvas.finish_video)

<a id="easyskia.canvas"></a>

# easyskia.canvas

<a id="easyskia.canvas.Canvas"></a>

## Canvas Objects

```python
class Canvas()
```

<a id="easyskia.canvas.Canvas.__init__"></a>

### \_\_init\_\_

```python
def __init__(width: int = DEFAULT_WIDTH,
             height: int = DEFAULT_HEIGHT,
             show: bool = False,
             renderer: str = "GPU",
             title: str = "EasySkia",
             output: Optional[str] = None)
```

Create a canvas

**Arguments**:

- `width` _int_ - width of canvas
- `height` _int_ - height of canvas
- `show` _bool_ - show the canvas
- `renderer` _str_ - renderer to use (GPU, CPU, PDF)
- `title` _str_ - title of window
- `output` _str_ - output path for PDF renderer

<a id="easyskia.canvas.Canvas.setup_raster"></a>

### setup\_raster

```python
def setup_raster()
```

Setup a raster canvas

<a id="easyskia.canvas.Canvas.setup_pdf"></a>

### setup\_pdf

```python
def setup_pdf(output: str)
```

Setup a PDF canvas

**Arguments**:

- `output` _str_ - output path

<a id="easyskia.canvas.Canvas.setup_gl"></a>

### setup\_gl

```python
def setup_gl()
```

Setup a GPU canvas

<a id="easyskia.canvas.Canvas.background"></a>

### background

```python
def background(r: float, g: float, b: float, a=1.0)
```

Set the background color

**Arguments**:

- `r` _float_ - red value
- `g` _float_ - green value
- `b` _float_ - blue value
- `a` _float_ - alpha value (default: 1.0)

<a id="easyskia.canvas.Canvas.clear"></a>

### clear

```python
def clear()
```

Clear the canvas

<a id="easyskia.canvas.Canvas.fill"></a>

### fill

```python
def fill(r: float, g: float, b: float, a: float = 1.0)
```

Set the fill color

**Arguments**:

- `r` _float_ - red value
- `g` _float_ - green value
- `b` _float_ - blue value
- `a` _float_ - alpha value (default: 1.0)

<a id="easyskia.canvas.Canvas.stroke"></a>

### stroke

```python
def stroke(r: float, g: float, b: float, a: float = 1.0)
```

Set the stroke color

**Arguments**:

- `r` _float_ - red value
- `g` _float_ - green value
- `b` _float_ - blue value
- `a` _float_ - alpha value (default: 1.0)

<a id="easyskia.canvas.Canvas.stroke_weight"></a>

### stroke\_weight

```python
def stroke_weight(w: float)
```

Set the stroke weight

**Arguments**:

- `w` _float_ - stroke weight

<a id="easyskia.canvas.Canvas.no_fill"></a>

### no\_fill

```python
def no_fill()
```

Disable fill

<a id="easyskia.canvas.Canvas.no_stroke"></a>

### no\_stroke

```python
def no_stroke()
```

Disable stroke

<a id="easyskia.canvas.Canvas.text_font"></a>

### text\_font

```python
def text_font(fontname: str)
```

Set the text font

**Arguments**:

- `fontname` _str_ - font name

<a id="easyskia.canvas.Canvas.text_size"></a>

### text\_size

```python
def text_size(size: float)
```

Set the text size

**Arguments**:

- `size` _float_ - font size

<a id="easyskia.canvas.Canvas.text_style"></a>

### text\_style

```python
def text_style(s: str)
```

Set the text style

**Arguments**:

- `s` _str_ - text style

<a id="easyskia.canvas.Canvas.line"></a>

### line

```python
def line(x1: float, y1: float, x2: float, y2: float)
```

Draw a line

**Arguments**:

- `x1` _float_ - x1
- `y1` _float_ - y1
- `x2` _float_ - x2
- `y2` _float_ - y2

<a id="easyskia.canvas.Canvas.ellipse"></a>

### ellipse

```python
def ellipse(x: float, y: float, w: float, h: float)
```

Draw an ellipse

**Arguments**:

- `x` _float_ - x
- `y` _float_ - y
- `w` _float_ - width
- `h` _float_ - height

<a id="easyskia.canvas.Canvas.circle"></a>

### circle

```python
def circle(x: float, y: float, d: float)
```

Draw a circle

**Arguments**:

- `x` _float_ - x
- `y` _float_ - y
- `d` _float_ - diameter

<a id="easyskia.canvas.Canvas.quad"></a>

### quad

```python
def quad(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float,
         x4: float, y4: float)
```

Draw a quad

**Arguments**:

- `x1` _float_ - x1
- `y1` _float_ - y1
- `x2` _float_ - x2
- `y2` _float_ - y2
- `x3` _float_ - x3
- `y3` _float_ - y3
- `x4` _float_ - x4
- `y4` _float_ - y4

<a id="easyskia.canvas.Canvas.rect"></a>

### rect

```python
def rect(x: float,
         y: float,
         w: float,
         h: float,
         tl: Optional[float] = None,
         tr: Optional[float] = None,
         br: Optional[float] = None,
         bl: Optional[float] = None)
```

Draw a rectangle

**Arguments**:

- `x` _float_ - x
- `y` _float_ - y
- `w` _float_ - width
- `h` _float_ - height
- `tl` _float_ - top left corner radius
- `tr` _float_ - top right corner radius
- `br` _float_ - bottom right corner radius
- `bl` _float_ - bottom left corner radius

<a id="easyskia.canvas.Canvas.triangle"></a>

### triangle

```python
def triangle(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float)
```

Draw a triangle

**Arguments**:

- `x1` _float_ - x1
- `y1` _float_ - y1
- `x2` _float_ - x2
- `y2` _float_ - y2
- `x3` _float_ - x3
- `y3` _float_ - y3

<a id="easyskia.canvas.Canvas.text"></a>

### text

```python
def text(text: str, x: float, y: float)
```

Draw text

**Arguments**:

- `text` _str_ - text to draw
- `x` _float_ - x
- `y` _float_ - y

<a id="easyskia.canvas.Canvas.load_font"></a>

### load\_font

```python
def load_font(path: str) -> skia.Typeface
```

Load a font

**Arguments**:

- `path` _str_ - path to font file

<a id="easyskia.canvas.Canvas.load_image"></a>

### load\_image

```python
def load_image(path: str) -> skia.Image
```

Load an image

**Arguments**:

- `path` _str_ - path to image file

<a id="easyskia.canvas.Canvas.image"></a>

### image

```python
def image(image: skia.Image,
          x: float,
          y: float,
          w: Optional[float] = None,
          h: Optional[float] = None)
```

Draw an image

**Arguments**:

- `image` _skia.Image_ - image to draw
- `x` _float_ - x
- `y` _float_ - y
- `w` _float_ - width
- `h` _float_ - height

<a id="easyskia.canvas.Canvas.animate"></a>

### animate

```python
def animate()
```

Animate the canvas

<a id="easyskia.canvas.Canvas.add_page"></a>

### add\_page

```python
def add_page(width: Optional[float] = None, height: Optional[float] = None)
```

Add a page to a PDF canvas

**Arguments**:

- `width` _float_ - width of page
- `height` _float_ - height of page

<a id="easyskia.canvas.Canvas.render"></a>

### render

```python
def render(rewind=True)
```

Render the shape/image/text etc to the canvas

<a id="easyskia.canvas.Canvas.push"></a>

### push

```python
def push()
```

Push the canvas state

<a id="easyskia.canvas.Canvas.pop"></a>

### pop

```python
def pop()
```

Pop the canvas state

<a id="easyskia.canvas.Canvas.translate"></a>

### translate

```python
def translate(x: float, y: float)
```

Translate the canvas

**Arguments**:

- `x` _float_ - x
- `y` _float_ - y

<a id="easyskia.canvas.Canvas.rotate"></a>

### rotate

```python
def rotate(deg: float)
```

Rotate the canvas

**Arguments**:

- `deg` _float_ - degrees to rotate

<a id="easyskia.canvas.Canvas.scale"></a>

### scale

```python
def scale(sx: float, sy: Optional[float] = None)
```

Scale the canvas

**Arguments**:

- `sx` _float_ - x scale
- `sy` _float_ - y scale

<a id="easyskia.canvas.Canvas.save"></a>

### save

```python
def save(filename: str = "frame.png")
```

Save the canvas to a file

**Arguments**:

- `filename` _str_ - filename to save to

<a id="easyskia.canvas.Canvas.save_frame"></a>

### save\_frame

```python
def save_frame(filename: Optional[str] = None)
```

Save a frame. If filename is None, it will be named frame_0000000000.jpg

**Arguments**:

- `filename` _str_ - filename to save to

<a id="easyskia.canvas.Canvas.save_pdf"></a>

### save\_pdf

```python
def save_pdf()
```

Save the PDF canvas

<a id="easyskia.canvas.Canvas.save_video"></a>

### save\_video

```python
def save_video(filename: str = "sketch.mp4",
               fps: int = 60,
               max_frames: int = 0)
```

Save a video

**Arguments**:

- `filename` _str_ - filename to save to
- `fps` _float_ - frames per second
- `max_frames` _int_ - maximum number of frames to record

<a id="easyskia.canvas.Canvas.save_video_frame"></a>

### save\_video\_frame

```python
def save_video_frame()
```

Save a video frame

<a id="easyskia.canvas.Canvas.finish_video"></a>

### finish\_video

```python
def finish_video()
```

Finish recording a video


