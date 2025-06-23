from hue_entertainment_pykit.lowl.enums.log_level_enum import LogLevelEnum
from hue_entertainment_pykit.lowl.low_hepk import LowHepk
from hue_entertainment_pykit.lowl.models.device.device_hue import DeviceHue
from hue_entertainment_pykit.lowl.models.entertainment.entertainment_hue import EntertainmentHue
from hue_entertainment_pykit.lowl.models.entertainment_configuration.entertainment_configuration_request import \
    EntertainmentConfigurationRequest, Metadata, StreamProxy, Locations, ServiceLocationPost, Position
from hue_entertainment_pykit.lowl.models.shared.classes import ResourceReference


def main():
    LowHepk.configure_logs(LogLevelEnum.TRACE)
    bridges = LowHepk.discover_bridges()
    bridge = bridges[0]
    lights = LowHepk.fetch_lights_from_bridge(bridge.ip_address, bridge.api.username)

    light = lights[0]

    device_light: DeviceHue = LowHepk.fetch_device_by_id(bridge.ip_address, bridge.api.username, light.owner.rid)

    services = device_light.services

    entertainment_id = None
    for service in services:
        if service.rtype == 'entertainment':
            entertainment_id = service.rid

    if entertainment_id is None:
        raise Exception('No entertainment service found')


    entertainment: EntertainmentHue = LowHepk.fetch_entertainment_by_id(bridge.ip_address, bridge.api.username,
                                                                 entertainment_id)

    request = EntertainmentConfigurationRequest(type='entertainment_configuration',
                                      metadata=Metadata(name="test_creation_over_python"),
                                      configuration_type='3dspace',
                                      stream_proxy=StreamProxy(mode='auto'),
                                      locations=Locations(service_locations=[
                                          ServiceLocationPost(service=ResourceReference(rid=entertainment.id,
                                                                                        rtype=entertainment.renderer_reference.rtype),
                                                              positions=[Position(x=0.0,
                                                                                  y=0.0,
                                                                                  z=0.0)]
                                                              )
                                      ]))

    ent_conf_id = LowHepk.create_entertainment_configuration(bridge.ip_address,
                                               bridge.api.username,
                                               request)

    LowHepk.delete_entertainment_configuration(bridge.ip_address,
                                               bridge.api.username,
                                               ent_conf_id)

if __name__ == '__main__':
    main()
