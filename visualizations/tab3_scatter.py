import re
import pandas as pd
import plotly.graph_objects as go

def get_scatter_plot3(df):
    # === Preprocess ===
    df["Year"] = df["Year"].astype(int)
    df = df.sort_values("Year")
    df = df[df["GDP_loss_percent"] > 0]

    # Optional downsampling (disable if not needed)
    years = sorted(df["Year"].unique())
    # years = years[::2]  # Uncomment to skip every other year

    continents = sorted(df["Continent"].dropna().unique())
    continents.insert(0, "All")

    # === Helper: Scatter Trace Generator ===
    def get_scatter_trace(data):
        return go.Scatter(
            x=data["GDP_per_capita"],
            y=data["GDP_loss_percent"],
            mode="markers",
            marker=dict(size=8, opacity=0.5),
            text=data["Country"],
            hoverinfo="text+x+y"
        )

    # === Initial Plot ===
    initial_data = df[df["Year"] == years[0]]
    fig = go.Figure(data=[get_scatter_trace(initial_data)])

    # === Frames for All Continents ===
    fig.frames = [
        go.Frame(
            data=[get_scatter_trace(df[df["Year"] == year])],
            name=f"All_{year}"
        )
        for year in years
    ]

    # === Year Slider Steps ===
    slider_steps = [
        {
            "args": [[f"All_{year}"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
            "label": str(year),
            "method": "animate"
        }
        for year in years
    ]
    y_max = df["GDP_loss_percent"].quantile(0.95)

    # === Layout and Controls ===
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 0.5)',  # outer background
        plot_bgcolor='rgba(255, 255, 255, 0.5)',   # plotting area background
        title="GDP Loss (% of GDP) vs GDP per Capita Over Time",
        title_x=0.5,
        autosize=True,  # ✅ NEW: Helps layout scale responsively
        margin=dict(l=80, r=80, t=120, b=120),  # ✅ NEW: More breathing space
        xaxis=dict(title="GDP per Capita (USD)", type="log"),
        yaxis=dict(title="GDP Loss (% of GDP)", range=[-0.5, y_max]),
        updatemenus=[
            # === Continent Dropdown ===
            dict(
                buttons=[
                    dict(
                        label=cont,
                        method="update",
                        args=[
                            [],
                            {
                                "frames": [
                                    go.Frame(
                                        data=[get_scatter_trace(
                                            df[
                                                (df["Year"] == year) if cont == "All" else
                                                ((df["Year"] == year) & (df["Continent"] == cont))
                                            ]
                                        )],
                                        name=f"{cont}_{year}"
                                    )
                                    for year in years
                                ],
                                "transition": {"duration": 0}
                            }
                        ]
                    )
                    for cont in continents
                ],
                direction="down",
                showactive=True,
                x=0.1,
y=1.2,
xanchor="left",
yanchor="top"

            ),
            # === Play / Pause Buttons ===
            dict(
                type="buttons",
                showactive=True,
                direction="right",
                x=1,
y=1.25,
xanchor="right",
yanchor="top",

                pad={"r": 10, "t": 10},
                buttons=[
                    dict(
                        label="▶️ Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 1000, "redraw": True},  # ✅ SLOWER frames
                                "fromcurrent": True,
                                "mode": "immediate",
                                "transition": {"duration": 800, "easing": "linear"}  # ✅ SMOOTHER motion
                            }
                        ]
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            [None],  # ✅ FIXED: Use [None], not None
                            {
                                "mode": "immediate",
                                "frame": {"duration": 0, "redraw": False},
                                "transition": {"duration": 0}
                            }
                        ]
                    )
                ]
            )
        ],
        sliders=[{
            "active": 0,
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "y": -0.47,
"yanchor": "bottom",
"x": 0.5,
"xanchor": "center",

            "currentvalue": {
                "font": {"size": 16},
                "prefix": "Year: ",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 800, "easing": "cubic-in-out"},
            "steps": slider_steps
        }]
    )

    return fig

# === Load and Call Function ===
if __name__ == "__main__":
    file_path = "/Users/vishalsingh/python/sample/data/processed/tab3_scatter.csv"
    df = pd.read_csv(file_path)
    get_scatter_plot3(df)
