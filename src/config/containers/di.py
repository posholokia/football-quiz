import copy
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Type,
    TypeVar,
    Union,
)

from independency.container import (
    Container as LibContainer,
    ContainerBuilder as LibContainerBuilder,
    ContainerError,
    Dependency,
    get_arg_names,
    get_deps,
    get_from_localns,
)


_T = TypeVar("_T")
ObjType = Union[str, Type[_T]]


class Scope(Enum):
    transient: int = 0
    singleton: int = 1
    cached: int = 2


@dataclass
class Registration:
    cls: ObjType[Any]
    factory: Callable[..., Any]
    scope: Scope
    kwargs: Dict[str, Any]


def _resolve_constants(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in kwargs.items():
        if not isinstance(value, Dependency):
            result[key] = value
    return result


def _validate_registration(
    cls: ObjType[Any], factory: Callable[..., Any], kwargs: Dict[str, Any]
) -> None:
    if generic_params := getattr(cls, "__parameters__", None):
        raise ValueError(
            f"Specify generic parameters for {cls=}: {generic_params}"
        )
    signature = get_arg_names(factory)
    for name in kwargs:
        if name not in signature:
            raise ValueError(f"No argument {name} for factory for type {cls}")


def _update_localns(cls: ObjType[Any], localns: Dict[str, Any]) -> None:
    if isinstance(cls, type):
        localns[cls.__name__] = cls
    else:
        localns[cls] = cls


class ResolutionCache:
    def __init__(self):
        self.cache: dict[str, Any] = {}

    def __setitem__(self, key, instance):
        self.cache[key] = instance

    def __getitem__(self, key) -> Any:
        return self.cache.get(key)

    def has_cached(self, key) -> bool:
        return key in self.cache

    def clear(self):
        self.cache = {}


class Container(LibContainer):  # pylint: disable=R0903
    __slots__ = ["_registry", "_localns", "_resolved", "_cache"]

    def __init__(
        self,
        registry: Dict[ObjType[Any], Registration],
        localns: Dict[str, Any],
    ):
        self._registry = registry
        self._localns = localns
        self._resolved: Dict[ObjType[Any], Any] = {}
        self._cache = ResolutionCache()

    def resolve(self, cls: ObjType[Any]) -> Any:
        result = self.resolve_impl(cls)
        self._cache.clear()
        return result

    def resolve_impl(self, cls: ObjType[Any]) -> Any:
        cls = get_from_localns(cls, self._localns)

        if cls in self._resolved:
            return self._resolved[cls]

        if self._cache.has_cached(cls):
            return self._cache[cls]

        try:
            current = self._registry[cls]
        except KeyError as e:
            raise ContainerError(f"No dependency of type {cls}") from e

        args = _resolve_constants(current.kwargs)
        deps_to_resolve = get_deps(current, self._localns)
        for key, d in deps_to_resolve.items():
            args[key] = self.resolve_impl(d)
        result = current.factory(**args)
        if current.scope is Scope.singleton:
            self._resolved[current.cls] = result
        if current.scope is Scope.cached:
            self._cache[cls] = result
        return result  # noqa: R504

    def create_test_container(self) -> "TestContainer":
        registry = copy.deepcopy(self._registry)
        localns = copy.deepcopy(self._localns)
        test_container = TestContainer(registry=registry, localns=localns)
        registry[Container] = Registration(
            Container,
            factory=lambda: test_container,
            scope=Scope.singleton,
            kwargs={},
        )
        _update_localns(Container, localns)
        return test_container


class TestContainer(Container):
    def with_overridden(
        self,
        cls: ObjType[Any],
        factory: Callable[..., Any],
        scope: Scope = Scope.transient,
        **kwargs: Any,
    ) -> "TestContainer":
        if cls not in self._registry:
            raise ContainerError(
                "Can not override class without any registration"
            )
        _validate_registration(cls, factory, kwargs)
        registry = copy.deepcopy(self._registry)
        localns = copy.deepcopy(self._localns)
        _update_localns(cls, localns)
        registry[cls] = Registration(
            cls=cls, factory=factory, kwargs=kwargs, scope=scope
        )
        container = TestContainer(registry, localns)
        registry[Container] = Registration(
            Container,
            factory=lambda: container,
            scope=Scope.singleton,
            kwargs={},
        )
        _update_localns(Container, localns)
        return container

    def with_overridden_singleton(
        self, cls: ObjType[Any], factory: Callable[..., Any], **kwargs: Any
    ) -> "TestContainer":
        return self.with_overridden(
            cls, factory, scope=Scope.singleton, **kwargs
        )


class ContainerBuilder(LibContainerBuilder):
    __slots__ = ["_registry", "_localns"]

    def __init__(self) -> None:
        self._registry: Dict[ObjType[Any], Registration] = {}
        self._localns: Dict[str, Any] = {}

    def build(self) -> Container:
        registry = self._registry.copy()
        localns = self._localns.copy()
        container = Container(registry=registry, localns=localns)
        registry[Container] = Registration(
            cls=Container,
            factory=lambda: container,
            kwargs={},
            scope=Scope.singleton,
        )
        _update_localns(Container, localns)
        self._check_resolvable(registry, localns)
        return container

    def singleton(
        self, cls: ObjType[Any], factory: Callable[..., Any], **kwargs: Any
    ) -> None:
        self.register(
            cls=cls, factory=factory, scope=Scope.singleton, **kwargs
        )

    def register(
        self,
        cls: ObjType[Any],
        factory: Callable[..., Any],
        scope: Scope = Scope.transient,
        **kwargs: Any,
    ) -> None:
        if cls in self._registry:
            raise ContainerError(f"Type {cls} is already registered")
        _validate_registration(cls, factory, kwargs)
        self._registry[cls] = Registration(
            cls=cls, factory=factory, kwargs=kwargs, scope=scope
        )
        _update_localns(cls, self._localns)
