class SerializerByActionMixin:
    serializer_action_classes = {}

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, super().get_serializer_class())
