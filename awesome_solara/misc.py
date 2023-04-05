from typing import Callable, TypeVar

from solara.lab import Reactive

T = TypeVar("T")


def reactive_factory(factory: Callable[[], T]) -> Callable[[], Reactive[T]]:
    def _factory():
        return Reactive(factory())

    return _factory
