from pheasant.markdown.splitter import fenced_code_splitter

source = """start

~~~copy
```python
print('abc')
```
~~~

end
"""


def test_fenced_code_splitter_copy():
    for k, output in enumerate(fenced_code_splitter(source)):
        if k == 0:
            assert output == "start\n\n"
        if k == 1:
            assert output == "~~~\n```python\nprint('abc')\n```\n~~~\n\n"
        if k == 2:
            assert output == ("python", "print('abc')", [])
        if k == 3:
            assert output == "\nend\n"

        output
