from __future__ import annotations

import sys
from typing import Any

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 10


def _wait(dash_duo, timeout: float = DEFAULT_TIMEOUT) -> WebDriverWait:
    return WebDriverWait(
        dash_duo.driver,
        timeout,
        poll_frequency=0.05,
        ignored_exceptions=(StaleElementReferenceException,),
    )


def _visible_element(driver, selector: str, enabled: bool = False):
    for element in driver.find_elements(By.CSS_SELECTOR, selector):
        try:
            if not element.is_displayed():
                continue
            if enabled and not element.is_enabled():
                continue
            return element
        except StaleElementReferenceException:
            continue
    return False


def wait_element(
    dash_duo,
    selector: str,
    timeout: float = DEFAULT_TIMEOUT,
    enabled: bool = False,
):
    return _wait(dash_duo, timeout).until(
        lambda driver: _visible_element(driver, selector, enabled=enabled)
    )


def click(
    dash_duo,
    selector: str,
    timeout: float = DEFAULT_TIMEOUT,
):
    wait = _wait(dash_duo, timeout)

    def scroll_current(driver):
        element = _visible_element(driver, selector, enabled=True)
        if not element:
            return False
        try:
            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center',
                    inline: 'center'
                });
                """,
                element,
            )
            return True
        except StaleElementReferenceException:
            return False

    wait.until(scroll_current)

    def click_current(driver):
        element = _visible_element(driver, selector, enabled=True)
        if not element:
            return False
        try:
            element.click()
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException):
            return False

    wait.until(click_current)


def _set_react_value(dash_duo, element, value: Any) -> None:
    dash_duo.driver.execute_script(
        """
        const element = arguments[0];
        const value = String(arguments[1]);

        let prototype;
        if (element.tagName === 'TEXTAREA') {
            prototype = window.HTMLTextAreaElement.prototype;
        } else if (element.tagName === 'SELECT') {
            prototype = window.HTMLSelectElement.prototype;
        } else {
            prototype = window.HTMLInputElement.prototype;
        }

        const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
        descriptor.set.call(element, value);

        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        """,
        element,
        str(value),
    )


def set_value(
    dash_duo,
    selector: str,
    value: Any,
    timeout: float = DEFAULT_TIMEOUT,
    commit: bool = False,
):
    wait = _wait(dash_duo, timeout)
    expected = str(value)

    def set_current(driver):
        element = _visible_element(driver, selector, enabled=True)
        if not element:
            return False

        try:
            _set_react_value(dash_duo, element, expected)
            if commit:
                element.send_keys(Keys.ENTER)
            return True
        except StaleElementReferenceException:
            return False

    wait.until(set_current)

    if commit:
        wait.until(
            lambda driver: (
                (element := _visible_element(driver, selector))
                and element.get_attribute("value") == expected
            )
        )


def pattern_count(dash_duo, **expected: Any) -> int:
    return dash_duo.driver.execute_script(
        """
        const expected = arguments[0];

        return Array.from(document.querySelectorAll('[id^="{"]'))
            .filter(element => {
                try {
                    const id = JSON.parse(element.id);
                    return Object.entries(expected).every(
                        ([key, value]) => id[key] === value
                    );
                } catch (_) {
                    return false;
                }
            })
            .length;
        """,
        expected,
    )


def pattern_elements(dash_duo, **expected: Any):
    return dash_duo.driver.execute_script(
        """
        const expected = arguments[0];

        return Array.from(document.querySelectorAll('[id^="{"]'))
            .filter(element => {
                try {
                    const id = JSON.parse(element.id);
                    return Object.entries(expected).every(
                        ([key, value]) => id[key] === value
                    );
                } catch (_) {
                    return false;
                }
            });
        """,
        expected,
    )


def pattern_element(
    dash_duo,
    timeout: float = DEFAULT_TIMEOUT,
    element_index: int = 0,
    visible: bool = False,
    enabled: bool = False,
    **expected: Any,
):
    def find(_):
        elements = pattern_elements(dash_duo, **expected)
        if not elements:
            return False

        try:
            element = elements[element_index]
            if visible and not element.is_displayed():
                return False
            if enabled and not element.is_enabled():
                return False
            return element
        except (IndexError, StaleElementReferenceException):
            return False

    return _wait(dash_duo, timeout).until(find)


def click_pattern(
    dash_duo,
    timeout: float = DEFAULT_TIMEOUT,
    element_index: int = 0,
    **expected: Any,
):
    wait = _wait(dash_duo, timeout)

    def scroll_current(_):
        elements = pattern_elements(dash_duo, **expected)
        if not elements:
            return False

        try:
            element = elements[element_index]
            if not element.is_displayed() or not element.is_enabled():
                return False
            dash_duo.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                element,
            )
            return True
        except (IndexError, StaleElementReferenceException):
            return False

    wait.until(scroll_current)

    def click_current(_):
        elements = pattern_elements(dash_duo, **expected)
        if not elements:
            return False

        try:
            element = elements[element_index]
            if not element.is_displayed() or not element.is_enabled():
                return False
            element.click()
            return True
        except (
            IndexError,
            StaleElementReferenceException,
            ElementClickInterceptedException,
        ):
            return False

    wait.until(click_current)


def _set_pattern_value_js(dash_duo, value: Any, element_index: int, expected: dict):
    return dash_duo.driver.execute_script(
        """
        const expected = arguments[0];
        const wantedIndex = arguments[1];
        const value = String(arguments[2]);

        const elements = Array.from(document.querySelectorAll('[id^="{"]'))
            .filter(element => {
                try {
                    const id = JSON.parse(element.id);
                    return Object.entries(expected).every(
                        ([key, expectedValue]) => id[key] === expectedValue
                    );
                } catch (_) {
                    return false;
                }
            });

        if (elements.length === 0) {
            return false;
        }

        const index = wantedIndex < 0 ? elements.length + wantedIndex : wantedIndex;
        const element = elements[index];

        if (!element) {
            return false;
        }

        let prototype;
        if (element.tagName === 'TEXTAREA') {
            prototype = window.HTMLTextAreaElement.prototype;
        } else {
            prototype = window.HTMLInputElement.prototype;
        }

        const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
        descriptor.set.call(element, value);

        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));

        return true;
        """,
        expected,
        element_index,
        str(value),
    )


def get_pattern_value(
    dash_duo,
    element_index: int = 0,
    **expected: Any,
) -> str | None:
    return dash_duo.driver.execute_script(
        """
        const expected = arguments[0];
        const wantedIndex = arguments[1];

        const elements = Array.from(document.querySelectorAll('[id^="{"]'))
            .filter(element => {
                try {
                    const id = JSON.parse(element.id);
                    return Object.entries(expected).every(
                        ([key, value]) => id[key] === value
                    );
                } catch (_) {
                    return false;
                }
            });

        if (elements.length === 0) {
            return null;
        }

        const index = wantedIndex < 0 ? elements.length + wantedIndex : wantedIndex;
        return elements[index] ? elements[index].value : null;
        """,
        expected,
        element_index,
    )


def set_pattern_value(
    dash_duo,
    value: Any,
    timeout: float = DEFAULT_TIMEOUT,
    commit: bool = False,
    element_index: int = 0,
    **expected: Any,
):
    wait = _wait(dash_duo, timeout)
    expected_value = str(value)

    wait.until(
        lambda _: _set_pattern_value_js(
            dash_duo,
            expected_value,
            element_index,
            expected,
        )
    )

    if commit:
        def commit_current(_):
            try:
                element = pattern_element(
                    dash_duo,
                    timeout=timeout,
                    element_index=element_index,
                    visible=True,
                    enabled=True,
                    **expected,
                )
                element.send_keys(Keys.ENTER)
                return True
            except StaleElementReferenceException:
                return False

        wait.until(commit_current)

    wait.until(
        lambda _: get_pattern_value(
            dash_duo,
            element_index=element_index,
            **expected,
        ) == expected_value
    )


def set_debounced_pattern_value(
    dash_duo,
    value: Any,
    timeout: float = DEFAULT_TIMEOUT,
    element_index: int = 0,
    **expected: Any,
):
    wait = _wait(dash_duo, timeout)
    expected_value = str(value)

    def enter_current(_):
        try:
            element = pattern_element(
                dash_duo,
                timeout=timeout,
                element_index=element_index,
                visible=True,
                enabled=True,
                **expected,
            )

            element.click()
            element.send_keys(
                Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL,
                "a",
            )
            element.send_keys(expected_value)
            element.send_keys(Keys.ENTER)
            return True
        except StaleElementReferenceException:
            return False

    wait.until(enter_current)
    wait.until(
        lambda _: get_pattern_value(
            dash_duo,
            element_index=element_index,
            **expected,
        ) == expected_value
    )


def click_and_wait_for_pattern(
    dash_duo,
    selector: str,
    timeout: float = DEFAULT_TIMEOUT,
    **expected: Any,
):
    old_count = pattern_count(dash_duo, **expected)
    click(dash_duo, selector, timeout=timeout)
    _wait(dash_duo, timeout).until(
        lambda _: pattern_count(dash_duo, **expected) > old_count
    )


def set_checkbox(
    dash_duo,
    selector: str,
    checked: bool,
    timeout: float = DEFAULT_TIMEOUT,
):
    wait = _wait(dash_duo, timeout)

    def update(driver):
        element = _visible_element(driver, selector, enabled=True)
        if not element:
            return False

        try:
            if element.is_selected() != checked:
                element.click()
            return True
        except StaleElementReferenceException:
            return False

    wait.until(update)
    wait.until(
        lambda driver: (
            (element := _visible_element(driver, selector))
            and element.is_selected() == checked
        )
    )


def toggle_checkbox(
    dash_duo,
    selector: str,
    timeout: float = DEFAULT_TIMEOUT,
):
    wait = _wait(dash_duo, timeout)

    def toggle(driver):
        element = _visible_element(driver, selector, enabled=True)
        if not element:
            return False
        try:
            element.click()
            return True
        except StaleElementReferenceException:
            return False

    wait.until(toggle)


def select_dcc_option(
    pysea,
    selector: str,
    option_text: str,
    timeout: float = DEFAULT_TIMEOUT,
):
    wait = _wait(pysea, timeout)

    def scroll_dropdown(driver):
        dropdown = _visible_element(driver, selector, enabled=True)
        if not dropdown:
            return False
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                dropdown,
            )
            return True
        except StaleElementReferenceException:
            return False

    wait.until(scroll_dropdown)

    def open_dropdown(driver):
        dropdown = _visible_element(driver, selector, enabled=True)
        if not dropdown:
            return False
        try:
            dropdown.click()
            return True
        except (
            StaleElementReferenceException,
            ElementClickInterceptedException,
        ):
            return False

    wait.until(open_dropdown)

    def scroll_matching_option(driver):
        candidates = driver.find_elements(
            By.CSS_SELECTOR,
            ".VirtualizedSelectOption, .Select-option, [role='option']",
        )

        for candidate in candidates:
            try:
                if not candidate.is_displayed():
                    continue
                if candidate.text.strip() != option_text:
                    continue
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'nearest'});",
                    candidate,
                )
                return True
            except StaleElementReferenceException:
                continue
        return False

    wait.until(scroll_matching_option)

    def choose_matching_option(driver):
        candidates = driver.find_elements(
            By.CSS_SELECTOR,
            ".VirtualizedSelectOption, .Select-option, [role='option']",
        )

        for candidate in candidates:
            try:
                if (
                    candidate.is_displayed()
                    and candidate.text.strip() == option_text
                ):
                    candidate.click()
                    return True
            except (
                StaleElementReferenceException,
                ElementClickInterceptedException,
            ):
                continue
        return False

    wait.until(choose_matching_option)


def create_section_and_tasks(
    dash_duo,
    task_count: int,
):
    click(dash_duo, "#b_edit_test")
    wait_element(dash_duo, "#neue-sektion")
    click(dash_duo, "#neue-sektion")
    wait_element(dash_duo, "#neue-aufgabe")

    for _ in range(task_count):
        old_count = pattern_count(
            dash_duo,
            type="b-aufgabe-bearbeiten",
        )
        click(dash_duo, "#neue-aufgabe")
        _wait(dash_duo).until(
            lambda _: pattern_count(
                dash_duo,
                type="b-aufgabe-bearbeiten",
            ) > old_count
        )


def open_task(
    dash_duo,
    index: int,
    timeout: float = DEFAULT_TIMEOUT,
):
    count = pattern_count(dash_duo, type="b-aufgabe-bearbeiten")
    if count <= index:
        raise AssertionError(
            f"Task {index} kann nicht geöffnet werden. Vorhandene Tasks: {count}"
        )

    click_pattern(
        dash_duo,
        timeout=timeout,
        element_index=index,
        type="b-aufgabe-bearbeiten",
    )

    wait_element(
        dash_duo,
        "#b_general",
        timeout=timeout,
        enabled=True,
    )


def load_images(
    pysea,
    media_dir,
    timeout: float = DEFAULT_TIMEOUT,
):
    media_dir = str(media_dir.resolve())
    wait = _wait(pysea, timeout)

    click(pysea, "#load_images", timeout=timeout)
    wait_element(pysea, "#path_images", timeout=timeout, enabled=True)
    set_value(pysea, "#path_images", media_dir, timeout=timeout)

    wait.until(
        lambda driver: (
            (element := _visible_element(driver, "#path_images"))
            and element.get_attribute("value") == media_dir
        )
    )

    click(pysea, "#b_load_images", timeout=timeout)

    def images_loaded(driver):
        for image in driver.find_elements(By.CSS_SELECTOR, "#div_images img"):
            try:
                if image.is_displayed():
                    return True
            except StaleElementReferenceException:
                continue
        return False

    wait.until(images_loaded)


def wait_for_feedback_view(
    dash_duo,
    timeout: float = DEFAULT_TIMEOUT,
):
    def feedback_ready(driver):
        initialize_visible = bool(
            _visible_element(driver, "#initialize_feedback")
        )
        incorrect_exists = (
            pattern_count(dash_duo, type="feedback_incorrect") > 0
        )
        return initialize_visible or incorrect_exists

    _wait(dash_duo, timeout).until(feedback_ready)


def initialize_feedback_if_needed(
    dash_duo,
    timeout: float = DEFAULT_TIMEOUT,
):
    wait_for_feedback_view(dash_duo, timeout=timeout)

    if pattern_count(dash_duo, type="feedback_incorrect") == 0:
        click(dash_duo, "#initialize_feedback", timeout=timeout)
        _wait(dash_duo, timeout).until(
            lambda _: pattern_count(
                dash_duo,
                type="feedback_incorrect",
            ) >= 1
        )

    return pattern_elements(dash_duo, type="feedback_incorrect")
