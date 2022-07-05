

class SerializerActionClassMixin(object):
    """
    A class which inhertis this mixins should have variable
    `serializer_action_classes`.
    Look for serializer class in self.serializer_action_classes, which
    should be a dict mapping action name (key) to serializer class (value),
    """
    serializer_action_classes = {}

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(SerializerActionClassMixin, self).get_serializer_class()