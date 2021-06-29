from desktop_buddy import asset


class Action:

    def activate(self, context=None):
        raise NotImplementedError()

    def is_invertible(self) -> bool:
        return False


class InvertibleAction(Action):

    def activate(self, context=None):
        raise NotImplementedError()

    def create_inverted_action(self, context=None) -> Action:
        raise NotImplementedError()

    def is_invertible(self) -> bool:
        return True


class ActionGroupAction(InvertibleAction):

    actions: list

    def __init__(self, actions: list):
        self.actions = actions

    def activate(self, context=None):
        for action in self.actions:
            action.activate(context)

    def create_inverted_action(self, context=None) -> Action:
        inverted_actions = []
        for action in self.actions:
            inverted = action.create_inverted_action(context)
            inverted_actions.append(inverted)
        return ActionGroupAction(inverted_actions)

    def is_invertible(self) -> bool:
        return all(action.is_invertible() for action in self.actions)


class AssetAction(InvertibleAction):

    graphics_asset: asset.GraphicAsset

    def __init__(self, graphics_asset: asset.GraphicAsset) -> None:
        super().__init__()
        self.graphics_asset = graphics_asset

    def activate(self, context=None):
        self.graphics_asset.toggle_active()

    def create_inverted_action(self, context=None) -> Action:
        return self


def load_actions(config):
    for action_name, action_config in config.items():
        duration = action_config.get('for', False)
        priority = action_config.get('priority', 0)
        changes = action_config['assets']
