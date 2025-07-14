# components.py
from dash import html, dcc

from .widgets import *
from visualizations import *

# --- Radar Chart Box Size Variables ---
RADAR_BOX_WIDTH = "550px"   # Change this to control width
RADAR_BOX_HEIGHT = "550px"  # Change this to control height


# Topbar
Topbar = html.Div(className="topbar", children=[
    html.Div("Natural Disasters Analysis", className="topbar-logo"),
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
            SafeVizWidget(get_choropleth_viz,chloropleth_tab1_data,{"gridColumn": "1 / 4", "gridRow": "1 / 4"}),
            SafeVizWidget(get_treemap_viz,merged_output_data,{"gridColumn": "1 / 4", "gridRow": "3 / 4"}),
        ]
    elif region == "disaster-analysis":
        return [
             html.Div(
                className="widget",
                style={"gridColumn": "2 / 4", "gridRow": "2 / 4"},
                children=[
                    dcc.Graph(
                        id="tab2_bar_chart",
                        config={"displayModeBar": False},
                        clear_on_unhover=True
                    )
                ]
            ),
            # SafeVizWidget(get_choropleth_viz,chloropleth_tab1_data,{"gridColumn": "1 / 4", "gridRow": "1 / 7"}),
            
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
            # Country and Year Selector Bar
            html.Div(
                className="widget widget--selector",
                style={"gridColumn": "1 / 4", "gridRow": "1 / 2", "background": "rgba(52, 152, 219, 0.1)", "border": "1px solid rgba(52, 152, 219, 0.3)"},
                children=[
                    html.Div(
                        className="selector-container",
                        style={"display": "flex", "gap": "20px", "alignItems": "center", "padding": "16px"},
                        children=[
                            html.Div(
                                style={"display": "flex", "flexDirection": "column", "gap": "8px"},
                                children=[
                                    html.Label("Select Country:", style={"color": "white", "fontWeight": "bold", "fontSize": "14px"}),
                                    dcc.Dropdown(
                                        id="country-selector",
                                        placeholder="Choose a country...",
                                        style={"backgroundColor": "rgba(255, 255, 255, 0.1)", "color": "white", "border": "1px solid rgba(52, 152, 219, 0.5)"},
                                        className="selector-dropdown"
                                    )
                                ]
                            ),
                            html.Div(
                                style={"display": "flex", "flexDirection": "column", "gap": "8px"},
                                children=[
                                    html.Label("Select Year:", style={"color": "white", "fontWeight": "bold", "fontSize": "14px"}),
                                    dcc.Dropdown(
                                        id="year-selector",
                                        options=[],  # Options will be set by callback
                                        placeholder="Choose a year...",
                                        style={"backgroundColor": "rgba(255, 255, 255, 0.1)", "color": "white", "border": "1px solid rgba(52, 152, 219, 0.5)"},
                                        className="selector-dropdown"
                                    )
                                ]
                            ),
                            # html.Div(
                            #     style={"display": "flex", "flexDirection": "column", "gap": "8px"},
                            #     children=[
                            #         html.Label("Analysis Type:", style={"color": "white", "fontWeight": "bold", "fontSize": "14px"}),
                            #         dcc.Dropdown(
                            #             id="analysis-type-selector",
                            #             options=[
                            #                 {"label": "Risk Profile", "value": "risk"},
                            #                 {"label": "Disaster Summary", "value": "disaster"},
                            #                 {"label": "Economic Impact", "value": "economic"},
                            #                 {"label": "Vulnerability Analysis", "value": "vulnerability"}
                            #             ],
                            #             value="risk",
                            #             style={"backgroundColor": "rgba(255, 255, 255, 0.1)", "color": "white", "border": "1px solid rgba(52, 152, 219, 0.5)"},
                            #             className="selector-dropdown"
                            #         )
                            #     ]
                            # ),
                            html.Div(
                                style={"display": "flex", "flexDirection": "column", "gap": "8px"},
                                children=[
                                    html.Label("Map Style:", style={"color": "white", "fontWeight": "bold", "fontSize": "14px"}),
                                    dcc.Dropdown(
                                        id="map-style-selector",
                                        options=[
                                            {"label": "Open Street Map", "value": "open-street-map"},
                                            {"label": "Carto Positron", "value": "carto-positron"},
                                            {"label": "Carto Dark Matter", "value": "carto-darkmatter"},
                                            {"label": "Stamen Terrain", "value": "stamen-terrain"},
                                            {"label": "Stamen Toner", "value": "stamen-toner"}
                                        ],
                                        value="open-street-map",
                                        style={"backgroundColor": "rgba(255, 255, 255, 0.1)", "color": "white", "border": "1px solid rgba(52, 152, 219, 0.5)"},
                                        className="selector-dropdown"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
             
            # Metrics Card
            html.Div(
                className="widget widget--metrics",
                style={"gridColumn": "1 / 2", "gridRow": "2 / 4", "background": "rgba(255, 107, 107, 0.1)", "border": "1px solid rgba(255, 107, 107, 0.3)", "height": "100%"},
                                children=[
                    # Hidden store to track click state
                    dcc.Store(id="click-state", data={"show_disaster": False}),
                    html.Div(
                        id="metrics-card",
                        style={"padding": "20px", "height": "100%", "overflowY": "auto", "position": "relative"}
                    ),
                    # Small reset button in top right corner
                    html.Button(
                        "↺",
                        id="reset-metrics-btn",
                        style={
                            "position": "absolute",
                            "top": "10px",
                            "right": "10px",
                            "backgroundColor": "rgba(255,255,255,0.1)",
                            "color": "white",
                            "border": "1px solid rgba(255,255,255,0.3)",
                            "borderRadius": "50%",
                            "width": "30px",
                            "height": "30px",
                            "cursor": "pointer",
                            "fontSize": "16px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "zIndex": "10"
                        }
                    )
                ]
            ),
            # Region Hotspot Map (replacing spider chart in first row)
            html.Div(
                className="widget",
                style={"gridColumn": "2 / 4", "gridRow": "2 / 4"},
                children=[
                    dcc.Graph(
                        id="region-hotspot-map",
                        config={"displayModeBar": False},
                        clear_on_unhover=True
                    )
                ]
            ),
            # Risk Profile Radar Chart (moved to second row)
            html.Div(
                className="widget",
                style={
                    "gridColumn": "1 / 2", "gridRow": "4 / 5",
                    "width": RADAR_BOX_WIDTH,
                    "height": RADAR_BOX_HEIGHT,
                    "minWidth": RADAR_BOX_WIDTH,
                    "minHeight": RADAR_BOX_HEIGHT,
                    "maxWidth": RADAR_BOX_WIDTH,
                    "maxHeight": RADAR_BOX_HEIGHT,
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "stretch",
                    "justifyContent": "flex-start",
                    "background": "transparent"
                },
                children=[
                    html.Div(
                        style={"marginBottom": "8px"},
                        children=[
                            html.Label("Compare Countries:", style={"color": "white", "fontWeight": "bold", "fontSize": "14px"}),
                            dcc.Dropdown(
                                id="multi-country-selector",
                                multi=True,
                                placeholder="Add countries for comparison...",
                                style={"backgroundColor": "rgba(255,255,255,0.1)", "color": "white", "border": "1px solid #3498db"},
                                className="selector-dropdown"
                            ),
                        ]
                    ),
                    dcc.Graph(
                        id="country-risk-radar",
                        config={"displayModeBar": False},
                        style={
                            "height": "500px",
                            "width": RADAR_BOX_WIDTH,
                            "backgroundColor": "transparent"
                        }
                    )
                ]
            ),
            # # Disaster Type Distribution Pie Chart
            # html.Div(
            #     className="widget",
            #     style={"gridColumn": "2 / 3", "gridRow": "4 / 5"},
            #     children=[
            #         dcc.Graph(
            #             id="disaster-pie-chart",
            #             config={"displayModeBar": False}
            #         )
            #     ]
            # ),
            # Economic Impact Bubble Chart
            html.Div(
                className="widget",
                style={"gridColumn": "2 / 3", "gridRow": "4 / 5", "marginLeft": "150px", "height": "500px", "width": "700px"} ,
                # style={},
                children=[
                html.H3(id="cluster-chlorepath-title", style={"textAlign": "center", "color": "white", "fontSize": "18px", "fontWeight": "bold"}),
                html.H5("Use the slider to see other countries with similar risk profile for different years", style={"textAlign": "center", "color": "white", "fontSize": "14px", "fontWeight": "bold", "marginTop": "2px", "marginBottom": "2px"}),
                    dcc.Graph(
                        id="economic-bubble-chart",
                        config={"displayModeBar": False}
                    )
                ]
            ),
            html.Div(
    className="widget",
    style={"gridColumn": "1 / 2", "gridRow": "6 / 7", "height": "600px", "width": "1200px", "marginTop": "500px"},
    children=[
        # Title + Dropdown Wrapper
        html.Div(
            style={
                "width": "1200px",
                "margin": "0 auto",
                "marginBottom": "12px",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between"
            },
            children=[
                # Title will be updated via callback
                html.H3(
                    id="parallel-plot-title",
                    children="Parallel Coordinates Plot",
                    style={
                        "color": "white",
                        "margin": "0",
                        "fontSize": "18px",
                        "fontWeight": "bold"
                    }
                ),
                html.Div(
                    style={"display": "flex", "alignItems": "center", "gap": "12px"},
                    children=[
                        html.Label("Type:", style={"color": "white", "fontWeight": "bold", "fontSize": "14px"}),
                        dcc.Dropdown(
                            id="parallel-plot-type-selector",
                            options=[
                                {"label": "Risk vs Outcome", "value": "risk_vs_outcome"},
                                {"label": "Wealth vs Impact", "value": "wealth_vs_impact"},
                                {"label": "Vulnerability Path", "value": "vulnerability_path"}
                            ],
                            value="risk_vs_outcome",
                            clearable=False,
                            style={
        "backgroundColor": "#222",   # dark background
        "color": "black",            # white text
        "width": "260px",
        # "border": "1px solid #444"
    }
                            # style={
                            #     "backgroundColor": "rgba(255,255,255,0.1)",
                            #     "color": "white",
                            #     "width": "260px"
                            # }
                        )
                    ]
                )
            ]
        ),
        html.Div(
            style={"width": "1200px", "margin": "0 auto"},
            children=dcc.Graph(
                id="tab4-parallel-plot",
                config={"displayModeBar": False},
                style={
                    "height": "500px",
                    "width": "100%",
                    "backgroundColor": "transparent"
                }
            )
        )
    ],
    )
    ,
    html.Div(
        className="widget",
        style={"gridColumn": "1 / 2", "gridRow": "9 / 10", "height": "500px", "width": "500px", "marginTop": "200px"},
        children=[
            html.Img(id="wordcloud-img", style={"width": "500px", "height": "300px"})
        ]
)



,
            # # Vulnerability Metrics Bar Chart (right)
            # html.Div(
            #     className="widget",
            #     style={"gridColumn": "2 / 3", "gridRow": "5 / 6"},
            #     children=[
            #         dcc.Graph(
            #             id="vulnerability-radar",
            #             config={"displayModeBar": False}
            #         )
            #     ]
            # )
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