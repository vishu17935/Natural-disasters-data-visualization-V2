# widgets.py
import pandas as pd, ast
from dash import html, dcc

# Import all visualization functions
from visualizations import *

# Load datasets (example: you may need to adjust filenames as needed)
from pathlib import Path
from utils.data_loader import load_all_csvs

data_dir = Path(__file__).resolve().parents[1] / "data" / "processed"
data_vars = load_all_csvs(data_dir)

globals().update(data_vars)


# Safe widget wrapper: returns a dcc.Graph or a skeleton on error
def SafeVizWidget(viz_func, data, style=None, **kwargs):
    from .components import SkeletonWidget
    try:
        fig = viz_func(data, **kwargs)
        return html.Div(
            className="widget",
            style=style or {},
            children=[dcc.Graph(
    figure=fig,
    config={"displayModeBar": False},
    style={"height": "100%", "width": "100%"}
)
]
        )
    except Exception:
        return SkeletonWidget(style)
