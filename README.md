[![Travis Master](https://img.shields.io/travis/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://travis-ci.org/SethMichaelLarson/stormhttp/branches)
[![Coveralls Master](https://img.shields.io/coveralls/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://coveralls.io/github/SethMichaelLarson/stormhttp)
[![Requires.io](https://img.shields.io/requires/github/SethMichaelLarson/stormhttp.svg?maxAge=300)](https://requires.io/github/SethMichaelLarson/stormhttp/requirements)
[![PyPI](https://img.shields.io/pypi/v/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)
[![PyPI](https://img.shields.io/pypi/dm/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)

Stormhttp is a lightning-fast asynchronous web framework for Python 3.5+. It is suitable for both client and server use. Stormhttp has been built to be a speedy lower-level replacement for aiohttp without sacrificing usability.

> **NOTE:** This project is currently in alpha (>0.1.0) and therefore may not be suitable for production environments.

## Installation

Stormhttp requires Python 3.5+ and is [available on PyPI](https://pypi.python.org/pypi/stormhttp). 

You can use pip to install it with the following command: ([Using a virtual environment is encouraged](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwj90s7yr_vOAhUYzmMKHUBfDBMQFggeMAA&url=http%3A%2F%2Fdocs.python-guide.org%2Fen%2Flatest%2Fdev%2Fvirtualenvs%2F&usg=AFQjCNEvupNSRAVxfumkI5JFoxABd0GHhQ)):

```
python -m pip install stormhttp
```

If you would prefer to work with the latest development version you may download it directly from Github via the following link.
```
git clone https://www.github.com/SethMichaelLarson/stormhttp.git
cd stormhttp && python setup.py install
```

## Features

- Complete HTTP client and server functionality.
- Super fast HTTP [parser](https://github.com/MagicStack/httptools/) and builder.
- Extremely flexible by having minimal decisions made for you. Power users rejoice!
- Support SSL/TLS for HTTPS connections.
- WebSockets v7 (hybi-07), v8 (hybi-10), and v13 (RFC 6455) are all supported.
- Cookies that can be stored offline for future Client sessions.
- Tons of optional extensions like Sessions, CORS, Authentication, all ready to use!
- All modules and installation requirements are licensed under MIT to allow maximum usability.

... and many more! View our documentation for a complete list of features.

## License

Stormhttp is licensed under the MIT license.
