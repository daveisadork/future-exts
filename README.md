# future-exts

Adds `.completed`, `.map` and `.then` methods to the Python 2 [futures][futures] library.

## Setup

`pip install future-exts`

## Example

Here's a contrived example:

``` python
import future_exts  # noqa
import requests

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=8)

def read_url(url):
  print "Requesting", url
  return executor.submit(requests.get, url) \
                 .map(lambda res: (res.status_code, res.text))

def read_next_url(response):
  status, text = response
  if status == 404:
    return read_url("http://example.com")
  return response

future = read_url("http://yahoo.com/foo") \
  .then(read_next_url) \
  .then(read_next_url)
```

[futures]: https://pypi.python.org/pypi/futures
