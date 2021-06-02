from __future__ import annotations

import wx
from . import time, denormalize


class ActiveTimeTrigger:

    def millis_until_activation(self, now=None) -> int:
        raise NotImplementedError()

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

    def activate(self, now=None) -> ActiveTimeTrigger:
        raise NotImplementedError()


class TriggerList(TimeTrigger):

    trigger_list: list

    def __init__(self, trigger_list: list = None) -> None:
        if trigger_list is None:
            trigger_list = []
        self.trigger_list = trigger_list

    def activate(self, now=None) -> ActiveTriggerList:
        if now is None:
            now = time.now_millis()
        triggers = [trigger.activate(now) for trigger in self.trigger_list]
        return ActiveTriggerList(triggers)

    def append(self, trigger: TimeTrigger):
        self.trigger_list.append(trigger)


class ActiveTriggerList(TriggerList, ActiveTimeTrigger):

    def __init__(self, trigger_list) -> None:
        super().__init__(trigger_list)
        if len(trigger_list) < 1:
            raise ValueError()
        self.trigger_list.sort()

    def millis_until_activation(self, now=None) -> int:
        return self.trigger_list[0].millis_until_activation(now)


class TimeInstantTrigger(TimeTrigger, ActiveTimeTrigger):

    def __init__(self, trigger_time: wx.DateTime) -> None:
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

    def __init__(self, trigger_times) -> None:
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
            now = wx.DateTime.Now()
        else:
            now = time.to_date_time(now)
        triggers = [time.set_to_future(wx.DateTime(trigger.trigger_time), now) for trigger in self.sub_trigger]
        triggers.sort()
        return TimeInstantListTrigger(triggers)

    def millis_until_activation(self, now=None) -> int:
        return self.sub_trigger[0].millis_until_activation(now)


class IntervalTrigger(TimeTrigger):

    def __init__(self, milli_seconds_interval) -> None:
        self.interval = milli_seconds_interval

    def activate(self, now=None) -> ActiveTimeTrigger:
        if now is None:
            now = time.now_millis()
        return ActiveIntervalTrigger(self.interval, now)


class ActiveIntervalTrigger(IntervalTrigger, ActiveTimeTrigger):

    def __init__(self, milli_seconds_interval, now) -> None:
        super().__init__(milli_seconds_interval)
        self.started = time.to_milli_seconds(now)
        self.complete = self.started + self.interval

    def activate(self, now=None) -> ActiveTimeTrigger:
        if now is None:
            now = time.now_millis()
        else:
            now = time.to_milli_seconds(now)
        if self.millis_until_activation(now) > 0:
            return self
        last_possible_completion = self.complete + ((now - self.complete) // self.interval) * self.interval
        return ActiveIntervalTrigger(self.interval, last_possible_completion)

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


class IntervalTriggerDenormalizer(denormalize.Denormalizer):

    def denormalize(self, config):
        trigger_interval = config['every']
        millis_interval = time.parse_time_duration(trigger_interval)
        return IntervalTrigger(millis_interval)

    def supports_denormalization(self, config):
        return 'every' in config


def _create_instant_trigger(trigger_instant):
    try:
        trigger_time = time.parse_time_instant(trigger_instant)
        return TimeInstantTrigger(trigger_time)
    except time.InvalidInstantException as exception:
        raise denormalize.UnsupportedException(exception, message=exception.get_message())


class InstantTriggerDenormalizer(denormalize.Denormalizer):

    def denormalize(self, config):
        trigger_instant = config['on']
        if isinstance(trigger_instant, str):
            return _create_instant_trigger(trigger_instant)
        trigger_list = []
        for single_trigger_instant in trigger_instant:
            single_trigger = _create_instant_trigger(single_trigger_instant)
            trigger_list.append(single_trigger)
        return TimeInstantListTrigger(trigger_list)

    def supports_denormalization(self, config):
        return 'on' in config


trigger_denormalizer = denormalize.PriorityDenormalizer()
trigger_denormalizer.register(IntervalTriggerDenormalizer())
trigger_denormalizer.register(InstantTriggerDenormalizer())


def load_trigger(config) -> TriggerList:
    trigger_list = TriggerList()
    for trigger_config in config:
        trigger_list.append(trigger_denormalizer.denormalize(trigger_config))
    return trigger_list

