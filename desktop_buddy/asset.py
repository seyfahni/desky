import collections
import math
import os
import wx.svg
from PIL import Image


def prepare_image(image_file):
    file_without_extension, image_type = os.path.splitext(image_file)

    if image_type.casefold() == ".svg":
        # noinspection PyArgumentList
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
        assert region_mask.GetSize() == self.image.GetSize()
        self.size = region_mask.GetSize()
        offset_config = config.get('position', {'x': 0, 'y': 0})
        self.offset = Point(offset_config.get('x', 0), offset_config.get('y', 0))
        self.region = wx.Region(region_mask, wx.Colour(0, 0, 0))
        box = self.region.GetBox()
        self.move(-box.GetX(), -box.GetY())
        self.region.Offset(self.offset.x, self.offset.y)
        self.active = config.get('active', True)

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


def load_assets(assets_config):
    assets = collections.OrderedDict()
    for asset_id, asset_config in assets_config.items():
        if 'file' in asset_config:
            # TODO: Move config extraction from constructor to here (or sub-methods)
            assets[asset_id] = GraphicAsset(asset_config)
        else:
            raise NotImplementedError('Unknown trigger: ' + asset_id, asset_config)
    return assets
