# components.py
from dash import html

from .widgets import *
from visualizations import *



# Topbar
Topbar = html.Div(className="topbar", children=[
    html.Div("My Dashboard", className="topbar-logo"),
    html.Div(className="theme-toggle theme-toggle--dark", id="theme-toggle", children=[
        html.Div(className="theme-toggle__ball")
    ])
])

# Sidebar tabs
tabs = [
    ("overview", "🌍", "Overview & Global Patterns"),
    ("disaster-analysis", "⚡", "Disaster Type Analysis"),
    ("economic-impact", "💰", "Economic Impact & Vulnerability"),
    ("country-profiles", "📊", "Country Risk Profiles"),
    ("trends-correlations", "📈", "Trends & Correlations")
]

SidebarTabs = html.Div(className="sidebar-tabs", children=[
    html.Div(className=f"sidebar-tab {'sidebar-tab--active' if region[0]=='overview' else ''}", 
             **{"data-tab": region[0]}, children=[
        html.Div(region[1], className="icon"),
        html.Span(region[2], className="tab-label")
    ]) for region in tabs
])

# Sidebar
Sidebar = html.Div(id="sidebar", className="sidebar", children=[
    html.Button(id="sidebar-toggle", className="sidebar-toggle", children=[
        html.Span(className="bar"),
        html.Span(className="bar"),
        html.Span(className="bar")
    ]),
    SidebarTabs
])

# Skeleton widget
def SkeletonWidget(style=None):
    return html.Div(
        className="widget widget--skeleton",
        style=style or {},
        children=[
            html.Div(className="skeleton-bar"),
            html.Div(className="skeleton-bar short"),
            html.Div(className="skeleton-circle")
        ]
    )

# Per-region widget layout

def region_widgets(region):
    if region == "overview":
        return [
            SafeVizWidget(get_choropleth_viz,combined_disaster_data_data,{"gridColumn": "1 / 4", "gridRow": "1 / 3"}),
            SafeVizWidget(get_treemap_viz,merged_output_data,{"gridColumn": "1 / 4", "gridRow": "3 / 4"}),
        ]
    elif region == "disaster-analysis":
        return [
            SkeletonWidget({"gridColumn": "1 / 4", "gridRow": "1 / 2", "background": "#b33"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "2 / 3", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "2 / 4", "gridRow": "3 / 4"})
        ]
    elif region == "economic-impact":
        return [
        SafeVizWidget(get_bubble_viz_tab3, tab3_bubble_data,  {"gridColumn": "1 / 4", "gridRow": "4 / 7"}),
            SafeVizWidget(get_area_chart3, tab3_area_data,  {"gridColumn": "1 / 4", "gridRow": "7 / 10"}),
            SafeVizWidget(get_lollipop3, tab3_lolli_data, {"gridColumn": "1 / 4", "gridRow": " 10/ 12"}),
            SafeVizWidget(get_scatter_plot3, tab3_scatter_data, {"gridColumn": "1 / 4", "gridRow": "1 / 4"}),
        ]
    elif region == "country-profiles":
        return [
            SkeletonWidget({"gridColumn": "1 / 4", "gridRow": "1 / 2", "background": "#b33"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "2 / 3", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "3 / 4", "gridRow": "2 / 3"}),
            SkeletonWidget({"gridColumn": "1 / 2", "gridRow": "3 / 4"}),
            SkeletonWidget({"gridColumn": "2 / 4", "gridRow": "3 / 4"})
        ]
    elif region == "trends-correlations":
        return [ 
            SafeVizWidget(get_country_metric_correlation_viz,combined_disaster_data_data,{"gridColumn": "1 / 3", "gridRow": "1 / 2"}),
            SafeVizWidget(get_disaster_network_viz,combined_disaster_data_data,{"gridColumn": "3 / 4", "gridRow": "1 / 2"}),
            SafeVizWidget(get_multi_metric_parallel_viz,combined_disaster_data_data,{"gridColumn": "1 / 4", "gridRow": "3 / 4"}),
            SafeVizWidget(get_rolling_correlation_viz,combined_disaster_data_data, {"gridColumn": "1 / 4", "gridRow": "4 / 5"}),
            SafeVizWidget( get_scatter_matrix_viz,merged_output_data,{"gridColumn": "1 / 4", "gridRow": "5 / 6"}),
        ]
    else:
        return [SkeletonWidget()]

def ContentSection(region):
    return html.Div(
        id=f"content-{region}",
        className="content-section active" if region == "overview" else "content-section",
        children=region_widgets(region)
    )

def GlobeBackground():
    return html.Div(
        id="globe-container",
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "width": "100vw",
            "height": "100vh",
            "zIndex": 0,
            "pointerEvents": "none"
        }
    )