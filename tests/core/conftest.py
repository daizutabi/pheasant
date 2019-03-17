# import pytest
#
# from pheasant import Converter, Jupyter, Linker, Number
#
#
# @pytest.fixture()
# def converter():
#     converter = Converter()
#     converter.register("preprocess", [Jupyter(), Number()])
#     converter.register("postprocess", Linker())
#     return converter
