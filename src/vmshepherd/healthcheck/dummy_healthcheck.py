from .abstract import AbstractHealthcheck


class DummyHealthcheck(AbstractHealthcheck):

    def __init__(self, config=None):
        pass

    async def is_healthy(self, vm):
        return True
