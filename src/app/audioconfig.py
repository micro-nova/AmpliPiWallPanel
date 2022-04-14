import json

from app import api

_AUDIO_CONFIG_FILENAME = '../zone.txt'


# this is a singleton. all constructed instances refer to the same _instance
class AudioConfig:
    _instance = None
    _initialized = False

    # https://python-patterns.guide/gang-of-four/singleton/
    def __new__(cls):
        if cls._instance is None:
            print("creating AudioConfig object")
            cls._instance = super(AudioConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            print("initializing AudioConfig object")
            self.zone_id = -1
            self.source_id = -1
            self.stream_id = -1

    def load_settings(self):
        print("loading AudioConfig settings")
        self.__load_zone()
        # calling this will give real values to source_id and stream_id (if it has a stream)
        self.change_zone(self.zone_id)

    # def poll_source_and_stream_id(self):
    #     if self.zone_id >= 0:
    #         # get id of source that this new zone belongs to
    #         zone = api.get_zone_dict(self.zone_id)
    #         self.source_id = zone['source_id']
    #
    #         # get the current stream that is running on the source
    #         self.__update_stream_id_from_source()

    # changes what stream the sources is playing
    def change_stream(self, new_stream_id):
        print('changing stream')
        print(f'current zone id is {self.zone_id}')
        print(f'current stream id is {self.stream_id}')
        print(f'new stream id is {new_stream_id}')
        self.stream_id = new_stream_id
        # make api call to change the source's stream to new_stream_id
        api.set_stream(self.source_id, new_stream_id)

    # changing the zone may also change the source and stream
    def change_zone(self, new_zone_id):
        print('changing zone')
        print(f'current zone id is {self.zone_id}')
        print(f'current stream id is {self.stream_id}')
        print(f'new stream id is {new_zone_id}')
        self.zone_id = new_zone_id
        if new_zone_id >= 0:
            # get id of source that this new zone belongs to
            zone = api.get_zone(self.zone_id)
            self.source_id = zone['source_id']

            # get the current stream that is running on the source
            self.__update_stream_id_from_source()
            self.__save_zone()

    # moves the current zone to a different source
    # this may also change the stream
    def change_source(self, new_source_id):
        self.source_id = new_source_id
        # move zone to new source
        api.move_zone_to_source(self.zone_id, self.source_id)

        # get current stream
        self.__update_stream_id_from_source()

    def __load_zone(self):
        try:
            with open(_AUDIO_CONFIG_FILENAME) as zone_file:
                zone_file_str = zone_file.read()
                zone_file_dict = json.loads(zone_file_str)
                self.zone_id = zone_file_dict['zone']
        except OSError:
            # open failed, make file
            self.__save_zone()

    def __save_zone(self):
        zone_file_dict = {'zone': self.zone_id}
        with open(_AUDIO_CONFIG_FILENAME, 'w') as zone_file:
            zone_file_str = json.dumps(zone_file_dict)
            zone_file.write(zone_file_str)

    def __update_stream_id_from_source(self):
        source = api.get_source(self.source_id)
        self.stream_id = api.get_stream_id_from_source_dict(source)
