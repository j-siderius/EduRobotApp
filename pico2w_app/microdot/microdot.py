"""
microdot
--------

The ``microdot`` module defines a few classes that help implement HTTP-based
servers for MicroPython and standard Python.
"""
import asyncio
import io
import re
import time

try:
    import orjson as json  # type: ignore[import-not-found]
except ImportError:
    import json

try:
    from inspect import iscoroutinefunction, iscoroutine
    from functools import partial

    async def invoke_handler(handler, *args, **kwargs):
        """Invoke a handler and return the result.

        This method runs sync handlers in a thread pool executor.
        """
        if iscoroutinefunction(handler):
            ret = await handler(*args, **kwargs)
        else:
            ret = await asyncio.get_running_loop().run_in_executor(
                None, partial(handler, *args, **kwargs))
        return ret
except ImportError:  # pragma: no cover
    def iscoroutine(coro):  # type: ignore[misc]
        return hasattr(coro, 'send') and hasattr(coro, 'throw')

    async def invoke_handler(handler, *args, **kwargs):
        """Invoke a handler and return the result.

        This method runs sync handlers in the asyncio thread, which can
        potentially cause blocking and performance issues.
        """
        ret = handler(*args, **kwargs)
        if iscoroutine(ret):
            ret = await ret
        return ret

try:
    from sys import print_exception  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    import traceback

    def print_exception(exc):
        traceback.print_exc()

MUTED_SOCKET_ERRORS = [
    32,  # Broken pipe
    54,  # Connection reset by peer
    104,  # Connection reset by peer
    128,  # Operation on closed socket
]


def urldecode(s):
    if isinstance(s, str):
        s = s.encode()
    s = s.replace(b'+', b' ')
    parts = s.split(b'%')
    if len(parts) == 1:
        return s.decode()
    result = [parts[0]]
    for item in parts[1:]:
        if item == b'':
            result.append(b'%')
        else:
            code = item[:2]
            result.append(bytes([int(code, 16)]))
            result.append(item[2:])
    return b''.join(result).decode()


def urlencode(s):
    return s.replace('+', '%2B').replace(' ', '+').replace(
        '%', '%25').replace('?', '%3F').replace('#', '%23').replace(
            '&', '%26').replace('=', '%3D')


class NoCaseDict(dict):
    """A subclass of dictionary that holds case-insensitive keys.

    :param initial_dict: an initial dictionary of key/value pairs to
                         initialize this object with.

    Example::

        >>> d = NoCaseDict()
        >>> d['Content-Type'] = 'text/html'
        >>> print(d['Content-Type'])
        text/html
        >>> print(d['content-type'])
        text/html
        >>> print(d['CONTENT-TYPE'])
        text/html
        >>> del d['cOnTeNt-TyPe']
        >>> print(d)
        {}
    """
    def __init__(self, initial_dict=None):
        super().__init__(initial_dict or {})
        self.keymap = {k.lower(): k for k in self.keys() if k.lower() != k}

    def __setitem__(self, key, value):
        kl = key.lower()
        key = self.keymap.get(kl, key)
        if kl != key:
            self.keymap[kl] = key
        super().__setitem__(key, value)

    def __getitem__(self, key):
        kl = key.lower()
        return super().__getitem__(self.keymap.get(kl, kl))

    def __delitem__(self, key):
        kl = key.lower()
        super().__delitem__(self.keymap.get(kl, kl))

    def __contains__(self, key):
        kl = key.lower()
        return self.keymap.get(kl, kl) in self.keys()

    def get(self, key, default=None):
        kl = key.lower()
        return super().get(self.keymap.get(kl, kl), default)

    def update(self, other_dict):
        for key, value in other_dict.items():
            self[key] = value


def mro(cls):  # pragma: no cover
    """Return the method resolution order of a class.

    This is a helper function that returns the method resolution order of a
    class. It is used by Microdot to find the best error handler to invoke for
    the raised exception.

    In CPython, this function returns the ``__mro__`` attribute of the class.
    In MicroPython, this function implements a recursive depth-first scanning
    of the class hierarchy.
    """
    if hasattr(cls, 'mro'):
        return cls.__mro__

    def _mro(cls):
        m = [cls]
        for base in cls.__bases__:
            m += _mro(base)
        return m

    mro_list = _mro(cls)

    # If a class appears multiple times (due to multiple inheritance) remove
    # all but the last occurence. This matches the method resolution order
    # of MicroPython, but not CPython.
    mro_pruned = []
    for i in range(len(mro_list)):
        base = mro_list.pop(0)
        if base not in mro_list:
            mro_pruned.append(base)
    return mro_pruned


