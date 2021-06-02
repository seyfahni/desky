

class UnsupportedException(Exception):

    def __init__(self, *args: object, message=None, config=None) -> None:
        super().__init__(*args)
        self._message = message
        self._config = config

    def get_message(self):
        return self._message

    def get_config(self):
        return self._config


class Denormalizer:

    def denormalize(self, config):
        """
        Denormalize a config into the represented object.

        :param config: config to denormalize
        :raise UnsupportedException: when denormalizing an unsupported type
        """
        raise NotImplementedError()

    def supports_denormalization(self, config):
        raise NotImplementedError()


class PriorityDenormalizer(Denormalizer):

    def __init__(self) -> None:
        super().__init__()
        self.queue = []

    def register(self, denormalizer: Denormalizer, priority: int = 0):
        self.queue.append((priority, denormalizer))
        self.queue.sort(key=lambda p: p[0], reverse=True)

    def denormalize(self, config):
        for (_, denormalizer) in self.queue:
            if denormalizer.supports_denormalization(config):
                return denormalizer.denormalize(config)
        raise UnsupportedException(config=config, message='No denormalizer available.')

    def supports_denormalization(self, config):
        for _, denormalizer in self.queue:
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

            pass

    def supports_denormalization(self, config):
        pass
