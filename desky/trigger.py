import wx

from desky import time


class ActiveTimeTrigger:

    def millis_until_activation(self, now=None) -> int:
        pass

    def __eq__(self, other):
        if isinstance(other, ActiveTimeTrigger):
            now = time.now_millis()
            return self.millis_until_activation(now) == other.millis_until_activation(now)
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ActiveTimeTrigger):
            now = time.now_millis()
            return self.millis_until_activation(now) < other.millis_until_activation(now)
        else:
            return NotImplemented

    def __bool__(self):
        return self.millis_until_activation() <= 0


class TimeTrigger:

    def activate(self, now) -> ActiveTimeTrigger:
        pass


class TriggerList(TimeTrigger):

    def __init__(self, trigger_list):
        if len(trigger_list) <= 1:
            raise ValueError()
        self.trigger_list = trigger_list
        self.trigger_list.sort()

    def activate(self, now=None) -> ActiveTimeTrigger:
        if now is None:
            now = time.now_millis()
        triggers = [trigger.activate(now) for trigger in self.trigger_list]
        return TimeInstantListTrigger(triggers)


class ActiveTriggerList(TriggerList, ActiveTimeTrigger):

    def __init__(self, trigger_list):
        super().__init__(trigger_list)

    def millis_until_activation(self, now=None) -> int:
        return self.trigger_list[0].millis_until_activation(now)


class TimeInstantTrigger(TimeTrigger, ActiveTimeTrigger):

    def __init__(self, trigger_time: wx.DateTime):
        self.trigger_time = trigger_time
        self.trigger_time_millis = time.to_milli_seconds(trigger_time)

    def activate(self, now=None) -> ActiveTimeTrigger:
        if now is None:
            now = time.now_millis()
        trigger_time = wx.DateTime(self.trigger_time)
        time.set_to_future(trigger_time, now)
        return TimeInstantTrigger(trigger_time)

    def millis_until_activation(self, now=None) -> int:
        if now is None:
            now = time.now_millis()
        return self.trigger_time_millis - time.to_milli_seconds(now)

    def __eq__(self, other):
        if isinstance(other, TimeInstantTrigger):
            return self.trigger_time.IsEqualTo(other.trigger_time)
        else:
            return super().__eq__(other)

    def __lt__(self, other):
        if isinstance(other, TimeInstantTrigger):
            return self.trigger_time.IsEarlierThan(other.trigger_time)
        else:
            return super().__lt__(other)


class TimeInstantListTrigger(TimeTrigger, ActiveTimeTrigger):

    def __init__(self, trigger_times):
        if len(trigger_times) <= 1:
            raise ValueError()
        self.sub_trigger = []
        for trigger in trigger_times:
            if isinstance(trigger, wx.DateTime):
                trigger = TimeInstantTrigger(trigger)
            elif not isinstance(trigger, TimeInstantTrigger):
                raise TypeError()
            self.sub_trigger.append(trigger)
        self.sub_trigger.sort()

    def activate(self, now=None) -> ActiveTimeTrigger:
        if now is None:
            now = time.now_millis()
        triggers = [time.set_to_future(wx.DateTime(trigger.trigger_time), now) for trigger in self.sub_trigger]
        triggers.sort()
        return TimeInstantListTrigger(triggers)

    def millis_until_activation(self, now=None) -> int:
        return self.sub_trigger[0].millis_until_activation(now)


class IntervalTrigger(TimeTrigger):

    def __init__(self, milli_seconds_interval):
        self.interval = milli_seconds_interval

    def activate(self, now=None) -> ActiveTimeTrigger:
        if now is None:
            now = time.now_millis()
        return ActiveIntervalTrigger(self.interval, now)


class ActiveIntervalTrigger(IntervalTrigger, ActiveTimeTrigger):

    def __init__(self, milli_seconds_interval, now):
        super().__init__(milli_seconds_interval)
        self.started = time.to_milli_seconds(now)
        self.complete = self.started + self.interval

    def millis_until_activation(self, now=None) -> int:
        if now is None:
            now = time.now_millis()
        return self.complete - time.to_milli_seconds(now)

    def __eq__(self, other):
        if isinstance(other, ActiveIntervalTrigger):
            return self.complete == other.complete
        else:
            return super().__eq__(other)

    def __lt__(self, other):
        if isinstance(other, ActiveIntervalTrigger):
            return self.complete < other.complete
        else:
            return super().__lt__(other)


def load_trigger(config) -> TimeTrigger:
    pass
