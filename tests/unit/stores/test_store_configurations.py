import unittest

from backend.stores import StoreConfigurations
from backend.utils.Configurations import AdvancedSettings


class TestAcceptEmptyAsZeroDefault(unittest.TestCase):

    def test_advanced_settings_defaults_to_true(self):
        self.assertTrue(AdvancedSettings().accept_empty_as_zero)

    def test_store_configurations_defaults_to_true(self):
        self.assertTrue(StoreConfigurations().advanced_settings.accept_empty_as_zero)


class TestSetAcceptEmptyAsZero(unittest.TestCase):

    def test_can_disable(self):
        configurations = StoreConfigurations()
        configurations.set_accept_empty_as_zero(False)
        self.assertFalse(configurations.advanced_settings.accept_empty_as_zero)

    def test_can_re_enable(self):
        configurations = StoreConfigurations()
        configurations.set_accept_empty_as_zero(False)
        configurations.set_accept_empty_as_zero(True)
        self.assertTrue(configurations.advanced_settings.accept_empty_as_zero)

    def test_value_is_coerced_to_bool(self):
        configurations = StoreConfigurations()
        configurations.set_accept_empty_as_zero(0)
        self.assertIs(configurations.advanced_settings.accept_empty_as_zero, False)


class TestAdvancedSettingsSerialization(unittest.TestCase):

    def test_to_dict_includes_accept_empty_as_zero(self):
        settings = AdvancedSettings()
        settings.accept_empty_as_zero = False
        self.assertEqual(settings.to_dict()["accept_empty_as_zero"], False)

    def test_from_dict_restores_accept_empty_as_zero(self):
        data = {"navigation_mode": "linear", "keep_responses": True, "accept_empty_as_zero": False}
        settings = AdvancedSettings.from_dict(data)
        self.assertFalse(settings.accept_empty_as_zero)

    def test_from_dict_defaults_to_true_when_missing(self):
        data = {"navigation_mode": "linear", "keep_responses": True}
        settings = AdvancedSettings.from_dict(data)
        self.assertTrue(settings.accept_empty_as_zero)

    def test_round_trip_preserves_value(self):
        settings = AdvancedSettings()
        settings.accept_empty_as_zero = False
        restored = AdvancedSettings.from_dict(settings.to_dict())
        self.assertFalse(restored.accept_empty_as_zero)


class TestStoreConfigurationsSerialization(unittest.TestCase):

    def test_round_trip_through_test_store_preserves_setting(self):
        configurations = StoreConfigurations()
        configurations.set_accept_empty_as_zero(False)

        restored = StoreConfigurations.from_dict(configurations.to_dict())

        self.assertFalse(restored.advanced_settings.accept_empty_as_zero)


if __name__ == "__main__":
    unittest.main()
