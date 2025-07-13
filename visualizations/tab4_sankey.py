import plotly.graph_objects as go
import random
import pandas as pd
import numpy as np
import plotly.colors as pc

def sankey_disaster_deaths_colored(df, country_name):
    # Filter for the country and valid data
    country_df = df[
        (df['Country_x'].str.lower() == country_name.lower()) &
        (df['Total Deaths'].notna()) &
        (df['Total Deaths'] > 0) &
        (df['Disaster Subgroup'].notna()) &
        (df['Disaster Type'].notna())
    ].copy()

    # Group by subgroup → type
    grouped = country_df.groupby(['Disaster Subgroup', 'Disaster Type'])['Total Deaths'].sum().reset_index()

    # Get total deaths per subgroup
    subgroup_totals = grouped.groupby('Disaster Subgroup')['Total Deaths'].sum().reset_index()

    # Unique labels
    subgroups = subgroup_totals['Disaster Subgroup'].tolist()
    types = grouped['Disaster Type'].unique().tolist()
    labels = ['Total Deaths'] + subgroups + types

    label_to_idx = {label: i for i, label in enumerate(labels)}

    # Assign random color per subgroup (can make consistent palette too)
    color_map = {}
    for sg in subgroups:
        color_map[sg] = f'rgba({random.randint(50,220)}, {random.randint(50,200)}, {random.randint(50,200)}, 0.6)'

    node_colors = ['#222222']  # For 'Total Deaths'
    node_colors += [color_map[sg] for sg in subgroups]
    node_colors += [color_map.get(grouped[grouped['Disaster Type'] == dt]['Disaster Subgroup'].values[0], '#999999') for dt in types]

    # Links: Total Deaths → Subgroups
    sources = []
    targets = []
    values = []
    link_colors = []

    for _, row in subgroup_totals.iterrows():
        sources.append(label_to_idx['Total Deaths'])
        targets.append(label_to_idx[row['Disaster Subgroup']])
        values.append(row['Total Deaths'])
        link_colors.append(color_map[row['Disaster Subgroup']])

    # Links: Subgroups → Types
    for _, row in grouped.iterrows():
        sources.append(label_to_idx[row['Disaster Subgroup']])
        targets.append(label_to_idx[row['Disaster Type']])
        values.append(row['Total Deaths'])
        link_colors.append(color_map[row['Disaster Subgroup']])

    # Sankey plot
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])

    fig.update_layout(
        title_text=f"{country_name} — Disaster Subgroup & Type Contribution to Deaths (Colored)",
        font_size=14,
        template='plotly_white'
    )

    return fig

import plotly.graph_objects as go

def sankey_disaster_deaths_multilevel(df, country_name):
    # Filter for the country and valid entries
    country_df = df[
        (df['Country_x'].str.lower() == country_name.lower()) &
        (df['Total Deaths'].notna()) &
        (df['Total Deaths'] > 0) &
        (df['Disaster Subgroup'].notna()) &
        (df['Disaster Type'].notna())
    ].copy()

    # Group by Subgroup → Type
    grouped = country_df.groupby(['Disaster Subgroup', 'Disaster Type'])['Total Deaths'].sum().reset_index()

    # Group by Subgroup (total deaths per subgroup)
    subgroup_totals = grouped.groupby('Disaster Subgroup')['Total Deaths'].sum().reset_index()

    # Unique labels
    subgroups = subgroup_totals['Disaster Subgroup'].tolist()
    types = grouped['Disaster Type'].unique().tolist()

    labels = ['Total Deaths'] + subgroups + types

    # Helper: map label to index
    label_to_idx = {label: idx for idx, label in enumerate(labels)}

    sources = []
    targets = []
    values = []

    # From Total Deaths → Disaster Subgroup
    for _, row in subgroup_totals.iterrows():
        sources.append(label_to_idx['Total Deaths'])
        targets.append(label_to_idx[row['Disaster Subgroup']])
        values.append(row['Total Deaths'])

    # From Disaster Subgroup → Disaster Type
    for _, row in grouped.iterrows():
        sources.append(label_to_idx[row['Disaster Subgroup']])
        targets.append(label_to_idx[row['Disaster Type']])
        values.append(row['Total Deaths'])

    # Sankey Plot
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="lightblue"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(150, 0, 0, 0.4)"
        )
    )])

    fig.update_layout(
        title_text=f"{country_name} — Disaster Subgroup & Type Contribution to Deaths",
        font_size=14,
        template="plotly_white"
    )

    return fig

