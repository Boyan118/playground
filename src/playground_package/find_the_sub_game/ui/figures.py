"""Plotly figures for the sub game, shared by the Streamlit page and the notebooks.

Only builds figures: showing them is up to the caller (`st.plotly_chart` on the
page, `fig.show()` in a notebook).
"""

import numpy as np
import plotly.graph_objects as go

# Sequential blue ramp for the heatmaps (light = low, dark = high); markers use
# the next categorical hues so they stand out against it.
HEATMAP_COLORS = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
MOST_LIKELY_COLOR = "#eb6834"
ENTROPY_COLOR = "#1baf7a"
SUB_COLOR = "#eda100"
LAST_PING_COLOR = "#1a1a19"


def map_figure(
        values: np.ndarray,
        value_label: str = "P(sub here)",
        value_format: str = ".1%",
        *,
        show_values: bool | None = None,
        most_likely: tuple[int, int] | None = None,
        entropy_choice: tuple[int, int] | None = None,
        last_ping: tuple[int, int] | None = None,
        last_ping_label: str | None = None,
        sub_location: tuple[int, int] | None = None,
        title: str | None = None) -> go.Figure:
    """Heatmap of `values` (rows × cols), with optional markers.

    Every cell also gets an invisible marker: it carries the hover text, and it
    makes the cells clickable on the Streamlit page (a heatmap itself can't be
    selected). `show_values` writes each value into its cell; by default only
    on boards up to 150 squares, where the text still fits.
    """
    rows, cols = values.shape
    cell_px = min(48, 640 // cols)
    if show_values is None:
        show_values = values.size <= 150

    for location in (most_likely, entropy_choice, last_ping, sub_location):
        if location is not None and not (0 <= location[0] < rows and 0 <= location[1] < cols):
            raise ValueError(f"marker location {location} is outside the {rows} x {cols} map")

    # Row number and column number of every square, as two grids of the map's shape
    r, c = np.indices(values.shape)

    fig = go.Figure(
        go.Heatmap(
            z=values,
            colorscale=HEATMAP_COLORS,
            colorbar={"title": value_label},
            hoverinfo="skip",
            texttemplate=f"%{{z:{value_format}}}" if show_values else None,
        )
    )

    # A scatter trace takes flat lists of points, so ravel() lays each grid out as
    # one long row. The three lists stay aligned: position i is the same square
    # in c, r and values, giving one point per square at (column, row).
    fig.add_scatter(
        x=c.ravel(),
        y=r.ravel(),
        mode="markers",
        marker={"symbol": "square", "size": cell_px, "color": "rgba(0, 0, 0, 0)"},
        customdata=values.ravel(),
        hovertemplate=f"Square (%{{y}}, %{{x}})<br>{value_label}: %{{customdata:{value_format}}}<extra></extra>",
        showlegend=False,
    )

    def add_marker(location, name, symbol, color, size_factor=0.8):
        if location is not None:
            fig.add_scatter(
                x=[location[1]],
                y=[location[0]],
                mode="markers",
                name=name,
                # Open symbols draw their outline in marker.color, at marker.line.width
                marker={"symbol": symbol, "size": cell_px * size_factor, "color": color,
                        "line": {"width": 3}},
                hoverinfo="skip",
            )

    add_marker(most_likely, "Most likely", "circle-open", MOST_LIKELY_COLOR)
    add_marker(entropy_choice, "Entropy", "diamond-open", ENTROPY_COLOR)

    if last_ping is not None:
        # Filled with a white outline, so it shows on light and dark cells alike
        fig.add_scatter(
            x=[last_ping[1]],
            y=[last_ping[0]],
            mode="markers",
            # The label goes in the legend: text on the map would cover the cell's value
            name=f"Last ping: {last_ping_label}" if last_ping_label else "Last ping",
            marker={"symbol": "x", "size": cell_px * 0.45, "color": LAST_PING_COLOR,
                    "line": {"width": 1.5, "color": "white"}},
            hoverinfo="skip",
        )

    if sub_location is not None:
        fig.add_scatter(
            x=[sub_location[1]],
            y=[sub_location[0]],
            mode="markers",
            name="Sub",
            marker={"symbol": "star", "size": cell_px * 0.6, "color": SUB_COLOR,
                    "line": {"width": 1, "color": HEATMAP_COLORS[-1]}},
            hoverinfo="skip",
        )

    # Fixed ranges: the invisible click markers would otherwise pad the axes, and
    # constrain="domain" shrinks the plot area (not the range) to keep cells square.
    # The y range runs from the last row to the first, so row 0 is at the top.
    fig.update_xaxes(title="column", range=[-0.5, cols - 0.5], dtick=1 if cols <= 15 else 2,
                     showgrid=False, zeroline=False, constrain="domain")
    fig.update_yaxes(title="row", range=[rows - 0.5, -0.5], dtick=1 if rows <= 15 else 2,
                     showgrid=False, zeroline=False, scaleanchor="x", constrain="domain")
    fig.update_layout(
        title=title,
        height=rows * cell_px + 160 + (40 if title else 0),
        margin={"l": 10, "r": 10, "t": 50 if title else 10, "b": 10},
        # Below the plot: on top, a one-entry legend looks like a title
        legend={"orientation": "h", "yanchor": "top", "y": -0.12, "x": 0},
        dragmode=False,
    )
    return fig
