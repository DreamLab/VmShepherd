from .abstract import AbstractHealthcheck


class DummyHealthcheck(AbstractHealthcheck):
    status = True

    def __init__(self, config=None):
        pass

    async def is_healthy(self, vm):
        return self.status

    def set_status(self, healthy):
        self.status = healthy
