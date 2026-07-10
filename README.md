FilterMonitor Phase 1 pivot deliverables

What is included
- web/airscape.html
- web/esp32.html
- web/css/app.css
- web/js/api.js
- web/js/airscape.js
- web/js/esp32.js
- include/http_server_manager.h
- src/http_server_manager.cpp (placeholder comment only)

Use these web files
1. Copy the web folder into your project root.
2. Add this to platformio.ini under your env:

board_build.embed_txtfiles =
    web/airscape.html
    web/esp32.html
    web/css/app.css
    web/js/api.js
    web/js/airscape.js
    web/js/esp32.js

3. Update your real src/http_server_manager.cpp to serve:
   /                -> airscape.html
   /airscape.html   -> airscape.html
   /esp32.html      -> esp32.html
   /css/app.css     -> app.css
   /js/api.js       -> api.js
   /js/airscape.js  -> airscape.js
   /js/esp32.js     -> esp32.js

4. Keep your existing JSON API routes:
   /text_sensor/device_name
   /sensor/dp_pa_smoothed
   /number/dp_high_pa
   /binary_sensor/high_static
   /switch/ntfy_enable
   /text/ntfy_topic
   /switch/unit_inwc
   /text_sensor/connected_ssid
   /text_sensor/esphome_version
   /text_sensor/ip_address
   /text_sensor/mac_address
   /binary_sensor/wifi_connected

5. Keep your existing write routes:
   POST /switch/unit_inwc/turn_on
   POST /switch/unit_inwc/turn_off
   POST /number/dp_high_pa/set?value=...
   POST /switch/ntfy_enable/turn_on
   POST /switch/ntfy_enable/turn_off
   POST /text/ntfy_topic/set?value=...

Regular browser testing
- Run a local static server in the web folder and open:
  airscape.html?api=http://filtermonitor-xxxxxx.local
  esp32.html?api=http://filtermonitor-xxxxxx.local

On-device testing
- Browse to:
  http://filtermonitor-xxxxxx.local/
  http://filtermonitor-xxxxxx.local/esp32.html
