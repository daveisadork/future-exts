# future-exts

Adds `.completed`, `.map` and `.then` methods to the Python 2 [futures][futures] library.

## Setup

`pip install future-exts`

## Example

``` python
import future_exts  # noqa
import re
import requests
import threading

from concurrent.futures import Future, ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=8)
anchor_re = re.compile(r'<a href="([^"]+)">')
seen = set()


def process(response):
    futures = []
    for match in anchor_re.finditer(response.text):
        anchor = match.group(1)
        if anchor not in seen and anchor.startswith("http://"):
            futures.append(crawl(anchor))

    return Future.sequence(futures)


def read_url(url):
    print "Crawling", url, "on thread", threading.current_thread()
    return requests.get(url)


def crawl(url):
    seen.add(url)
    return executor.submit(read_url, url).then(process)


future = crawl("http://reddit.com")
future.result()
```

[futures]: https://pypi.python.org/pypi/futures
