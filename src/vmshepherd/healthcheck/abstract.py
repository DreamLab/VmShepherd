class AbstractHealthcheck:

    async def is_healthy(self, vm):
        raise NotImplementedError
