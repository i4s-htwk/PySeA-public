from __future__ import annotations

import importlib
import os
from collections.abc import Generator

import pytest
from dash import Dash
from selenium.webdriver.common.by import By


def _load_dash_app() -> Dash:
    """
    Lädt die Dash-App.

    Über PYSEA_DASH_APP kann der Einstiegspunkt angepasst werden:

        app:app
        frontend.app:app
        frontend.app:create_app
    """

    target = os.environ.get(
        "PYSEA_DASH_APP",
        "app:app",
    )

    module_name, attribute_name = target.split(
        ":",
        1,
    )

    module = importlib.import_module(
        module_name
    )

    value = getattr(
        module,
        attribute_name,
    )

    if callable(value) and not isinstance(value, Dash):
        app = value()
    else:
        app = value

    if not isinstance(app, Dash):
        raise TypeError(
            f"{target!r} liefert keine dash.Dash-App, "
            f"sondern {type(app)!r}"
        )

    return app


@pytest.fixture
def dash_app(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> Dash:
    """
    Neue Dash-App für den Integrationstest.

    Wichtig:
    Das Working Directory wird NICHT auf tmp_path geändert,
    da PySeA relative Pfade zu Testdaten verwendet.
    """

    monkeypatch.setenv(
        "PYSEA_TEST_MODE",
        "1",
    )

    monkeypatch.setenv(
        "PYSEA_OUTPUT_DIR",
        str(tmp_path),
    )

    app = _load_dash_app()

    app.server.config.update(
        TESTING=True,
        PROPAGATE_EXCEPTIONS=True,
    )

    return app


@pytest.fixture
def pysea(
    dash_duo,
    dash_app,
) -> Generator:
    """
    Startet den echten Dash-Server und Browser.

    Nach jedem Test werden sämtliche aufgezeichneten
    Browser- und Callbackfehler geprüft.
    """

    dash_duo.start_server(
        dash_app
    )

    dash_duo.wait_for_element(
        "#b_edit_test",
        timeout=10,
    )

    _install_callback_error_probe(
        dash_duo
    )

    yield dash_duo

    assert_no_frontend_errors(
        dash_duo
    )


def _install_callback_error_probe(
    dash_duo,
) -> None:
    """
    Zeichnet fehlgeschlagene Dash POST-Callbacks während des
    gesamten Tests auf.
    """

    dash_duo.driver.execute_script(
        """
        window.__pyseaCallbackErrors = [];

        if (!window.__pyseaFetchPatched) {

            const originalFetch = window.fetch;

            window.fetch = async function (...args) {

                try {

                    const response =
                        await originalFetch.apply(
                            this,
                            args
                        );

                    const url =
                        String(args[0]);

                    if (
                        url.includes(
                            '_dash-update-component'
                        )
                        &&
                        !response.ok
                    ) {

                        let body = '';

                        try {
                            body =
                                await response
                                    .clone()
                                    .text();
                        } catch (_) {}

                        window.__pyseaCallbackErrors.push({
                            url: url,
                            status: response.status,
                            body: body
                        });
                    }

                    return response;

                } catch (error) {

                    window.__pyseaCallbackErrors.push({
                        url: String(args[0]),
                        status: null,
                        body: String(error)
                    });

                    throw error;
                }
            };

            window.__pyseaFetchPatched = true;
        }
        """
    )


def assert_no_frontend_errors(
    dash_duo,
) -> None:
    """
    Der Test schlägt fehl bei:

      * JavaScript-/Browserfehlern
      * fehlgeschlagenen Dash-Callbacks
      * sichtbaren Dash-Fehlerdialogen
      * Fehlerhinweisen im DOM
    """

    errors: list[str] = []

    # --------------------------------------------------------------
    # Browser / JavaScript errors
    # --------------------------------------------------------------

    for entry in dash_duo.get_logs():
        level = str(
            entry.get(
                "level",
                "",
            )
        ).upper()

        message = str(
            entry.get(
                "message",
                "",
            )
        )

        if level in {
            "SEVERE",
            "ERROR",
        }:
            errors.append(
                "Browserfehler:\n"
                f"{message}"
            )

    # --------------------------------------------------------------
    # Dash callback HTTP errors
    # --------------------------------------------------------------

    callback_errors = (
        dash_duo.driver.execute_script(
            """
            return window.__pyseaCallbackErrors || [];
            """
        )
    )

    for error in callback_errors:
        errors.append(
            "Dash-Callback fehlgeschlagen:\n"
            f"Status: {error.get('status')}\n"
            f"URL: {error.get('url')}\n"
            f"{error.get('body', '')[:2000]}"
        )

    # --------------------------------------------------------------
    # Dash error overlay
    # --------------------------------------------------------------

    error_selectors = (
        ".dash-error-card",
        ".dash-fe-error__info",
        ".dash-fe-error__title",
        ".dash-fe-error__detail",
    )

    for selector in error_selectors:
        elements = (
            dash_duo.driver.find_elements(
                By.CSS_SELECTOR,
                selector,
            )
        )

        for element in elements:
            if (
                element.is_displayed()
                and element.text.strip()
            ):
                errors.append(
                    "Dash-Fehleranzeige:\n"
                    f"{element.text.strip()}"
                )

    # --------------------------------------------------------------
    # Fehlertexte im Dokument
    # --------------------------------------------------------------

    body = dash_duo.driver.find_element(
        By.TAG_NAME,
        "body",
    ).text

    markers = (
        "Callback error updating",
        "Callback failed",
        "Internal Server Error",
        "Traceback (most recent call last)",
    )

    for marker in markers:
        if marker in body:
            errors.append(
                f"Fehlermarker im DOM: {marker}"
            )

    assert not errors, "\n\n".join(errors)