<p align="center">
  <img alt="Wallpanel with homepage"
      src="images/home_page_on_display_transparent.png" width="354">
  </img>
</p>

Building on top of the powerful NSPanel hardware by Sonoff, we have added our own custom, open-source software to create a beautiful, wall-mountable interface for your AmpliPi system. The wall panel controller can be used to quickly mute, adjust the volume, select streaming sources, and control the currently playing stream for a specific zone or group in your AmpliPi system. The panel mounts in a standard single gang box and can be powered by AC 100-240V. It uses your existing Wi-Fi network to communicate with the main AmpliPi controller, so no additional wiring needs to be run. The panel has 2 physical buttons connected to relays that can be used to control two AC devices, such as lights in a room. You can add as many panels as you’d like to control your AmpliPi system!

Sonoff's NSPanel makes use of a Nextion display. These displays have their own stm32 for handling GUI related tasks, like rendering and handling touch response. This display connects to an esp32 in the Sonoff panel which acts as the "backend" for the device. Another way of looking at it is the display+stm32 would be the "view" and the esp32 would be the "model" in the model-view-controller design pattern. Nextion also provides a scripting language that can be used for building more complex GUI logic, so it doesn't quite fit into the MVC design pattern since some simpler GUI things don't need to go to the backend, like slider animation or page changes for example.

TODO: talk about serial communication between stm32 and esp32. talk about display updates, OTA updates

TODO: add basic instructions on how to use the device

