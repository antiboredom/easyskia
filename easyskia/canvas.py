import time
import glfw
import os
import skia
from skia import Color4f, Paint, Typeface, Font, Path
from OpenGL import GL
import imageio_ffmpeg


DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 600

# NOTE: many of these functions are borrowed from p5py's skia renderer


class Canvas:
    def __init__(
        self,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT,
        show=False,
        renderer="GPU",
        title="EasySkia",
        output=None,
    ):
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
            raise Exception("Invalid renderer: Pick between GPU, CPU, or PDF")

    def setup_raster(self):
        self.surface = skia.Surface(self.width, self.height)
        self.canvas = self.surface.getCanvas()

    def setup_pdf(self, output):
        self.stream = skia.FILEWStream(output)
        self.surface = skia.PDF.MakeDocument(self.stream)
        self.canvas = self.surface.beginPage(self.width, self.height)

    def setup_gl(self):
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

    def background(self, r, g, b, a=1.0):
        self.canvas.drawRect(
            skia.Rect(0, 0, self.width, self.height), paint=Paint(Color4f(r, g, b, a))
        )

    def clear(self):
        self.canvas.clear(Color4f(0, 0, 0, 0))

    def fill(self, r, g, b, a=1):
        self._fill = (r, g, b, a)

    def stroke(self, r, g, b, a=1):
        self._stroke = (r, g, b, a)

    def stroke_weight(self, w):
        self._stroke_weight = w

    def no_fill(self):
        self._fill = None

    def no_stroke(self):
        self._stroke_weight = 0

    def text_font(self, fontname):
        self._text_font = Font(Typeface(fontname))

    def text_size(self, size):
        self._text_size = size
        self._text_font.setSize(size)

    def text_style(self, s):
        skia_font_style = None
        if s == "bold":
            skia_font_style = skia.FontStyle.Bold()
        elif s == "bolditalic":
            skia_font_style = skia.FontStyle.BoldItalic()
        elif s == "italic":
            skia_font_style = skia.FontStyle.BoldItalic()
        elif s == "normal":
            skia_font_style = skia.FontStyle.Normal()
        else:
            return False

        self._text_style = s
        # skia.Font.
        family_name = self._text_font.getTypeface().getFamilyName()
        typeface = Typeface.MakeFromName(family_name, skia_font_style)
        self._text_font.setTypeface(typeface)

        return self

    def line(self, path):
        x1, y1, x2, y2 = path[0].x, path[0].y, path[1].x, path[1].y
        self.path.moveTo(x1, y1)
        self.path.lineTo(x2, y2)
        self.render()

    def ellipse(self, x, y, w, h):
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

    def circle(self, x, y, d):
        self.path.addCircle(x, y, d / 2)
        self.render()

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.path.moveTo(x1, y1)
        self.path.lineTo(x2, y2)
        self.path.lineTo(x3, y3)
        self.path.lineTo(x4, y4)
        self.path.close()
        self.render()

    def rect(self, *args):
        x, y, w, h = args[:4]
        args = args[4:]
        tl = args[0] if len(args) >= 1 else None
        tr = args[1] if len(args) >= 2 else None
        br = args[2] if len(args) >= 3 else None
        bl = args[3] if len(args) >= 4 else None

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

    def triangle(self, *args):
        x1, y1, x2, y2, x3, y3 = args
        self.path.moveTo(x1, y1)
        self.path.lineTo(x2, y2)
        self.path.lineTo(x3, y3)
        self.path.close()

        self.render()

    def text(self, text, x, y):
        if self._stroke_weight and self._stroke_weight > 0:
            self.paint.setStyle(Paint.kStroke_Style)
            self.paint.setColor(Color4f(*self._stroke))
            self.paint.setStrokeWidth(self._stroke_weight)
            self.canvas.drawSimpleText(text, x, y, self._text_font, self.paint)

        if self._fill:
            self.paint.setStyle(Paint.kFill_Style)
            self.paint.setColor(Color4f(*self._fill))
            self.canvas.drawSimpleText(text, x, y, self._text_font, self.paint)

    def load_font(self, path):
        """
        path: string
        Absolute path of the font file
        returns: skia.Typeface
        """
        typeface = skia.Typeface().MakeFromFile(path=path)
        return typeface

    def load_image(self, path):
        return skia.Image.open(path)

    def image(self, image, x, y, w=None, h=None):
        if w is None:
            w = image.width()
        if h is None:
            h = image.height()
        self.canvas.drawImageRect(image, skia.Rect(x, y, x + w, y + h))

    def animate(self):
        self.frame_count += 1

        if self.is_recording:
            if self.max_frames == 0 or self.total_recorded_frames < self.max_frames:
                self.save_video_frame()
            else:
                self.finish_video()

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

    def add_page(self, width=None, height=None):
        if width is None:
            width = self.width

        if height is None:
            height = self.height

        self.surface.endPage()
        self.surface.beginPage(width, height)

    def render(self, rewind=True):
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
        self.canvas.save()
        return self

    def pop(self):
        self.canvas.restore()
        return self

    def translate(self, x, y):
        self.canvas.translate(x, y)
        return self

    def rotate(self, deg):
        self.canvas.rotate(deg)
        return self

    def scale(self, sx, sy=None):
        if sy is None:
            sy = sx
        self.canvas.scale(sx, sy)
        return self

    def save(self, filename="frame.png"):
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

    def save_frame(self, filename=None):
        f_count = str(self.frame_count).zfill(10)
        if filename is None:
            filename = f"frame_{f_count}.jpg"
        else:
            parts = os.path.splitext(filename)
            filename = f"{parts[0]}_{f_count}{parts[1]}"
        self.save(filename)

    def save_pdf(self):
        self.surface.close()

    def save_video(self, filename="sketch.mp4", fps=60, max_frames=0):
        print("starting recording")
        self.total_recorded_frames = 0
        self.is_recording = True
        self.max_frames = max_frames
        self.writer = imageio_ffmpeg.write_frames(
            filename, (self.width, self.height), fps=fps, pix_fmt_in="rgba"
        )
        self.writer.send(None)

    def save_video_frame(self):
        self.total_recorded_frames += 1
        self.writer.send(self.canvas.toarray())

    def finish_video(self):
        print("stopping recording")
        self.is_recording = False
        self.writer.close()
