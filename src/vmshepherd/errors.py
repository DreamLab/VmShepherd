class VmShepherdError(Exception):
    message = None

    def __init__(self, message):
        super().__init__(self.message)
        self.message = message
        assert self.message is not None

    def __str__(self):
        return 'VmShepherdError: %s' % self.message

    def __repr__(self):
        return 'VmShepherdError(message=%s)' % repr(self.message)


class PresetNotFound(VmShepherdError):
    def __init__(self, preset_name):
        """
        :param preset_name: Preset human friendly id
        """
        self.message = f"Preset {preset_name} not found"
        super().__init__(self.message)
