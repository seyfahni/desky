import pathlib
import wx
from ruamel.yaml import YAML
from . import trigger, asset


class DeskyFrame(wx.Frame):

    def __init__(self, config):
        window_config = config['window']
        title = window_config['title']
        self.background_color = wx.Colour(window_config['background'])

        self.assets = asset.load_assets(config.get('assets', []))

        full_region = wx.Region()
        for single_asset in self.assets.values():
            full_region.Union(single_asset.region)

        box = full_region.GetBox()
        for single_asset in self.assets.values():
            single_asset.move(-box.GetX(), -box.GetY())
        size = box.GetSize()

        style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_SHAPED | wx.BORDER_NONE
        super(DeskyFrame, self).__init__(None, title=title, size=size, style=style)
        self.active_region = wx.Region()
        self.calculate_active_region()

        self.trigger = trigger.load_trigger(config.get('trigger', []))
        self.trigger = self.trigger.activate()

        self.timer = wx.Timer(self, 1)
        self.timer.StartOnce(self.trigger.millis_until_activation())

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_TIMER, self.on_timer)

    def on_paint(self, event: wx.PaintEvent):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(self.background_color, wx.BRUSHSTYLE_SOLID))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        for a in self.assets.values():
            a.draw_active(gc)

    def on_timer(self, event: wx.TimerEvent):
        self.assets['speech_bubble'].toggle_active()
        self.calculate_active_region()
        self.Refresh()

        self.trigger = self.trigger.activate()
        event.GetTimer().StartOnce(self.trigger.millis_until_activation())

    def calculate_active_region(self):
        self.active_region.Clear()
        for single_asset in self.assets.values():
            if single_asset.active:
                self.active_region.Union(single_asset.region)
        self.SetShape(self.active_region)


if __name__ == '__main__':
    desky_config_file = pathlib.Path('config.yaml')

    yaml = YAML()
    desky_config = yaml.load(desky_config_file)

    app = wx.App()

    desky_frame = DeskyFrame(desky_config)

    desky_frame.Show()
    app.MainLoop()
