import math
import os
import pathlib
import collections
import wx.svg
from PIL import Image
from ruamel.yaml import YAML


def prepare_image(image_file):
    file_without_extension, image_type = os.path.splitext(image_file)

    if image_type.casefold() == ".svg":
        svg_image = wx.svg.SVGimage.CreateFromFile(image_file)
        image_file = file_without_extension + ".png"
        width = math.ceil(svg_image.width)
        height = math.ceil(svg_image.height)
        png_image = svg_image.ConvertToBitmap(width=width, height=height)
        png_image.SaveFile(image_file, wx.BITMAP_TYPE_PNG)

    image = Image.open(image_file)
    if "A" in image.getbands():
        alpha_channel = image.getchannel("A")
        region_mask = alpha_channel.point(lambda a: a != 0 and 255)
        region_mask = region_mask.convert("1")
    else:
        region_mask = Image.new("1", image.size, 1)
    region_mask_file = file_without_extension + "_region_mask.png"
    region_mask.save(region_mask_file, "PNG")

    return {
        "image": image_file,
        "region_mask": region_mask_file,
    }


Point = collections.namedtuple('Point', ['x', 'y'])


class GraphicAsset:

    def __init__(self, config) -> None:
        super().__init__()
        prepared_images = prepare_image(config['file'])
        self.image = wx.Bitmap(prepared_images['image'])
        region_mask = wx.Bitmap(prepared_images['region_mask'])
        assert region_mask.Size == self.image.Size
        self.size = region_mask.Size
        offset_config = config['position']
        self.offset = Point(offset_config['x'], offset_config['y'])
        self.region = wx.Region(region_mask, wx.Colour(0, 0, 0))
        box = self.region.GetBox()
        self.move(-box.GetX(), -box.GetY())
        self.region.Offset(self.offset.x, self.offset.y)
        self.active = config['active'] if 'active' in config else True

    def move(self, offset_x, offset_y):
        self.region.Offset(offset_x, offset_y)
        self.offset = Point(self.offset.x + offset_x, self.offset.y + offset_y)

    def draw_active(self, context):
        if self.active:
            context.DrawBitmap(self.image, self.offset.x, self.offset.y, self.size.width, self.size.height)

    def draw(self, context):
        context.DrawBitmap(self.image, self.offset.x, self.offset.y, self.size.width, self.size.height)

    def toggle_active(self):
        self.active = not self.active


class DeskyFrame(wx.Frame):

    def __init__(self, config):
        window_config = config['window']
        title = window_config['title']
        self.background_color = wx.Colour(window_config['background'])

        self.assets = collections.OrderedDict()
        self.load_assets(config)

        full_region = wx.Region()
        for asset in self.assets.values():
            full_region.Union(asset.region)

        box = full_region.GetBox()
        for asset in self.assets.values():
            asset.move(-box.GetX(), -box.GetY())
        size = box.GetSize()

        style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_SHAPED | wx.BORDER_NONE
        super(DeskyFrame, self).__init__(None, title=title, size=size, style=style)
        self.active_region = wx.Region()
        self.calculate_active_region()

        self.timer = wx.Timer(self, 1)
        print('timer started:', self.timer.Start(2000))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_TIMER, self.on_timer)

    def load_assets(self, config):
        self.assets.clear()
        assets_config = config['assets']
        for asset_id, asset_config in assets_config.items():
            self.assets[asset_id] = GraphicAsset(asset_config)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(self.background_color, wx.BRUSHSTYLE_SOLID))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        for a in self.assets.values():
            a.draw_active(gc)

    def on_timer(self, event):
        self.assets['speech_bubble'].toggle_active()
        self.calculate_active_region()
        self.Refresh()

    def calculate_active_region(self):
        self.active_region.Clear()
        for asset in self.assets.values():
            if asset.active:
                self.active_region.Union(asset.region)
        self.SetShape(self.active_region)


if __name__ == '__main__':
    desky_config_file = pathlib.Path('config.yaml')

    yaml = YAML()
    desky_config = yaml.load(desky_config_file)

    app = wx.App()

    desky_frame = DeskyFrame(desky_config)

    desky_frame.Show()
    app.MainLoop()
