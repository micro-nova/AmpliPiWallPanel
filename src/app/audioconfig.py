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
            self.group_id = -1
            self.using_group = False
            self.supported_cmds = []

    def load_settings(self) -> bool:
        print("loading AudioConfig settings")
        self.__load_info()
        # calling change_group or change_zone will give real values to source_id and stream_id (if it has a stream)
        if self.using_group:
            return self.change_group(self.group_id)
        return self.change_zone(self.zone_id)

    # changes what stream the source is playing
    def change_stream(self, new_stream_id):
        print('changing stream')
        print(f'current zone id is {self.zone_id}')
        print(f'current stream id is {self.stream_id}')
        print(f'new stream id is {new_stream_id}')
        self.stream_id = new_stream_id
        # make api call to change the source's stream to new_stream_id
        api.set_stream(self.source_id, new_stream_id)
        self.__update_supported_cmds_from_source(api.get_source(self.source_id))

    # changing the zone may also change the source and stream
    def change_zone(self, new_zone_id) -> bool:
        self.using_group = False
        print('changing zone')
        print(f'current zone id is {self.zone_id}')
        print(f'current stream id is {self.stream_id}')
        print(f'new zone id is {new_zone_id}')
        self.zone_id = new_zone_id
        if new_zone_id >= 0:
            # get id of source that this new zone belongs to
            zone = api.get_zone(self.zone_id)
            if zone is None:
                return False
            self.source_id = zone['source_id']

            # get the current stream that is running on the source
            source = api.get_source(self.source_id)
            self.__update_stream_id_from_source(source)
            self.__update_supported_cmds_from_source(source)
            self.__save_info()
        return True

    def change_group(self, new_group_id) -> bool:
        self.using_group = True
        print('changing group')
        print(f'current group is {self.group_id}')
        print(f'current stream id is {self.stream_id}')
        print(f'new group id is {new_group_id}')
        self.group_id = new_group_id
        if new_group_id >= 0:
            # get id of source that this new group belongs to
            group = api.get_group(self.group_id)
            if group is None:
                return False
            try:
                self.source_id = group['source_id']
            except Exception:
                pass

            # get the current stream that is running on the source
            source = api.get_source(self.source_id)
            self.__update_stream_id_from_source(source)
            self.__update_supported_cmds_from_source(source)
            self.__save_info()
        return True

    # moves the current zone to a different source
    # this may also change the stream
    def change_source(self, new_source_id):
        self.source_id = new_source_id
        if self.using_group:
            api.move_group_to_source(self.group_id, self.source_id)
        else:
            # move zone to new source
            api.move_zone_to_source(self.zone_id, self.source_id)

        # get current stream
        source = api.get_source(self.source_id)
        self.__update_stream_id_from_source(source)
        self.__update_supported_cmds_from_source(source)

    def __load_info(self):
        try:
            with open(_AUDIO_CONFIG_FILENAME) as zone_file:
                zone_file_str = zone_file.read()
                zone_file_dict = json.loads(zone_file_str)
                self.zone_id = zone_file_dict['zone']
                self.group_id = zone_file_dict['group']
                self.using_group = zone_file_dict['using_group']
        except Exception:
            # open failed, make file
            self.__save_info()

    def __save_info(self):
        zone_file_dict = {'zone': self.zone_id, 'group': self.group_id, 'using_group': self.using_group}
        with open(_AUDIO_CONFIG_FILENAME, 'w') as zone_file:
            zone_file_str = json.dumps(zone_file_dict)
            zone_file.write(zone_file_str)

    def __update_stream_id_from_source(self, source):
        self.stream_id = api.get_stream_id_from_source_dict(source)

    def __update_supported_cmds_from_source(self, source):
        self.supported_cmds = source['info']['supported_cmds']
