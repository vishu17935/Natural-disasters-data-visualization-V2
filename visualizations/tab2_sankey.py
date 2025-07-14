import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.colors as pc

def get_sankey_viz(data: pd.DataFrame,
                   country: str = "World",
                   year_start: int = 1999,
                   year_end: int = 2020,
                   use_log: bool = True) -> go.Figure:
    """
    Generates a Sankey diagram linking disaster types to deaths, damages, and affected.

    Parameters:
    - data (pd.DataFrame): Your disaster dataset.
    - country (str): Filter by country; use 'World' for global.
    - year_start (int): Start year for filtering.
    - year_end (int): End year for filtering.
    - use_log (bool): Whether to apply log scale to values.

    Returns:
    - Plotly Sankey figure.
    """

    try:
        # Rename for easier processing
        data = data.rename(columns={
            "Start Year": "Year",
            "Country_x": "Country name",
            "Total Deaths": "Deaths",
            "Total Damage ('000 US$)": "Damages",
            "Total Affected": "Affected"
        })

        # Filter rows
        df_filtered = data[(data['Year'] >= year_start) & (data['Year'] <= year_end)]
        if country != 'World':
            df_filtered = df_filtered[df_filtered['Country name'] == country]

        # Drop NA from necessary columns
        df_filtered = pd.DataFrame(df_filtered)
        df_filtered = df_filtered.dropna(subset=['Disaster Type', 'Deaths', 'Damages', 'Affected'])

        # Aggregate
        metrics = ['Deaths', 'Damages', 'Affected']
        agg_df = df_filtered.groupby('Disaster Type', as_index=False)[metrics].sum()
        disaster_types = agg_df['Disaster Type'].tolist()

        sources = []
        targets = []
        values = []
        link_colors = []

        palette = pc.qualitative.Plotly
        type_to_color = {dt: palette[i % len(palette)] for i, dt in enumerate(disaster_types)}

        for i, dt in enumerate(disaster_types):
            for j, metric in enumerate(metrics):
                val = agg_df.loc[agg_df['Disaster Type'] == dt, metric].values[0]
                val_scaled = np.log1p(val) if use_log else val

                if val_scaled > 0:
                    sources.append(i)
                    targets.append(len(disaster_types) + j)
                    values.append(val_scaled)
                    link_colors.append(type_to_color[dt])

        # Sankey Plot
        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=disaster_types + metrics,
                color="lightgray"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
                hovertemplate='Source: %{source.label}<br>Target: %{target.label}<br>Value (scaled): %{value:.2f}'
            )
        ))

        fig.update_layout(
            title_text=f"Sankey: Disaster Types → Metrics ({country}, {year_start}-{year_end})",
            font_size=12,
            margin=dict(t=50, l=20, r=20, b=20)
        )

        return fig

    except Exception as e:
        print(f"Error generating Sankey diagram: {e}")
        return go.Figure()
