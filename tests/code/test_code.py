# from pheasant.code import convert
# from pheasant.code.hilite import escaped_code_splitter
# from pheasant.jupyter.converter import initialize
#
#
# def test_convert():
#     initialize()
#     assert convert('abc') == 'abc'
#     content = convert('[pheasant] Pheasant')
#     content
#     assert title == 'Pheasant'
#     assert content.startswith('#begin\n<div class="codehilite pheasant-')
#
#
# def test_code_splitter():
#     splitter = escaped_code_splitter('a\nb')
#     for k, splited in enumerate(splitter):
#         if k == 0:
#             assert splited == 'a\nb'
#     assert k == 0
#
#     splitter = escaped_code_splitter('~~~python\nprint(1)\n~~~\n\nabc')
#     for k, splited in enumerate(splitter):
#         if k == 0:
#             assert splited.startswith('#begin\n<div class="codehilite')
#             assert splited.endswith('</pre></div>\n#end')
#         elif k == 1:
#             assert splited == 'abc'
#     assert k == 1
