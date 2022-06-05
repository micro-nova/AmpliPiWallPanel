<p align="center">
  <img alt="Wallpanel with homepage"
      src="images/home_page_on_display_transparent.png" width="354">
  </img>
</p>

# Overview
The AmpliPi wallpanel is an in-wall touch interface for controlling an AmpliPi Zone or Group of Zones in your house. It uses the [NSPanel by Sonoff](https://sonoff.tech/product/smart-wall-swtich/nspanel) with custom controller firmware and display UI. Since it uses the NSPanel, the firmware can be loaded on an existing panel by following these [steps](#programming-the-nspanel). Preloaded wall panels can be purchased [at the MicroNova web store](https://www.micro-nova.com/amplipi/store/amplipi-in-wall-wifi-touchscreen-controller-with-integrated-2-device-switch).

## Setup
After installation, the wallpanel needs to be connected to the same Wi-Fi that the AmpliPi is connected to. To do this, go to settings, connection, then select an SSID from the drop-down and enter the password. Press connect then return to settings to select a zone or group. Going back to the home page, the device should now be operational. If not, then you may need to specify the AmpliPi's IP manually in the connection settings. 

## Controller
Built on a MicroPython runtime and runs on an ESP32. It can adjust zone and group volumes using AmpliPi's API.

## Button-controlled Relays
The two physical buttons can control two low-powered light circuits, see the [NSPanel specifications](https://sonoff.tech/product/smart-wall-swtich/nspanel) for full details. We are planning on exposing the physical buttons via MQTT in the future.

## Display
The NSPanel uses a Nextion display for the touch panel display that communicates directly with the controller. The UI has been completely customized for controlling an AmpliPi Zone or Group.

## Comms
The ESP32 controls the touch panel by sending and receiving [Nextion instructions](https://nextion.tech/instruction-set/) over UART to the display's STM32.

## Updates
The panel uses GitHub releases to provide firmware and UI updates. New releases available will be indicated by a red dot on top of the settings icon.

## Programming the NSPanel
TODO: add instructions on how to use the device
