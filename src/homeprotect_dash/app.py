from __future__ import annotations

from dash import Dash, Input, Output, State, dcc, html

from homeprotect_dash.config import CONFIG
from homeprotect_dash.data.contracts import StructuredInsights
from homeprotect_dash.data.figures import build_sentiment_figure
from homeprotect_dash.data.loaders import InvalidInsightsError, load_insights, parse_upload
from homeprotect_dash.pages.dashboard import dashboard_layout


def build_app() -> Dash:
    initial_insights = load_insights(CONFIG.insights_path)
    app = Dash(
        __name__,
        title=CONFIG.title,
        assets_folder=str(CONFIG.assets_dir),
        suppress_callback_exceptions=True,
    )

    app.layout = html.Div(
        children=[
            dcc.Store(id="insights-store", data=initial_insights.model_dump(mode="json")),
            html.Div(
                className="toolbar",
                children=[
                    html.Div(
                        children=[
                            html.Div("Structured insights file", className="toolbar__label"),
                            dcc.Upload(
                                id="upload-insights",
                                children=html.Button("Upload JSON", className="upload-button"),
                                accept=".json",
                                multiple=False,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(f"Source: {CONFIG.insights_path.name}", className="toolbar__label"),
                            html.Div(id="upload-status", className="toolbar__status"),
                        ]
                    ),
                ],
            ),
            html.Div(id="dashboard-root"),
        ]
    )

    @app.callback(Output("dashboard-root", "children"), Input("insights-store", "data"))
    def render_dashboard(data: dict[str, object]) -> html.Div:
        insights = StructuredInsights.model_validate(data)
        return dashboard_layout(insights)

    @app.callback(
        Output("insights-store", "data"),
        Output("upload-status", "children"),
        Input("upload-insights", "contents"),
        State("upload-insights", "filename"),
        State("insights-store", "data"),
        prevent_initial_call=True,
    )
    def update_insights(
        contents: str | None, filename: str | None, current_data: dict[str, object]
    ) -> tuple[dict[str, object], str]:
        if contents is None:
            return current_data, "No file uploaded."
        try:
            insights = parse_upload(contents)
        except InvalidInsightsError as exc:
            return current_data, f"Upload failed: {exc}"
        return insights.model_dump(mode="json"), f"Loaded {filename or 'uploaded file'} successfully."

    @app.callback(
        Output("sentiment-figure", "figure"),
        Input("insights-store", "data"),
        Input("sentiment-view-toggle", "value"),
    )
    def update_sentiment_figure(data: dict[str, object], view_mode: str):
        insights = StructuredInsights.model_validate(data)
        return build_sentiment_figure(insights, view_mode)

    return app