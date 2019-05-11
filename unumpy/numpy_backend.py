import numpy as np
from uarray.backend import DispatchableInstance
from .multimethods import ufunc, ufunc_list, ndarray
import unumpy.multimethods as multimethods
import functools

from typing import Dict

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}

__ua_domain__ = "numpy"


def compat_check(args):
    args = [arg.value if isinstance(arg, DispatchableInstance) else arg for arg in args]
    return all(
        isinstance(arg, (np.ndarray, np.generic, np.ufunc))
        for arg in args
        if arg is not None
    )


_implementations: Dict = {
    multimethods.ufunc.__call__: np.ufunc.__call__,
    multimethods.ufunc.reduce: np.ufunc.reduce,
}


def __ua_function__(method, args, kwargs, dispatchable_args):
    if not compat_check(dispatchable_args):
        return NotImplemented

    if method in _implementations:
        return _implementations[method](*args, **kwargs)

    if not hasattr(np, method.__name__):
        return NotImplemented

    return getattr(np, method.__name__)(*args, **kwargs)


def __ua_coerce__(arg):
    if isinstance(arg, DispatchableInstance) and arg.dispatch_type is ndarray:
        return np.asarray(arg.value) if arg.value is not None else None

    if isinstance(arg, DispatchableInstance) and arg.dispatch_type is ufunc:
        return getattr(np, arg.value.name)

    return NotImplemented


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner
