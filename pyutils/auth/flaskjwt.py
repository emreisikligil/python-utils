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
PyJWT
cryptography
Werkzeug
"""

from dataclasses import dataclass
from functools import wraps
import jwt
import logging
from flask import request
from jwt.exceptions import InvalidTokenError, ExpiredSignature
from werkzeug.exceptions import Unauthorized, InternalServerError


@dataclass
class Claims:
    sub: str
    exp: int
    iat: int
    nbf: str
    iss: str
    aud: str
    jti: str


class FlaskJWT:

    def __init__(self, key: str, algorithms: List[str], claims_cls: class = Claims):
        """

        """
        self.key = key
        self.algorithms = algorithms
        self.claims_cls = claims_cls

    def authenticated(self, func):
        """Decorator for making flask views authenticated

        * Reads JWT from the Authorization header
        * Validates the JWT
        * Builds claims object from the JWT
        * Pass the generated object to the decorated function with keyword arg claims

        Ex: 
        auth = FlaskJWT("key", ["RS256"])

        @app.route('/user/<user_id>', methods=['GET'])
        @auth.authenticated
        def get_user(user_id, claims):
            pass
        """

        @wraps(func)
        def _wrapper(*args, **kwargs):
            token = request.headers.get("Authorization", "")
            if not token:
                raise Unauthorized("authorization_required")
            token = re.sub("Bearer\s*", "", token)
            if not token:
                raise Unauthorized("missing_token")
            try:
                jwt_claims = jwt.decode(
                    token, self.key, algorithms=self.algorithms)
                claims = self.claims_cls(**jwt_claims)
            except ExpiredSignature:
                raise Unauthorized("Expired token")
            except InvalidTokenError:
                raise Unauthorized("Invalid token")
            except TypeError as e:
                logging.error(f"Could not parse claims from jwt: {e}")
                raise InternalServerError(
                    "Could not parse claims in the token")

            kwargs["claims"] = claims
            return func(*args, **kwargs)

        return _wrapper
