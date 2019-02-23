import pytest
from pheasant.markdown.splitter import fenced_code_splitter


@pytest.mark.parametrize('source, length, index_markdown', [
    ('```python\nprint(1)\n```\n', 1, []),
    ('\n```python\nprint(1)\n```\n', 2, [0]),
    ('\n```python\nprint(1)\n```\ntext', 3, [0, 2]),
    ('text\n```python\nprint(1)\n```\ntext', 3, [0, 2]),
    ('```python\nprint(1)\n```\n```python\nprint(1)\n```\n', 2, []),
])
def test_fenced_code_splitter(source, length, index_markdown):
    for k, output in enumerate(fenced_code_splitter(source)):
        print('>>', output, '<<')
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
        print(k, output)
        if k in [0]:
            assert output == 'text\n\n'
        elif k in [6]:
            assert output == '\ntext\n\n'
        elif k in [1, 3, 7]:
            assert isinstance(output, tuple)
        elif k == 2:
            assert output == '\n``` python\nprint(1)\n```\n\ntext\n\n'
        elif k in [5, 9]:
            assert output.startswith('~~~')
        elif k == 10:
            assert output == '\n\n```unknown\nabc\n```'


def test_fenced_code_splitter_pheasant_options():
    source = '```python\n## inline\na = 1\n```\n'
    for output in fenced_code_splitter(source):
        assert output[2] == ['inline']
