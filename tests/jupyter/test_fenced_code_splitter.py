import pytest
from pheasant.jupyter.markdown import fenced_code_splitter


@pytest.mark.parametrize('source, length, index_markdown', [
    ('```python\nprint(1)\n```', 1, []),
    ('\n```python\nprint(1)\n```', 1, []),
    ('\n```python\nprint(1)\n```\ntext', 2, [1]),
    ('text\n```python\nprint(1)\n```\ntext', 3, [0, 2]),
    ('```python\nprint(1)\n```\n```python\nprint(1)\n```\n', 2, []),
])
def test_fenced_code_splitter(source, length, index_markdown):
    for k, output in enumerate(fenced_code_splitter(source)):
        if k in index_markdown:
            assert isinstance(output, str)
        else:
            assert isinstance(output, tuple)
    assert length == k + 1


@pytest.fixture
def stream():
    yield """
text

```python
print(1)
```

``` python
print(1)
```

text


```python
print(1)
```

~~~
```python
print(1)
```
~~~

text

```python
print(1)
```

~~~
``` python
print(1)
```
~~~


```unknown
abc
```
""".strip()


def test_fenced_code_splitter_stream(stream):
    for k, output in enumerate(fenced_code_splitter(stream)):
        if k in [0, 5]:
            assert output == 'text'
        elif k in [1, 3, 6]:
            assert isinstance(output, tuple)
        elif k == 2:
            assert output == '``` python\nprint(1)\n```\n\ntext'
        elif k == 4:
            assert output.startswith('<div class')
        elif k == 7:
            assert output.startswith('<div class')
        elif k == 8:
            assert output == '```unknown\nabc\n```'
