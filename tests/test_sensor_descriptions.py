"""Tests for sensor value accessors and descriptions."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfPower

from custom_components.solar_plus_intelbras.sensor_descriptions import (
    INVERTER_SENSORS,
    PLANT_SENSORS,
)


def _by_key(descriptions, key):  # noqa: ANN001, ANN202
    return next(d for d in descriptions if d.key == key)


def test_current_power_is_power_in_watts(coordinator_data: dict) -> None:
    """current_power is a POWER sensor in Watts reading plant.metrics.currentPower."""
    desc = _by_key(PLANT_SENSORS, "current_power")
    assert desc.device_class == SensorDeviceClass.POWER
    assert desc.native_unit_of_measurement == UnitOfPower.WATT
    assert desc.value_fn(coordinator_data) == 4993  # noqa: PLR2004


def test_economy_of_last_30_uses_correct_key(coordinator_data: dict) -> None:
    """economy_of_last_30 reads economyOfLast30, not todayEconomy."""
    desc = _by_key(PLANT_SENSORS, "economy_of_last_30")
    assert desc.value_fn(coordinator_data) == 317.124  # noqa: PLR2004


def test_year_energy_reads_from_records(coordinator_data: dict) -> None:
    """year_energy reads the coordinator's year_energy value."""
    desc = _by_key(PLANT_SENSORS, "year_energy")
    assert desc.value_fn(coordinator_data) == 292.4  # noqa: PLR2004


def test_saved_co2_has_no_invalid_device_class(coordinator_data: dict) -> None:
    """saved_co2 has no device_class and is reported in kg."""
    desc = _by_key(PLANT_SENSORS, "saved_co2")
    assert desc.device_class is None
    assert desc.native_unit_of_measurement == "kg"
    assert desc.value_fn(coordinator_data) == 117.643  # noqa: PLR2004


def test_inverter_temperature(coordinator_data: dict) -> None:
    """inverter_temperature is a TEMPERATURE sensor reading the row temperature."""
    row = coordinator_data["inverters"]["rows"][0]
    desc = _by_key(INVERTER_SENSORS, "inverter_temperature")
    assert desc.device_class == SensorDeviceClass.TEMPERATURE
    assert desc.value_fn(row) == 40  # noqa: PLR2004


def test_weather_sensors_read_plant_weather(coordinator_data: dict) -> None:
    """Weather sensors read plant.weather.current."""
    assert _by_key(PLANT_SENSORS, "weather_temperature").value_fn(coordinator_data) == 31.4  # noqa: PLR2004
    assert _by_key(PLANT_SENSORS, "weather_humidity").value_fn(coordinator_data) == 63  # noqa: PLR2004
    assert _by_key(PLANT_SENSORS, "weather_condition").value_fn(coordinator_data) == "Partly cloudy"


def test_mppt_power_sensors_read_module_parameters() -> None:
    from custom_components.solar_plus_intelbras.sensor_descriptions import MPPT_SENSORS, mppt_indexes

    row = {"parameters": {"module_1": "121.60", "module_2": 125, "module_3": "", "dev_code": 1}}
    assert mppt_indexes(row) == [1, 2, 3]
    assert MPPT_SENSORS[1].value_fn(row) == 121.6
    assert MPPT_SENSORS[2].value_fn(row) == 125.0
    assert MPPT_SENSORS[3].value_fn(row) is None
    assert mppt_indexes({}) == []
    assert mppt_indexes({"parameters": None}) == []
