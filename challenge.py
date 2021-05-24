from hacksport.problem import Challenge, PreTemplatedFile, File, ExecutableFile, files_from_directory
from string import digits
from os.path import join
import os
from hacksport.deploy import give_port

STATIC_PORT = 8080
SERVICE_FILENAME = "/etc/systemd/system/{0}.service"
SERVICE_IMPL = """[Unit]
Description={0}
After=network.target
[Service]
ExecStart={1}/start.sh
Restart=always
User={0}
Group={0}
Environment=PATH=/usr/bin:/usr/local/bin
WorkingDirectory={1}
[Install]
WantedBy=multi-user.target
"""

START_FILENAME = "start.sh"
START_SERV = """#!/bin/sh
forever kill 0
forever start problem/dist/server.js --PORT=\"{port}\" --FLAG=\"{flag}\" 
forever logs -f 0
"""
INIT_CMDS = [
    "mkdir /home/{user}",
    "chown {user}:{user} /home/{user}",
    "npm i -g yarn forever",
    "mkdir {directory}/node_modules",
    "cd problem && yarn install --modules-folder {directory}/node_modules"
]
START_CMD = "systemctl start {0}"

def files_from_dir_pretemp(directory):
    result = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            result.append(PreTemplatedFile(join(root, filename)))
    return result

class Problem(Challenge):
    flag = ""
    full_flag = ""
    files = files_from_dir_pretemp("node_modules/") + files_from_dir_pretemp("problem/")
    dont_template = ["node_modules", "problem"]
    start_cmd = ''
    port = -1    
    
    def initialize(self):
        print(self.__dict__)
        for cmd in INIT_CMDS:
            cmd = cmd.format(directory=self.directory, user=self.user)
            print("Running {}".format(cmd))   
            os.system(cmd)
        self.write_service()
        self.start_cmd = START_CMD.format(self.user)

    def generate_flag(self, random):
        hexdigits = "{:08x}".format(random.randrange(16**8))
        return "picoCTF{all_it_takes_is_a_little_white_lie_and_your__proto__gets_pwnd_%s}" %hexdigits
    def setup(self):
        os.system(self.start_cmd)

    def write_service(self):
        #Write start file
        open(START_FILENAME, 'w').write(START_SERV.format(flag = self.flag, port = self.port))
        self.files.append(ExecutableFile(START_FILENAME))

        #write service
        open(SERVICE_FILENAME.format(self.user),'w').write(SERVICE_IMPL.format(self.user, self.directory))
        os.system("systemctl daemon-reload") 

    @property
    def port(self):
        """
        Provides port on-demand with caching
        """
        if not hasattr(self, '_port'):
            self._port = give_port()
        return self._port

    def service(self):
        return {"Type": "simple", "ExecStart": self.start_cmd} 
