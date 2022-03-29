import api


class AudioConfig:
    def __init__(self, zone_id):
        self.zone_id = zone_id
        self.source_id = -1
        self.stream_id = -1
        # calling this will give real values to source_id and stream_id (if it has a stream)
        self.change_zone(zone_id)

    # changes what stream the sources is playing
    def change_stream(self, new_stream_id):
        self.stream_id = new_stream_id
        # make api call to change the source's stream to new_stream_id
        api.set_stream(self.source_id, new_stream_id)

    # changing the zone may also change the source and stream
    def change_zone(self, new_zone_id):
        self.zone_id = new_zone_id

        # get id of source that this new zone belongs to
        zone = api.get_zone_dict(self.zone_id)
        self.source_id = zone['source_id']

        # get the current stream that is running on the source
        self.__update_stream_id_from_source()

    # moves the current zone to a different source
    # this may also change the stream
    def change_source(self, new_source_id):
        self.source_id = new_source_id
        # move zone to new source
        api.move_zone_to_source(self.zone_id, self.source_id)

        # get current stream
        self.__update_stream_id_from_source()

    def __update_stream_id_from_source(self):
        source = api.get_source_dict(self.source_id)
        self.stream_id = api.get_stream_id_from_source_dict(source)


