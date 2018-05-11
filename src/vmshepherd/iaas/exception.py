class IaasException(Exception):
    pass


class IaasPresetConfigurationException(IaasException):
    pass


class IaasCommunicationException(IaasException):
    pass


class IaasAuthException(IaasException):
    pass
