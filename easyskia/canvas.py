from typing import Optional, Literal
import time
import glfw
import os
import skia
from skia import Color4f, Paint, Typeface, Font, Path
from OpenGL import GL
import imageio_ffmpeg


DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 600
DEFAULT_TITLE = "Sketch"

# NOTE: many of these functions are borrowed from p5py's skia renderer


class Canvas:
    def __init__(
        self,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        show: bool = False,
        renderer: Literal["GPU", "CPU", "PDF"] = "GPU",
        title: str = DEFAULT_TITLE,
        output: Optional[str] = None,
    ):
        """Create a canvas
        Args:
            width (int): width of canvas
            height (int): height of canvas
            show (bool): show the canvas
            renderer (str): renderer to use (GPU, CPU, PDF)
            title (str): title of window
            output (str): output path for PDF renderer
        """
        self.width = width
        self.height = height
        self.show = show
        self.renderer = renderer
        self.frame_count = 0
        self.title = title
        self.density = 1.0

        self.last_frame_time = 0
        self._fps = 1.0 / 60.0

        self.paint = Paint()
        self.paint.setAntiAlias(True)
        self.path = Path()

        self._fill = (0.5, 0.5, 0.5, 1)
        self._stroke = (0, 0, 0, 1)
        self._stroke_weight = 1
        self._alphaf = 1.0

        self._text_font = Font(Typeface())
        self._text_size = 16
        self._text_style = "normal"

        self.is_recording = False
        self.total_recorded_frames = 0
        self.max_frames = 0

        if renderer == "GPU":
            self.setup_gl()
        elif renderer == "CPU":
            self.setup_raster()
        elif renderer == "PDF":
            if output is None or output.lower().endswith(".pdf") is False:
                raise Exception("PDF renderer requires output path")
            self.setup_pdf(output)
        else:
            raise Exception("Invalid renderer: Pick between 'GPU', 'CPU', or 'PDF'")

    def setup_raster(self):
        """Setup a raster canvas"""
        self.surface = skia.Surface(self.width, self.height)
        self.canvas = self.surface.getCanvas()

    def setup_pdf(self, output: str):
        """Setup a PDF canvas
        Args:
            output (str): output path
        """
        self.stream = skia.FILEWStream(output)
        self.surface = skia.PDF.MakeDocument(self.stream)
        self.canvas = self.surface.beginPage(self.width, self.height)

    def setup_gl(self):
        """Setup a GPU canvas"""
        if not glfw.init():
            return

        if not self.show:
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

        glfw.window_hint(glfw.STENCIL_BITS, 8)  # why do i need this?

        window = glfw.create_window(self.width, self.height, self.title, None, None)

        if not window:
            glfw.terminate()
            return

        glfw.make_context_current(window)

        context = skia.GrDirectContext.MakeGL()
        (real_width, real_height) = glfw.get_framebuffer_size(window)
        self.density = glfw.get_window_content_scale(window)[0]
        self.width = real_width
        self.height = real_height
        backend_render_target = skia.GrBackendRenderTarget(
            real_width,
            real_height,
            0,  # sampleCnt
            0,  # stencilBits
            skia.GrGLFramebufferInfo(0, GL.GL_RGBA8),
        )
        surface = skia.Surface.MakeFromBackendRenderTarget(
            context,
            backend_render_target,
            skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType,
            skia.ColorSpace.MakeSRGB(),
        )
        self.window = window
        self.surface = surface
        self.context = context
        self.canvas = surface.getCanvas()

        self.canvas.scale(self.density, self.density)

    def background(self, r: float, g: float, b: float, a=1.0):
        """
        Set the background color
        Args:
            r (float): red value
            g (float): green value
            b (float): blue value
            a (float): alpha value (default: 1.0)
        """
        self.canvas.drawRect(
            skia.Rect(0, 0, self.width, self.height), paint=Paint(Color4f(r, g, b, a))
        )

    def clear(self):
        """Clear the canvas"""
        self.canvas.clear(Color4f(0, 0, 0, 0))

    def fill(self, r: float, g: float, b: float, a: float = 1.0):
        """Set the fill color
        Args:
            r (float): red value
            g (float): green value
            b (float): blue value
            a (float): alpha value (default: 1.0)
        """
        self._fill = (r, g, b, a)

    def alpha(self, a: float):
        """Set the alpha value of images drawn to the canvas
        Args:
            a (float): alpha value"""
        self._alphaf = a

    def stroke(self, r: float, g: float, b: float, a: float = 1.0):
        """Set the stroke color
        Args:
            r (float): red value
            g (float): green value
            b (float): blue value
            a (float): alpha value (default: 1.0)
        """
        self._stroke = (r, g, b, a)

    def stroke_weight(self, w: float):
        """Set the stroke weight
        Args:
            w (float): stroke weight
        """
        self._stroke_weight = w

    def no_fill(self):
        """Disable fill"""
        self._fill = None

    def no_stroke(self):
        """Disable stroke"""
        self._stroke_weight = 0

    def text_font(self, fontname: str):
        """Set the text font
        Args:
            fontname (str): font name
        """
        self._text_font = Font(Typeface(fontname))

    def text_size(self, size: float):
        """Set the text size
        Args:
            size (float): font size
        """
        self._text_size = size
        self._text_font.setSize(size)

    def text_style(self, s: Literal["bold", "bolditalic", "italic", "normal"]):
        """Set the text style
        Args:
            s (str): text style (bold, bolditalic, italic, normal)
        """
        skia_font_style = None
        if s == "bold":
            skia_font_style = skia.FontStyle.Bold()
        elif s == "bolditalic":
            skia_font_style = skia.FontStyle.BoldItalic()
        elif s == "italic":
            skia_font_style = skia.FontStyle.Italic()
        elif s == "normal":
            skia_font_style = skia.FontStyle.Normal()
        else:
            return False

        self._text_style = s
        family_name = self._text_font.getTypeface().getFamilyName()
        typeface = Typeface.MakeFromName(family_name, skia_font_style)
        self._text_font.setTypeface(typeface)

        return self

    def line(self, x1: float, y1: float, x2: float, y2: float):
        """Draw a line
        Args:
            x1 (float): x1
            y1 (float): y1
            x2 (float): x2
            y2 (float): y2
        """
        self.path.moveTo(x1, y1)
        self.path.lineTo(x2, y2)
        self.render()

    def ellipse(self, x: float, y: float, w: float, h: float):
        """Draw an ellipse
        Args:
            x (float): x
            y (float): y
            w (float): width
            h (float): height
        """
        # TODO: Switch to built in oval method

        kappa = 0.5522847498
        ox = w / 2 * kappa
        oy = h / 2 * kappa
        xe = x + w
        ye = y + h
        xm = x + w / 2
        ym = y + h / 2

        self.path.moveTo(x, ym)
        self.path.cubicTo(x, ym - oy, xm - ox, y, xm, y)
        self.path.cubicTo(xm + ox, y, xe, ym - oy, xe, ym)
        self.path.cubicTo(xe, ym + oy, xm + ox, ye, xm, ye)
        self.path.cubicTo(xm - ox, ye, x, ym + oy, x, ym)

        self.render()

    def circle(self, x: float, y: float, d: float):
        """Draw a circle
        Args:
            x (float): x
            y (float): y
            d (float): diameter
        """
        self.path.addCircle(x, y, d / 2)
        self.render()

    def quad(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
    ):
        """Draw a quad
        Args:
            x1 (float): x1
            y1 (float): y1
            x2 (float): x2
            y2 (float): y2
            x3 (float): x3
            y3 (float): y3
            x4 (float): x4
            y4 (float): y4
        """
        self.path.moveTo(x1, y1)
        self.path.lineTo(x2, y2)
        self.path.lineTo(x3, y3)
        self.path.lineTo(x4, y4)
        self.path.close()
        self.render()

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        tl: Optional[float] = None,
        tr: Optional[float] = None,
        br: Optional[float] = None,
        bl: Optional[float] = None,
    ):
        """Draw a rectangle
        Args:
            x (float): x
            y (float): y
            w (float): width
            h (float): height
            tl (float): top left corner radius
            tr (float): top right corner radius
            br (float): bottom right corner radius
            bl (float): bottom left corner radius
        """

        # TODO: make it more "skia-ish" and have sep func for rounded rect?

        if tl is None:
            self.path.moveTo(x, y)
            self.path.lineTo(x + w, y)
            self.path.lineTo(x + w, y + h)
            self.path.lineTo(x, y + h)
            self.path.close()
            self.render()
            return

        if tr is None:
            tr = tl
        if br is None:
            br = tr
        if bl is None:
            bl = br

        absW = abs(w)
        absH = abs(h)
        hw = absW / 2
        hh = absH / 2
        if absW < 2 * tl:
            tl = hw
        if absH < 2 * tl:
            tl = hh
        if absW < 2 * tr:
            tr = hw
        if absH < 2 * tr:
            tr = hh
        if absW < 2 * br:
            br = hw
        if absH < 2 * br:
            br = hh
        if absW < 2 * bl:
            bl = hw
        if absH < 2 * bl:
            bl = hh

        self.path.moveTo(x + tl, y)
        self.path.arcTo(x + w, y, x + w, y + h, tr)
        self.path.arcTo(x + w, y + h, x, y + h, br)
        self.path.arcTo(x, y + h, x, y, bl)
        self.path.arcTo(x, y, x + w, y, tl)
        self.path.close()

        self.render()

    def triangle(
        self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float
    ):
        """Draw a triangle
        Args:
            x1 (float): x1
            y1 (float): y1
            x2 (float): x2
            y2 (float): y2
            x3 (float): x3
            y3 (float): y3
        """
        self.path.moveTo(x1, y1)
        self.path.lineTo(x2, y2)
        self.path.lineTo(x3, y3)
        self.path.close()

        self.render()

    def arc(self):
        # TODO: implement
        raise NotImplementedError

    def polygon(self):
        # TODO: implement with addPoly
        raise NotImplementedError

    def create_path(self):
        # TODO: implement
        raise NotImplementedError

    def text(self, text: str, x: float, y: float):
        """Draw text
        Args:
            text (str): text to draw
            x (float): x
            y (float): y
        """
        if self._stroke_weight and self._stroke_weight > 0:
            self.paint.setStyle(Paint.kStroke_Style)
            self.paint.setColor(Color4f(*self._stroke))
            self.paint.setStrokeWidth(self._stroke_weight)
            self.canvas.drawSimpleText(text, x, y, self._text_font, self.paint)

        if self._fill:
            self.paint.setStyle(Paint.kFill_Style)
            self.paint.setColor(Color4f(*self._fill))
            self.canvas.drawSimpleText(text, x, y, self._text_font, self.paint)

    def load_font(self, path: str) -> skia.Typeface:
        """Load a font
        Args:
            path (str): path to font file
        """
        typeface = skia.Typeface().MakeFromFile(path=path)
        return typeface

    def load_image(self, path: str) -> skia.Image:
        """Load an image
        Args:
            path (str): path to image file
        """
        return skia.Image.open(path)

    def image(
        self,
        image: skia.Image,
        x: float,
        y: float,
        w: Optional[float] = None,
        h: Optional[float] = None,
    ):
        """Draw an image
        Args:
            image (skia.Image): image to draw
            x (float): x
            y (float): y
            w (Optional[float]): width
            h (Optional[float]): height
        """

        if w is None:
            w = image.width()
        if h is None:
            h = image.height()

        if self._alphaf < 1.0:
            self.paint.setAlphaf(self._alphaf)
            self.canvas.drawImageRect(
                image,
                skia.Rect(x, y, x + w, y + h),  # type: ignore
                paint=self.paint,
            )
        else:
            self.canvas.drawImageRect(image, skia.Rect(x, y, x + w, y + h))  # type: ignore

    def animate(self):
        """Animate the canvas"""
        self.frame_count += 1

        if self.is_recording:
            if self.max_frames == 0 or self.total_recorded_frames < self.max_frames:
                self.save_video_frame()
            else:
                self.finish_video()
                return False

        if self.renderer == "GPU" and self.show:
            now = glfw.get_time()
            if now - self.last_frame_time < self._fps:
                time.sleep(self._fps - (now - self.last_frame_time))
            self.last_frame_time = now

            # print(now, self.frame_count / now)
            # if now - self.last_frame_time > self._fps and self.show:

            self.surface.flushAndSubmit()
            glfw.swap_buffers(self.window)

            glfw.poll_events()

            if glfw.get_key(
                self.window, glfw.KEY_ESCAPE
            ) == glfw.PRESS or glfw.window_should_close(self.window):
                glfw.terminate()
                self.context.abandonContext()
                return False

        return True

    def add_page(self, width: Optional[float] = None, height: Optional[float] = None):
        """Add a page to a PDF canvas
        Args:
            width (float): width of page
            height (float): height of page
        """
        if width is None:
            width = self.width

        if height is None:
            height = self.height

        self.surface.endPage()
        self.surface.beginPage(width, height)

    def render(self, rewind=True):
        """Render the shape/image/text etc to the canvas"""
        if self._fill:
            self.paint.setStyle(Paint.kFill_Style)
            self.paint.setColor(Color4f(*self._fill))
            self.canvas.drawPath(self.path, self.paint)

        if self._stroke_weight and self._stroke_weight > 0:
            # self.paint.setStrokeCap(self.style.stroke_cap)
            # self.paint.setStrokeJoin(self.style.stroke_join)
            self.paint.setStyle(Paint.kStroke_Style)
            self.paint.setColor(Color4f(*self._stroke))
            self.paint.setStrokeWidth(self._stroke_weight)
            self.canvas.drawPath(self.path, self.paint)

        if rewind:
            self.path.rewind()

    def push(self):
        """Push the canvas state"""
        self.canvas.save()
        return self

    def pop(self):
        """Pop the canvas state"""
        self.canvas.restore()
        return self

    def translate(self, x: float, y: float):
        """Translate the canvas
        Args:
            x (float): x
            y (float): y
        """

        self.canvas.translate(x, y)
        return self

    def rotate(self, deg: float):
        """Rotate the canvas
        Args:
            deg (float): degrees to rotate
        """
        self.canvas.rotate(deg)
        return self

    def scale(self, sx: float, sy: Optional[float] = None):
        """Scale the canvas
        Args:
            sx (float): x scale
            sy (float): y scale
        """
        if sy is None:
            sy = sx
        self.canvas.scale(sx, sy)
        return self

    def save(self, filename: str = "frame.png"):
        """Save the canvas to a file
        Args:
            filename (str): filename to save to
        """
        encoding = skia.kPNG
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".png":
            encoding = skia.kPNG
        elif ext == ".jpg":
            encoding = skia.kJPEG
        elif ext == ".webp":
            encoding = skia.kWEBP
        else:
            print("invalid filename")
            return False

        image = self.surface.makeImageSnapshot()
        image.save(filename, encoding)
        if self.show:
            self.canvas.drawImage(image, 0, 0)
        return self

    def save_frame(self, filename: Optional[str] = None):
        """Save a frame. If filename is None, it will be named frame_0000000000.jpg
        Args:
            filename (str): filename to save to
        """
        f_count = str(self.frame_count).zfill(10)
        if filename is None:
            filename = f"frame_{f_count}.jpg"
        else:
            parts = os.path.splitext(filename)
            filename = f"{parts[0]}_{f_count}{parts[1]}"
        self.save(filename)

    def save_pdf(self):
        """Save the PDF canvas"""
        self.surface.close()

    def save_video(
        self,
        filename: str = "sketch.mp4",
        fps: int = 60,
        frames: int = 0,
        input_params: Optional[list[str]] = None,
        output_params: Optional[list[str]] = None,
    ):
        """Save a video
        Args:
            filename (str): filename to save to
            fps (float): frames per second
            frames (int): maximum number of frames to record
            input_params (Optional[list]): Additional ffmpeg input command line parameters.
            output_params (Optional[list]): Additional ffmpeg output command line parameters.
        """
        print("starting recording")
        self.total_recorded_frames = 0
        self.is_recording = True
        self.max_frames = frames
        self.writer = imageio_ffmpeg.write_frames(
            filename,
            (self.width, self.height),
            fps=fps,
            pix_fmt_in="rgba",
            input_params=input_params,
            output_params=output_params,
        )
        self.writer.send(None)

    def save_video_frame(self):
        """Save a video frame"""
        self.total_recorded_frames += 1
        self.writer.send(self.canvas.toarray())

    def finish_video(self):
        """Finish recording a video"""
        print("stopping recording")
        self.is_recording = False
        self.writer.close()
