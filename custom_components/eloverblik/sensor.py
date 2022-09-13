"""Platform for Eloverblik sensor integration."""
import logging
from datetime import datetime, timedelta
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.helpers.entity import Entity
from pyeloverblik.eloverblik import Eloverblik
from pyeloverblik.models import TimeSeries

_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN



async def async_setup_entry(hass, config, async_add_entities):
    """Set up the sensor platform."""
    eloverblik = hass.data[DOMAIN][config.entry_id]

    sensors = []
    sensors.append(EloverblikEnergy("Eloverblik Energy Total", 'total', eloverblik))
    async_add_entities(sensors)


class EloverblikEnergy(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, sensor_type, client):
        """Initialize the sensor."""
        self._rawdata = None
        self._state = None
        self._data_date = None
        self._data = client
        self._name = name
        self._sensor_type = sensor_type

        self._unique_id = f"{self._data.get_metering_point()}-total"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        attributes = dict()
        attributes['Metering date'] = self._data_date
        attributes['metering_date'] = self._data_date
        attributes['rawdata'] = self._rawdata
        
        return attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ENERGY_KILO_WATT_HOUR

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._data.update()        

        self._data_date = self._data.get_data_date()

        self._state = self._data.get_total_day()
        self._rawdata = []
        for x in range(1, 25):
            hour_start = datetime.fromisoformat("{}T{:02d}:00:00".format(self._data_date, x-1))
            hour_end = hour_start + timedelta(hours=1)
            self._rawdata.append({
                "start": f"{hour_start.isoformat()}",
                "end": f"{hour_end.isoformat()}",
                "value": self._data.get_usage_hour(x)
                })

