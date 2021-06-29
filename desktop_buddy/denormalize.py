from __future__ import annotations

from abc import ABC


class UnsupportedException(Exception):

    def __init__(self, *args: object, message=None, config=None) -> None:
        super().__init__(*args)
        self._message = message
        self._config = config

    def get_message(self):
        return self._message

    def get_config(self):
        return self._config


class Denormalizer(ABC):

    def denormalize(self, config):
        """
        Denormalize a config into the represented object.

        :param config: config to denormalize
        :raise UnsupportedException: when denormalizing an unsupported type
        """
        raise NotImplementedError()

    def supports_denormalization(self, config) -> bool:
        """
        Check if a config is denormalizable with this denormalizer.

        :param config: config to check
        """
        raise NotImplementedError()


class PriorityDenormalizer(Denormalizer):

    def __init__(self) -> None:
        super().__init__()
        self._priority_list = []

    def register(self, denormalizer: Denormalizer, priority: int = 0) -> PriorityDenormalizer:
        self._priority_list.append((priority, denormalizer))
        self._priority_list.sort(key=lambda p: p[0], reverse=True)
        return self

    def denormalize(self, config):
        for (_, denormalizer) in self._priority_list:
            if denormalizer.supports_denormalization(config):
                return denormalizer.denormalize(config)
        raise UnsupportedException(config=config, message='No denormalizer available.')

    def supports_denormalization(self, config) -> bool:
        for _, denormalizer in self._priority_list:
            if denormalizer.supports_denormalization(config):
                return True
        return False


def _supply_list():
    return []


class ListDenormalizer(Denormalizer):

    def __init__(self, denormalizer: Denormalizer, list_supplier: callable = None) -> None:
        super().__init__()
        self._denormalizer = denormalizer
        if list_supplier is None:
            list_supplier = _supply_list
        self._list_supplier = list_supplier

    def denormalize(self, config):
        object_list = self._list_supplier()
        for object_config in config:
            if not self._denormalizer.supports_denormalization(object_config):
                raise UnsupportedException(config=object_config, message='List item cannot be denormalized.')
            denormalized = self._denormalizer.denormalize(object_config)
            object_list.append(denormalized)
        return object_list

    def supports_denormalization(self, config) -> bool:
        try:
            for object_config in config:
                if not self._denormalizer.supports_denormalization(object_config):
                    return False
            return True
        except TypeError:
            return False


def _supply_dict():
    return {}


class DictDenormalizer(Denormalizer):

    def __init__(self, denormalizer: Denormalizer, dict_supplier: callable = None) -> None:
        super().__init__()
        self._denormalizer = denormalizer
        if dict_supplier is None:
            dict_supplier = _supply_dict
        self._dict_supplier = dict_supplier

    def denormalize(self, config):
        object_dict = self._dict_supplier()
        for object_name, object_config in config:
            if not self._denormalizer.supports_denormalization(object_config):
                raise UnsupportedException(config=object_config, message='List item cannot be denormalized.')
            denormalized = self._denormalizer.denormalize(object_config)
            object_dict[object_name](denormalized)
        return object_dict

    def supports_denormalization(self, config) -> bool:
        try:
            for object_name, object_config in config:
                if not self._denormalizer.supports_denormalization(object_config):
                    return False
            return True
        except TypeError:
            return False
