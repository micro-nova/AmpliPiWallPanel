from app import wifi, sysconsts, displayserial
from app.ota.ota_updater import make_ota_updater
from app.pages import version, home, config
from app.utils import compare_versions

def check_for_updates():
    if wifi.is_connected():
        print("checking for updates...")
        has_update = False

        ota = make_ota_updater()

        releases = ota.get_all_releases()
        for r in releases:
            if (not r['prerelease']) and compare_versions(r['tag_name'], sysconsts.VERSION) == 1:
                has_update = True
                print(f'newer update available: {r["tag_name"]}')
                break

        config.set_update_available(has_update)
        if has_update:
            # set settings button to gear with exclamation point
            displayserial.set_component_property(displayserial.HOME_PAGE_NAME, home.CONFIG_BUTTON_OBJNAME, 'pic',
                                                 displayserial.GEAR_W_NOTE_PIC_ID)
            displayserial.set_component_property(displayserial.HOME_PAGE_NAME, home.CONFIG_BUTTON_OBJNAME, 'pic2',
                                                 displayserial.GEAR_W_NOTE_PIC_ID)
        else:
            # set settings button to gear
            displayserial.set_component_property(displayserial.HOME_PAGE_NAME, home.CONFIG_BUTTON_OBJNAME, 'pic',
                                                 displayserial.GEAR_PIC_ID)
            displayserial.set_component_property(displayserial.HOME_PAGE_NAME, home.CONFIG_BUTTON_OBJNAME, 'pic2',
                                                 displayserial.GEAR_PIC_ID)
    else:
        print('failed up check for updates. not connected to wifi')