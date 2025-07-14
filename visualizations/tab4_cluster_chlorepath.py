import pandas as pd
import numpy as np
import plotly.graph_objects as go

def plot_cluster_choropleth_by_risk(cluster_df, risk_df, risk_columns=None, country_name=None):
    if risk_columns is None:
        risk_columns = ['Exposure', 'Vulnerability', 'Susceptibility',
                        'Coping Capacity', 'Adaptive Capacity', 'World Risk Index']

    # Clean columns
    cluster_df.columns = cluster_df.columns.str.strip()
    risk_df.columns = risk_df.columns.str.strip()
    cluster_df['cluster'] = cluster_df['cluster'].astype(int)

    # Rename for consistency
    risk_df = risk_df.rename(columns={'ISO': 'iso_code', 'Start Year': 'year', 'Country_x': 'country_name'})

    # Merge datasets
    merged = pd.merge(cluster_df, risk_df[['iso_code', 'year'] + risk_columns], on=['iso_code', 'year'], how='left')
    merged['AverageRisk'] = merged[risk_columns].mean(axis=1)

    # Compute cluster-level average risk
    cluster_avg_risk = merged.groupby(['year', 'cluster'])['AverageRisk'].mean().reset_index()
    cluster_avg_risk.rename(columns={'AverageRisk': 'ClusterAverageRisk'}, inplace=True)
    merged = pd.merge(merged, cluster_avg_risk, on=['year', 'cluster'], how='left')

    # Generate hover text
    def build_hover(row):
        hover = f"<b>{row['country_name']}</b><br>Cluster: {row['cluster']}<br>"
        for col in risk_columns:
            hover += f"{col}: {row[col]:.2f}<br>"
        return hover

    merged['hover'] = merged.apply(build_hover, axis=1)

    # Collect years
    years = sorted(merged['year'].unique())
    fig = go.Figure()

    for i, year in enumerate(years):
        df_year = merged[merged['year'] == year]

        if country_name:
            match = df_year[df_year['country_name'].str.lower() == country_name.lower()]
            if match.empty:
                print(f"⚠️ Country '{country_name}' not found for year {year}. Skipping.")
                continue

            target_cluster = match.iloc[0]['cluster']
            cluster_risk = match.iloc[0]['ClusterAverageRisk']
            df_year = df_year[df_year['cluster'] == target_cluster]
            z_values = np.ones(len(df_year))  # all same cluster
            colorscale = [[0, "green"], [1, "green"]]
            showscale = False
            title = f"Countries in the same cluster as '{country_name}' — Year {year} <br><sub>Avg Cluster Risk: {cluster_risk:.2f}</sub>"
        else:
            z_values = df_year['ClusterAverageRisk']
            colorscale = 'Reds'
            showscale = True
            title = f"Cluster Average Risk Map — Year {year}"

        fig.add_trace(go.Choropleth(
            locations=df_year['iso_code'],
            z=z_values,
            locationmode='ISO-3',
            text=df_year['hover'],
            hovertemplate='%{text}<extra></extra>',
            colorscale=colorscale,
            colorbar_title='Avg Cluster Risk' if showscale else None,
            zmin=merged['ClusterAverageRisk'].min() if not country_name else None,
            zmax=merged['ClusterAverageRisk'].max() if not country_name else None,
            marker_line_color='white',
            name=str(year),
            visible=(i == 0),
            showscale=showscale
        ))

    # Create slider steps
    # Precompute average cluster risks for all years and clusters
    avg_risk_map = (
        merged.groupby(['year', 'cluster'])['ClusterAverageRisk']
        .mean()
        .round(2)
        .to_dict()
    )

    # Slider steps
    steps = []
    for i, year in enumerate(years):
        year_df = merged[merged['year'] == year]
        if country_name:
            # Get the target cluster and its average risk
            match = year_df[year_df['country_name'].str.lower() == country_name.lower()]
            if not match.empty:
                cluster_id = match.iloc[0]['cluster']
                avg_risk = avg_risk_map.get((year, cluster_id), "N/A")
                title = f"Avg Risk for {country_name} Cluster (Year {year}): {avg_risk}"
            else:
                title = f"No data for {country_name} in {year}"
        else:
            title = f"Global Cluster Average Risk Map — Year {year}"

        steps.append(dict(
            method="update",
            args=[
                {"visible": [j == i for j in range(len(years))]},
                {"title.text": title}
            ],
            label=str(year)
        ))


    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Year: "},
        pad={"t": 50},
        steps=steps
    )]

    # Layout
    fig.update_layout(
        title=title if country_name else f"Cluster Average Risk Map — Year {years[0]}",
        geo=dict(showframe=False, projection_type='natural earth'),
        sliders=sliders,
        height=600,
        width=1000
    )

    return fig


# plot_cluster_choropleth_by_risk(cluster_df,data, country_name="Australia")
