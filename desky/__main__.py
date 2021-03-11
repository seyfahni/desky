import math
import wx.svg


class DeskyFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(DeskyFrame, self).__init__(*args, **kw)

        self.svg = wx.svg.SVGimage.CreateFromFile("assets/shapeblob.svg")

        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0), wx.BRUSHSTYLE_SOLID))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        self.svg.RenderToGC(gc)


if __name__ == '__main__':
    app = wx.App()
    renderer = wx.GraphicsRenderer.GetDefaultRenderer()

    shapeSvg = wx.svg.SVGimage.CreateFromFile("assets/shapeblob.svg")

    size = wx.Size(math.ceil(shapeSvg.width), math.ceil(shapeSvg.height))
    style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_SHAPED | wx.BORDER_NONE

    frame = DeskyFrame(None, title='Hello World 2', size=size, style=style)

    fullSize = frame.GetSize()

    bmp = shapeSvg.ConvertToScaledBitmap(size, frame)

    region = wx.Region(bmp, wx.Colour(0, 0, 0, wx.ALPHA_TRANSPARENT))
    frame.SetShape(region)

    regionBitmap = region.ConvertToBitmap()
    regionBitmap.SaveFile("test.png", wx.BITMAP_TYPE_PNG)

    frame.Show()
    app.MainLoop()
