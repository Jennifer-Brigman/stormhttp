__all__ = [
    "STATUS_CODES"
]
STATUS_CODES = {
    100: b"Continue",
    101: b"Switching Protocols",
    102: b"Processing",  # RFC 2518
    200: b"OK",
    201: b"Created",
    202: b"Accepted",
    203: b"Non-Authoritative Information",
    204: b"No Content",
    205: b"Reset Content",
    206: b"Partial Content",  # RFC 7233
    207: b"Multi-Status",  # RFC 4918
    208: b"Already Reported",  # RFC 5842
    226: b"IM Used",  # RFC 3229
    300: b"Multiple Choices",
    301: b"Moved Permanently",
    302: b"Found",
    303: b"See Other",
    304: b"Not Modified",  # RFC 7232
    305: b"Use Proxy",
    306: b"Switch Proxy",
    307: b"Temporary Redirect",
    308: b"Permanent Redirect",  # RFC 7538
    400: b"Bad Request",
    401: b"Unauthorized",  # RFC 7235
    402: b"Payment Required",
    403: b"Forbidden",
    404: b"Not Found",
    405: b"Method Not Allowed",
    406: b"Not Acceptable",
    407: b"Proxy Authentication Required",  # RFC 7235
    408: b"Request Timeout",
    409: b"Conflict",
    410: b"Gone",
    411: b"Length Required",
    412: b"Precondition Failed",  # RFC 7232
    413: b"Payload Too Large",  # RFC 7231
    414: b"URI Too Long",  # RFC 7231
    415: b"Unsupported Media Type",
    416: b"Range Not Satisfiable",  # RFC 7233
    417: b"Expectation Failed",
    418: b"I'm a teapot",  # RFC 2324 (IETF April Fool's joke)
    421: b"Misdirected Request",  # RFC 7540
    422: b"Unprocessable Entity",  # RFC 4918
    423: b"Locked",  # RFC 4918
    424: b"Failed Dependency",  # RFC 4918
    426: b"Upgrade Required",
    428: b"Precondition Required",  # RFC 6585
    429: b"Too Many Requests",  # RFC 6585
    431: b"Request Header Fields Too Large",  # RFC 6585
    451: b"Unavailable for Legal Reasons",
    500: b"Internal Server Error",
    501: b"Not Implemented",
    502: b"Bad Gateway",
    503: b"Service Unavailable",
    504: b"Gateway Timeout",
    505: b"HTTP Version Not Supported",
    506: b"Variant Also Negotiates",  # RFC 2295
    507: b"Insufficient Storage",  # RFC 4918
    508: b"Loop Detected",  # RFC 5842
    510: b"Not Extended",  # RFC 2274
    511: b"Network Authentication Required"  # RFC 6585
}