class MultiDict(dict):
    """A subclass of dictionary that can hold multiple values for the same
    key. It is used to hold key/value pairs decoded from query strings and
    form submissions.

    :param initial_dict: an initial dictionary of key/value pairs to
                         initialize this object with.

    Example::

        >>> d = MultiDict()
        >>> d['sort'] = 'name'
        >>> d['sort'] = 'email'
        >>> print(d['sort'])
        'name'
        >>> print(d.getlist('sort'))
        ['name', 'email']
    """
    def __init__(self, initial_dict=None):
        super().__init__()
        if initial_dict:
            for key, value in initial_dict.items():
                self[key] = value

    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, [])
        super().__getitem__(key).append(value)

    def __getitem__(self, key):
        return super().__getitem__(key)[0]

    def get(self, key, default=None, type=None):
        """Return the value for a given key.

        :param key: The key to retrieve.
        :param default: A default value to use if the key does not exist.
        :param type: A type conversion callable to apply to the value.

        If the multidict contains more than one value for the requested key,
        this method returns the first value only.

        Example::

            >>> d = MultiDict()
            >>> d['age'] = '42'
            >>> d.get('age')
            '42'
            >>> d.get('age', type=int)
            42
            >>> d.get('name', default='noname')
            'noname'
        """
        if key not in self:
            return default
        value = self[key]
        if type is not None:
            value = type(value)
        return value

    def getlist(self, key, type=None):
        """Return all the values for a given key.

        :param key: The key to retrieve.
        :param type: A type conversion callable to apply to the values.

        If the requested key does not exist in the dictionary, this method
        returns an empty list.

        Example::

            >>> d = MultiDict()
            >>> d.getlist('items')
            []
            >>> d['items'] = '3'
            >>> d.getlist('items')
            ['3']
            >>> d['items'] = '56'
            >>> d.getlist('items')
            ['3', '56']
            >>> d.getlist('items', type=int)
            [3, 56]
        """
        if key not in self:
            return []
        values = super().__getitem__(key)
        if type is not None:
            values = [type(value) for value in values]
        return values


class AsyncBytesIO:
    """An async wrapper for BytesIO."""
    def __init__(self, data):
        self.stream = io.BytesIO(data)

    async def read(self, n=-1):
        return self.stream.read(n)

    async def readline(self):  # pragma: no cover
        return self.stream.readline()

    async def readexactly(self, n):  # pragma: no cover
        return self.stream.read(n)

    async def readuntil(self, separator=b'\n'):  # pragma: no cover
        return self.stream.readuntil(separator=separator)

    async def awrite(self, data):  # pragma: no cover
        return self.stream.write(data)

    async def aclose(self):  # pragma: no cover
        pass


