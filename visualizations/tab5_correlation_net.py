import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go

def get_disaster_network_viz(
    data: pd.DataFrame,
    country: str = "India",
    metric: str = "Deaths",
    year_start: int = 2000,
    year_end: int = 2015,
    corr_threshold: float = 0.3
) -> go.Figure:
    """
    Generates an interactive correlation network graph between disaster types for a country over a time range.

    Parameters:
    - data (pd.DataFrame): DataFrame containing disaster data.
    - country (str): Country to filter.
    - metric (str): Metric to analyze correlations on (e.g., 'Deaths').
    - year_start (int): Start year for filtering.
    - year_end (int): End year for filtering.
    - corr_threshold (float): Minimum absolute correlation value to draw an edge.

    Returns:
    - go.Figure: Plotly interactive network graph figure.
    """

    # Filter data
    df_filtered = data[
        (data['Country name'] == country) &
        (data['Year'] >= year_start) &
        (data['Year'] <= year_end)
    ]
    if df_filtered.empty:
        raise ValueError("No data available for given filters.")

    # Pivot: aggregate by year and disaster type
    pivot_df = df_filtered.groupby(['Year', 'Disaster Type'])[metric].sum().reset_index()

    # Create wide-form table: years as rows, disaster types as columns
    pivot_wide = pivot_df.pivot(index='Year', columns='Disaster Type', values=metric).fillna(0)

    # Compute correlation matrix across years
    corr = pivot_wide.corr()

    # Build graph
    G = nx.Graph()

    # Add nodes
    for disaster in corr.columns:
        G.add_node(disaster)

    # Add edges based on threshold
    for i in corr.columns:
        for j in corr.columns:
            if i != j:
                weight = corr.loc[i, j]
                if not np.isnan(weight) and abs(weight) >= corr_threshold:
                    G.add_edge(i, j, weight=weight)

    # Layout
    pos = nx.spring_layout(G, seed=42)

    # Nodes
    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='lightgreen',
            size=20,
            line=dict(width=2, color='darkgreen')
        )
    )

    # Edges
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = edge[2]['weight']
        color = '#FF0000' if weight > 0 else '#0000FF'
        width = max(1, abs(weight) * 10)

        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=width, color=color, opacity=0.7),
            hoverinfo='text',
            mode='lines',
            text=[f"{edge[0]} ↔ {edge[1]}<br>Correlation: {weight:.2f}"]
        ))

    # Assemble figure
    fig = go.Figure()

    for et in edge_traces:
        fig.add_trace(et)

    fig.add_trace(node_trace)

    fig.update_layout(
        title=f"Disaster Type Correlation Network<br>{metric} in {country} ({year_start}–{year_end})",
        titlefont_size=18,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    return fig
