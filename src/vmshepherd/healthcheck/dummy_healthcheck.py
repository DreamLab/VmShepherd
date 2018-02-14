from .abstract import AbstractHealthcheck


class DummyHealthcheck(AbstractHealthcheck):

    async def is_healthy(self, vm):
        return True
