# # Script abc de
# ## Test def

import logging
import sys

import altair as alt
import pandas as pd

df = pd.DataFrame([[1, 2, 3], [2, 1, 4]], columns=list("txy"))

chart = (
    alt.Chart(df)
    .mark_line(clip=True)
    .encode(x="t", y=alt.Y("x", scale=alt.Scale(domain=(0, 5))))
)
chart

# -
x = 1
sys.stderr.write("abc\n")
# -
x * 4
logging.error("error")