class Request:
    """An HTTP request."""
    #: Specify the maximum payload size that is accepted. Requests with larger
    #: payloads will be rejected with a 413 status code. Applications can
    #: change this maximum as necessary.
    #:
    #: Example::
    #:
    #:    Request.max_content_length = 1 * 1024 * 1024  # 1MB requests allowed
    max_content_length = 16 * 1024

    #: Specify the maximum payload size that can be stored in ``body``.
    #: Requests with payloads that are larger than this size and up to
    #: ``max_content_length`` bytes will be accepted, but the application will
    #: only be able to access the body of the request by reading from
    #: ``stream``. Set to 0 if you always access the body as a stream.
    #:
    #: Example::
    #:
    #:    Request.max_body_length = 4 * 1024  # up to 4KB bodies read
    max_body_length = 16 * 1024

    #: Specify the maximum length allowed for a line in the request. Requests
    #: with longer lines will not be correctly interpreted. Applications can
    #: change this maximum as necessary.
    #:
    #: Example::
    #:
    #:    Request.max_readline = 16 * 1024  # 16KB lines allowed
    max_readline = 2 * 1024

    class G:
        pass

    def __init__(self, app, client_addr, method, url, http_version, headers,
                 body=None, stream=None, sock=None, url_prefix='',
                 subapp=None, scheme=None, route=None):
        #: The application instance to which this request belongs.
        self.app = app
        #: The address of the client, as a tuple (host, port).
        self.client_addr = client_addr
        #: The HTTP method of the request.
        self.method = method
        #: The scheme of the request, either `http` or `https`.
        self.scheme = scheme or 'http'
        #: The request URL, including the path and query string, but not the
        #: scheme or the host, which is available in the ``Host`` header.
        self.url = url
        #: The URL prefix, if the endpoint comes from a mounted
        #: sub-application, or else ''.
        self.url_prefix = url_prefix
        #: The sub-application instance, or `None` if this isn't a mounted
        #: endpoint.
        self.subapp = subapp
        #: The route function that handles this request.
        self.route = route
        #: The path portion of the URL.
        self.path = url
        #: The query string portion of the URL.
        self.query_string = None
        #: The parsed query string, as a
        #: :class:`MultiDict <microdot.MultiDict>` object.
        self.args = {}
        #: A dictionary with the headers included in the request.
        self.headers = headers
        #: A dictionary with the cookies included in the request.
        self.cookies = {}
        #: The parsed ``Content-Length`` header.
        self.content_length = 0
        #: The parsed ``Content-Type`` header.
        self.content_type = None
        #: A general purpose container for applications to store data during
        #: the life of the request.
        self.g = Request.G()

        self.http_version = http_version
        if '?' in self.path:
            self.path, self.query_string = self.path.split('?', 1)
            self.args = self._parse_urlencoded(self.query_string)

        if 'Content-Length' in self.headers:
            self.content_length = int(self.headers['Content-Length'])
        if 'Content-Type' in self.headers:
            self.content_type = self.headers['Content-Type']
        if 'Cookie' in self.headers:
            for cookie in self.headers['Cookie'].split(';'):
                c = cookie.strip().split('=', 1)
                self.cookies[c[0]] = c[1] if len(c) > 1 else ''

        self._body = body
        self.body_used = False
        self._stream = stream
        self.sock = sock
        self._json = None
        self._form = None
        self._files = None
        self.after_request_handlers = []

    @staticmethod
    async def create(app, client_reader, client_writer, client_addr,
                     scheme=None):
        """Create a request object.

        :param app: The Microdot application instance.
        :param client_reader: An input stream from where the request data can
                              be read.
        :param client_writer: An output stream where the response data can be
                              written.
        :param client_addr: The address of the client, as a tuple.
        :param scheme: The scheme of the request, either 'http' or 'https'.

        This method is a coroutine. It returns a newly created ``Request``
        object.
        """
        # request line
        line = (await Request._safe_readline(client_reader)).strip().decode()
        if not line:  # pragma: no cover
            return None
        method, url, http_version = line.split()
        http_version = http_version.split('/', 1)[1]

        # headers
        headers = NoCaseDict()
        content_length = 0
        while True:
            line = (await Request._safe_readline(
                client_reader)).strip().decode()
            if line == '':
                break
            header, value = line.split(':', 1)
            value = value.strip()
            headers[header] = value
            if header.lower() == 'content-length':
                content_length = int(value)

        # body
        body = b''
        if content_length and content_length <= Request.max_body_length:
            body = await client_reader.readexactly(content_length)
            stream = None
        else:
            body = b''
            stream = client_reader

        return Request(app, client_addr, method, url, http_version, headers,
                       body=body, stream=stream,
                       sock=(client_reader, client_writer), scheme=scheme)

    def _parse_urlencoded(self, urlencoded):
        data = MultiDict()
        if len(urlencoded) > 0:  # pragma: no branch
            if isinstance(urlencoded, str):
                for kv in [pair.split('=', 1)
                           for pair in urlencoded.split('&') if pair]:
                    data[urldecode(kv[0])] = urldecode(kv[1]) \r
                        if len(kv) > 1 else ''
            elif isinstance(urlencoded, bytes):  # pragma: no branch
                for kv in [pair.split(b'=', 1)
                           for pair in urlencoded.split(b'&') if pair]:
                    data[urldecode(kv[0])] = urldecode(kv[1]) \r
                        if len(kv) > 1 else b''
        return data

    @property
    def body(self):
        """The body of the request, as bytes."""
        return self._body

    @property
    def stream(self):
        """The body of the request, as a bytes stream."""
        if self._stream is None:
            self._stream = AsyncBytesIO(self._body)
        return self._stream

    @property
    def json(self):
        """The parsed JSON body, or ``None`` if the request does not have a
        JSON body."""
        if self._json is None:
            if self.content_type is None:
                return None
            mime_type = self.content_type.split(';')[0]
            if mime_type != 'application/json':
                return None
            self._json = json.loads(self.body.decode())
        return self._json

    @property
    def form(self):
        """The parsed form submission body, as a
        :class:`MultiDict <microdot.MultiDict>` object, or ``None`` if the
        request does not have a form submission.

        Forms that are URL encoded are processed by default. For multipart
        forms to be processed, the
        :func:`with_form_data <microdot.multipart.with_form_data>`
        decorator must be added to the route.
        """
        if self._form is None:
            if self.content_type is None:
                return None
            mime_type = self.content_type.split(';')[0]
            if mime_type != 'application/x-www-form-urlencoded':
                return None
            self._form = self._parse_urlencoded(self.body)
        return self._form

    @property
    def files(self):
        """The files uploaded in the request as a dictionary, or ``None`` if
        the request does not have any files.

        The :func:`with_form_data <microdot.multipart.with_form_data>`
        decorator must be added to the route that receives file uploads for
        this property to be set.
        """
        return self._files

    def after_request(self, f):
        """Register a request-specific function to run after the request is
        handled. Request-specific after request handlers run at the very end,
        after the application's own a