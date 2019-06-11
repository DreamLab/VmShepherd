class VmShepherdError(Exception):
    message = None
    details = None

    def __init__(self, message, details=None):
        super().__init__(self.message)
        self.message = message
        self.details = details if details else ''
        assert self.message is not None

    def __str__(self):
        if self.details:
            return 'VmShepherdError: %s, details=%s' % (self.message, self.details)
        return 'VmShepherdError: %s' % self.message

    def __repr__(self):
        if self.details:
            return 'VmShepherdError(message=%s, details=%s' % (repr(self.message), repr(self.details))
        return 'VmShepherdError(message=%s)' % repr(self.message)


class PresetNotFound(VmShepherdError):
    def __init__(self, preset_name):
        """
        :param preset_name: Preset human friendly id
        """
        self.message = f"Preset {preset_name} not found"
        super().__init__(self.message)


class IaaSError(VmShepherdError):
    def __init__(self, message='IaaSError', details=None):
        super().__init__(message, details)


class IaasPresetConfigurationError(IaaSError):
    def __init__(self, message='IaaSPresetConfigurationError', details=None):
        super().__init__(message, details)


class IaasCommunicationError(IaaSError):
    def __init__(self, message='IaaSPresetConfigurationError', details=None):
        super().__init__(message, details)


class IaasAuthError(IaaSError):
    def __init__(self, message='IaaSAuthError', details=None):
        super().__init__(message, details)


class DummyIaasUserExc(IaaSError):
    def __init__(self, message, details):
        super().__init__(message, details)


class DummyIaasVmNotFound(DummyIaasUserExc):
    def __init__(self):
        super().__init__('VMNOTFOUND', 'Vm Not Found')
