"""
Copyright (c) 2021 Emre Isikligil <emreisikligil@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

""" Requirements:
SQLAlchemy
"""

from enum import Enum
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta


def model2dict(
    cls=None,
    include: List[str] = None,
    exclude: List[str] = None,
    unmapped: List[str] = None,
    include_none=False,
):
    """Adds todict() method to SQLAlchemy model class which returns attributes as dict

    :param include: Include given attributes only
    :param exclude: Exclude given attributes. Ignored if include is provided.
    :param unmapped: Unmapped attributes to add to the dict.
    :param include_none: Include attributes whose value is None
    :return: Returns dict of all mapped columns, relationships, composites and synonyms.
    """

    def _wrapper(cls):
        if isinstance(cls, DeclarativeMeta):

            def getval(obj):
                if hasattr(obj, "todict"):
                    return obj.todict()
                elif isinstance(obj, list):
                    return [getval(item) for item in obj]
                elif isinstance(obj, Enum):
                    return obj.name
                else:
                    return obj

            def _todict(self):
                inst_state = inspect(self)
                keys = [
                    c.key for c in inst_state.attrs if c.key not in inst_state.unloaded
                ]
                if include is not None:
                    keys = [key for key in keys if key in include]
                elif exclude is not None:
                    keys = [key for key in keys if key not in exclude]
                if unmapped is not None:
                    [keys.append(attr)
                     for attr in unmapped if hasattr(self, attr)]
                return {
                    key: getval(getattr(self, key))
                    for key in keys
                    if include_none is True or getattr(self, key) is not None
                }

            setattr(cls, "todict", _todict)
        return cls

    # decorator is used with parens
    if cls is None:
        return _wrapper

    # decorator is used without parens
    return _wrapper(cls)
