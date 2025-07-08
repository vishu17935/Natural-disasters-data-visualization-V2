# widgets.py
import pandas as pd, ast
from dash import html, dcc

# Import all visualization functions
from visualizations.viz1 import get_sunburst_viz
from visualizations.viz2 import get_sankey_viz
from visualizations.viz3 import get_bar_viz
from visualizations.viz4 import get_treemap_viz
from visualizations.viz5 import get_stacked_area_viz
from visualizations.viz6 import get_pie_viz
from visualizations.viz7 import get_choropleth_viz

# Load datasets (example: you may need to adjust filenames as needed)
data_gdp = pd.read_csv("/Users/vishalsingh/python/sample/data/processed/india_gdp_data.csv")
data_gdp['path'] = data_gdp['path'].apply(ast.literal_eval)
data_bar = pd.read_csv("/Users/vishalsingh/python/sample/data/processed/india_gdp_bar_data.csv")
data_pie = pd.read_csv("/Users/vishalsingh/python/sample/data/processed/india_gdp_pie_data.csv")
data_treemap = pd.read_csv("/Users/vishalsingh/python/sample/data/processed/india_gdp_treemap_data.csv")
data_treemap['path'] = data_treemap['path'].apply(ast.literal_eval)
data_sankey = pd.read_csv("/Users/vishalsingh/python/sample/data/processed/india_gdp_sankey_data.csv")
data_choropleth = pd.read_csv("/Users/vishalsingh/python/sample/data/processed/mapdata.csv")

# Safe widget wrapper: returns a dcc.Graph or a skeleton on error
def SafeVizWidget(viz_func, data, style=None, **kwargs):
    from .components import SkeletonWidget
    try:
        fig = viz_func(data, **kwargs)
        return html.Div(
            className="widget",
            style=style or {},
            children=[dcc.Graph(figure=fig, config={"displayModeBar": False})]
        )
    except Exception:
        return SkeletonWidget(style)
