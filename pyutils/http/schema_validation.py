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
Flask
fastjsonshchema
PyYAML
Werkzeug
"""

from functools import wraps

from fastjsonschema import JsonSchemaException, compile
from flask import request
from werkzeug.exceptions import UnprocessableEntity
from yaml import FullLoader, load


class SchemaNotFoundError(Exception):
    """Raised when the given schema is not defined"""

    def __init__(self, schema=None):
        self.msg = f"Schema cannot be found: {schema}"

    def __str__(self):
        return self.msg


class SchemaValidation:
    """ A Swagger validator for Flask request bodies

    This validator does not follow references in the schema. To be able to use it
    with schemas including $ref keys, schemas should be bundled by dereferencing
    all keys. https://www.npmjs.com/package/swagger-cli can be used for this purpose.

    Ex: swagger-cli bundle -r -o swagger-flat.yml -t yaml swagger.yml
    """

    def __init__(self, spec_path):
        self._spec_dict = load(open(spec_path, mode="r"), Loader=FullLoader)
        self._schemas = dict()
        for key, value in self._spec_dict["definitions"].items():
            self._schemas[key] = compile(value)

    def validate(self, schema_name):
        """
        Decorator for Flask views to validate request body against
        an object in the spec definitions. It also passes request body
        to the decorated function with body key.
        """

        def _decorator(func):
            @wraps(func)
            def _wrapper(*args, **kwargs):
                try:
                    validator = self._schemas[schema_name]
                    body = request.get_json()
                    validator(body)
                except KeyError:
                    raise SchemaNotFoundError(schema_name)
                except JsonSchemaException as e:
                    raise UnprocessableEntity(e.message)
                kwargs["body"] = body
                return func(*args, **kwargs)

            return _wrapper

        return _decorator
