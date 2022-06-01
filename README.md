<p align="center">
  <img alt="Wallpanel with homepage"
      src="images/home_page_on_display_transparent.png" width="354">
  </img>
</p>

# Overview
The AmpliPi wallpanel is a in-wall touch interface for controlling an AmpliPi Zone or Group of Zones in your house. It uses the NSPanel by Sonoff with custom controller firmware and display ui. Since it uses the NSPanel the firmware can be loaded on an existing panel by following these [steps](#programming-the-nspanel), preloaded wall panels can be purchased [here](https://www.micro-nova.com/amplipi/store/amplipi-in-wall-wifi-touchscreen-controller-with-integrated-2-device-switch).

## Controller
Built on a micro-python runtime and runs on an ESP32. It can adjust zone and group volumes using AmpliPi's API.

## Button controlled Relays
The two physical buttons can control two LED light circuits, We are planning on exposing these via MQTT in the future.

## Display
The NSPanel uses of a Nextion display for the touch panel display that communicates directly with the controller. The UI has been completely customized for controlling an AmpliPi zone.

## Comms
TODO: talk about serial communication between stm32 and esp32.

## Updates
The panel uses GitHub releases to provide firmware and ui updates. New releases available will be indicated by a red dot on top of the settings icon.

## Programming the NSPanel
TODO: add instructions on how to use the device
