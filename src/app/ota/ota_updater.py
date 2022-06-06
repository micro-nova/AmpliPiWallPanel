import gc
import json
import os

from app import sysconsts, displayserial
from app.ota.httpclient import HttpClient

def make_ota_updater():
    token = None
    try:
        with open('temp-token.txt') as file:
            token = json.loads(file.read())
    except Exception:
        pass

    if token is None:
        ota = OTAUpdater(sysconsts.WALL_PANEL_REPO, main_dir='app', github_src_dir='src', module='')
        print('OTAUpdater loaded without token.')
    else:
        ota = OTAUpdater(sysconsts.WALL_PANEL_REPO, main_dir='app', github_src_dir='src', module='',
                         headers={'Authorization': 'token {}'.format(token['token'])})
        print('OTAUpdater loaded with token.')
    return ota

class OTAUpdater:
    """
    A class to update your MicroController with the latest version from a GitHub tagged release,
    optimized for low power usage.
    """

    def __init__(self, github_repo, github_src_dir='', module='', main_dir='main', new_version_dir='next', secrets_files=None, headers={}):
        """secrets_files was modified to be a list instead of a single file"""
        self.http_client = HttpClient(headers=headers)
        self.github_repo = github_repo.rstrip('/').replace('https://github.com/', '')
        self.github_src_dir = '' if len(github_src_dir) < 1 else github_src_dir.rstrip('/') + '/'
        self.module = module.rstrip('/')
        self.main_dir = main_dir
        self.new_version_dir = new_version_dir
        self.secrets_files = secrets_files
        self.display_msg = ''

    def __del__(self):
        self.http_client = None

    def check_for_update_to_install_during_next_reboot(self) -> bool:
        """Function which will check the GitHub repo if there is a newer version available.
        
        This method expects an active internet connection and will compare the current 
        version with the latest version available on GitHub.
        If a newer version is available, the file 'next/.version' will be created 
        and you need to call machine.reset(). A reset is needed as the installation process 
        takes up a lot of memory (mostly due to the http stack)

        Returns
        -------
            bool: true if a new version is available, false otherwise
        """

        (current_version, latest_version) = self._check_for_new_version()
        if latest_version > current_version:
            print('New version available, will download and install on next reboot')
            self._create_new_version_file(latest_version)
            return True

        return False

    def install_update_if_available_after_boot(self, ssid, password) -> bool:
        """This method will install the latest version if out-of-date after boot.
        
        This method, which should be called first thing after booting, will check if the 
        next/.version' file exists. 

        - If yes, it initializes the WIFI connection, downloads the latest version and installs it
        - If no, the WIFI connection is not initialized as no new known version is available
        """

        if self.new_version_dir in os.listdir(self.module):
            if '.version' in os.listdir(self.modulepath(self.new_version_dir)):
                latest_version = self.get_version(self.modulepath(self.new_version_dir), '.version')
                print('New update found: ', latest_version)
                OTAUpdater._using_network(ssid, password)
                self.install_update_if_available()
                return True
            
        print('No new updates found...')
        return False

    def install_tagged_release(self, tag_name):
        """This method will immediately install the release with tag_name.

        This method expects an active internet connection. Must reset microcontroller after
        calling this method. """
        print(f'Updating to version {tag_name}')
        self._create_new_version_file(tag_name)
        self._download_new_version(tag_name)
        self._copy_secrets_file()
        self._delete_old_version()
        self._install_new_version()

    def install_update_if_available(self) -> bool:
        """This method will immediately install the latest version if out-of-date.
        
        This method expects an active internet connection and allows you to decide yourself
        if you want to install the latest version. It is necessary to run it directly after boot 
        (for memory reasons) and you need to restart the microcontroller if a new version is found.

        Returns
        -------
            bool: true if a new version is available, false otherwise
        """

        (current_version, latest_version) = self._check_for_new_version()
        if latest_version > current_version:
            print('Updating to version {}...'.format(latest_version))
            self._create_new_version_file(latest_version)
            self._download_new_version(latest_version)
            self._copy_secrets_file()
            self._delete_old_version()
            self._install_new_version()
            return True
        
        return False


    @staticmethod
    def _using_network(ssid, password):
        import network
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(ssid, password)
            while not sta_if.isconnected():
                pass
        print('network config:', sta_if.ifconfig())

    def _check_for_new_version(self):
        current_version = self.get_version(self.modulepath(self.main_dir))
        latest_version = self.get_latest_version()

        print('Checking version... ')
        print('\tCurrent version: ', current_version)
        print('\tLatest version: ', latest_version)
        return (current_version, latest_version)

    def _create_new_version_file(self, latest_version):
        self.mkdir(self.modulepath(self.new_version_dir))
        with open(self.modulepath(self.new_version_dir + '/.version'), 'w') as versionfile:
            versionfile.write(latest_version)
            versionfile.close()

    def get_version(self, directory, version_file_name='.version'):
        if version_file_name in os.listdir(directory):
            with open(directory + '/' + version_file_name) as f:
                version = f.read()
                return version
        return '0.0'

    def get_all_tags(self):
        tags = self.http_client.get(f'https://api.github.com/repos/{self.github_repo}/tags')
        return tags.json()

    def get_all_releases(self):
        return self.http_client.get(f'https://api.github.com/repos/{self.github_repo}/releases').json()

    def get_latest_version(self):
        latest_release = self.http_client.get('https://api.github.com/repos/{}/releases/latest'.format(self.github_repo))
        gh_json = latest_release.json()
        try:
            version = gh_json['tag_name']
        except KeyError as e:
            raise ValueError(
                "Release not found: \n",
                "Please ensure release as marked as 'latest', rather than pre-release \n",
                "github api message: \n {} \n ".format(gh_json)
            )
        latest_release.close()
        return version

    def _download_new_version(self, version):
        print('Downloading version {}'.format(version))
        self._download_all_files(version)
        print('Version {} downloaded to {}'.format(version, self.modulepath(self.new_version_dir)))

    def print(self, msg):
        """Prints to console and update screen"""
        print(msg)
        self.display_msg += msg + r'\r'
        if self.display_msg.count(r'\r') > 8:
            self.display_msg = self.display_msg[self.display_msg.find(r'\r')+2:]
            # self.display_msg = r'\r'.join(self.display_msg.splitlines()[-8:])
        displayserial.set_component_txt(displayserial.UPDATE_PAGE_NAME, 'tinfo', self.display_msg)


    def _download_all_files(self, version, sub_dir=''):
        url = 'https://api.github.com/repos/{}/contents/{}{}{}?ref=refs/tags/{}'.format(self.github_repo, self.github_src_dir, self.main_dir, sub_dir, version)
        print(url)
        gc.collect()
        file_list = self.http_client.get(url)
        file_list_json = file_list.json()
        for file in file_list_json:
            # print(file)
            if file == 'message':
                print('got "message" string instead of dict. not sure why.')
                continue
            path = self.modulepath(self.new_version_dir + '/' + file['path'].replace(self.main_dir + '/', '').replace(self.github_src_dir, ''))
            # print(f'path: {path}')
            # print(f'path without filename: {path[0:path.rfind("/")]}')
            # print(f'filename: {path.split("/")[-1]}')
            if file['type'] == 'file':
                gitPath = file['path']
                # print(os.listdir(path[0:path.rfind('/')]))

                if path.split("/")[-1] not in os.listdir(path[0:path.rfind('/')]):
                    self.print(f'\tDownloading: {gitPath} to {path}')
                    # print('\tDownloading: ', gitPath, 'to', path)
                    self._download_file(version, gitPath, path)
                else:
                    self.print(f'Skipping file {gitPath}, already downloaded')
            elif file['type'] == 'dir':
                self.print(f'Creating dir {path}')
                self.mkdir(path)
                self._download_all_files(version, sub_dir + '/' + file['name'])
            gc.collect()

        file_list.close()

    def _download_file(self, version, gitPath, path):
        self.http_client.get('https://raw.githubusercontent.com/{}/{}/{}'.format(self.github_repo, version, gitPath), saveToFile=path)

    def _copy_secrets_file(self):
        # iterate through all secrets files
        if self.secrets_files is not None:
            for secrets_file in self.secrets_files:
                if secrets_file:
                    fromPath = self.modulepath(self.main_dir + '/' + secrets_file)
                    toPath = self.modulepath(self.new_version_dir + '/' + secrets_file)
                    print(f'Copying secrets file from {fromPath} to {toPath}')
                    self._copy_file(fromPath, toPath)
                    print(f'Copied secrets file from {fromPath} to {toPath}')

    def _delete_old_version(self):
        print('Deleting old version at {} ...'.format(self.modulepath(self.main_dir)))
        self._rmtree(self.modulepath(self.main_dir))
        print('Deleted old version at {} ...'.format(self.modulepath(self.main_dir)))

    def _install_new_version(self):
        print('Installing new version at {} ...'.format(self.modulepath(self.main_dir)))
        if self._os_supports_rename():
            os.rename(self.modulepath(self.new_version_dir), self.modulepath(self.main_dir))
        else:
            self._copy_directory(self.modulepath(self.new_version_dir), self.modulepath(self.main_dir))
            self._rmtree(self.modulepath(self.new_version_dir))
        print('Update installed, please reboot now')

    def _rmtree(self, directory):
        for entry in os.ilistdir(directory):
            is_dir = entry[1] == 0x4000
            if is_dir:
                self._rmtree(directory + '/' + entry[0])
            else:
                os.remove(directory + '/' + entry[0])
        print(f'removing directory {directory}')
        os.rmdir(directory)

    def _os_supports_rename(self) -> bool:
        self._mk_dirs('otaUpdater/osRenameTest')
        os.rename('otaUpdater', 'otaUpdated')
        result = len(os.listdir('otaUpdated')) > 0
        self._rmtree('otaUpdated')
        return result

    def _copy_directory(self, fromPath, toPath):
        if not self._exists_dir(toPath):
            self._mk_dirs(toPath)

        for entry in os.ilistdir(fromPath):
            is_dir = entry[1] == 0x4000
            if is_dir:
                self._copy_directory(fromPath + '/' + entry[0], toPath + '/' + entry[0])
            else:
                self._copy_file(fromPath + '/' + entry[0], toPath + '/' + entry[0])

    def _copy_file(self, fromPath, toPath):
        with open(fromPath) as fromFile:
            with open(toPath, 'w') as toFile:
                CHUNK_SIZE = 512 # bytes
                data = fromFile.read(CHUNK_SIZE)
                while data:
                    toFile.write(data)
                    data = fromFile.read(CHUNK_SIZE)
            toFile.close()
        fromFile.close()

    def _exists_dir(self, path) -> bool:
        try:
            os.listdir(path)
            return True
        except:
            return False

    def _mk_dirs(self, path:str):
        paths = path.split('/')

        pathToCreate = ''
        for x in paths:
            self.mkdir(pathToCreate + x)
            pathToCreate = pathToCreate + x + '/'

    # different micropython versions act differently when directory already exists
    def mkdir(self, path:str):
        try:
            os.mkdir(path)
        except OSError as exc:
            if exc.args[0] == 17:
                pass


    def modulepath(self, path):
        return self.module + '/' + path if self.module else path