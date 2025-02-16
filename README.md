# Cover Time-based Component

Forked from [@duhow](https://github.com/duhow/hass-cover-time-based) @ 2024,
this custom component now integrates easily in Home Assistant.

Convert your (dummy) `switch` into a `cover`, and allow to control its position.

Additionally, if you interact with your physical switch, the position status will be updated as well.

**Optional:** If your cover uses a third button for stopping, you can also add it (normally your cover will stop once the up/down switch is turned off).

**Optional:** If needed you can set the slats_opening_time and slats_closing_time to adjust the time it takes to open/close the slats.

**Experimental:** You can add `scripts` to enable custom action (eg. MQTT calls), for easy integration with other hardware.

## Install

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mikipal7&repository=hass-cover-time-based&category=integration)

## Usage

[![Open your Home Assistant instance and show your helper entities.](https://my.home-assistant.io/badges/helpers.svg)](https://my.home-assistant.io/redirect/helpers/)

Add a Helper to **Change device type to a Cover time-based**.

## Credits

* [@davidramosweb](https://github.com/davidramosweb) for its original code base.
* [@kotborealis](https://github.com/kotborealis/home-assistant-custom-components-cover-time-based-synced) for another fork implementing synced status.
* [xknx](https://xknx.io/) Python library for the `TravelCalculator` control class.
