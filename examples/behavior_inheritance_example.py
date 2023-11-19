import stateforward as sf


class Print(sf.Behavior):
    def activity(self, event: sf.Event):
        print(f"{self.qualified_name} -> {event.qualified_name}")


class AsyncPrint(sf.Behavior):
    async def activity(self, event: sf.Event):
        print(f"{self.qualified_name} -> {event.qualified_name}")
