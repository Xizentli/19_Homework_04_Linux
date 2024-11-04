"""
файл с фикстурами
"""

import random
import pytest
import string
import yaml
from datetime import datetime
from checkers import ssh_checkout, ssh_getout


with open('config.yaml') as f:
    data = yaml.safe_load(f)


@pytest.fixture()
def make_folders():
    return ssh_checkout(data["ip"],
                        data["user"],
                        data["passwd"],
                        "mkdir {} {} {} {}".format(data["folder_in"],
                                                   data["folder_out"],
                                                   data["folder_from"],
                                                   data["folder_neg"]), "")


@pytest.fixture()
def clear_folders():
    return ssh_checkout(data["ip"],
                        data["user"],
                        data["passwd"],
                        "rm -rf {}/* {}/* {}/* {}/*".format(data["folder_in"],
                                                            data["folder_out"],
                                                            data["folder_from"],
                                                            data["folder_neg"]), "")


@pytest.fixture()
def make_files():
    list_of_files = []
    for i in range(data["count"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if ssh_checkout(data["ip"],
                        data["user"],
                        data["passwd"],
                        "cd {}; dd if=/dev/urandom of={} bs={} count=1 iflag=fullblock".format(data["folder_from"],
                                                                                               filename,
                                                                                               data["bs"]), ""):
            list_of_files.append(filename)
    return list_of_files


@pytest.fixture()
def make_subfolder():
    filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    if not ssh_checkout(data["ip"],
                        data["user"],
                        data["passwd"],
                        "cd {}; mkdir {}".format(data["folder_from"], subfoldername), ""):
        return None, None
    if not ssh_checkout(data["ip"],
                        data["user"],
                        data["passwd"],
                        "cd {}/{}; dd if=/dev/urandom of={} bs=1M count=1 iflag=fullblock".format(data["folder_from"],
                                                                                              subfoldername,
                                                                                              filename), ""):
        return subfoldername, None
    else:
        return subfoldername, filename


@pytest.fixture(autouse=True)
def print_time():
    print("Start: {}".format(datetime.now().strftime("%H:%M:%S.%f")))
    yield print("Stop: {}".format(datetime.now().strftime("%H:%M:%S.%f")))


@pytest.fixture()
def make_bad_arh():
    ssh_checkout(data["ip"],
                 data["user"],
                 data["passwd"],
                 "cd {}; 7z a {}/broken_arh".format(data["folder_from"], data["folder_neg"]), "")
    ssh_checkout(data["ip"],
                 data["user"],
                 data["passwd"],
                 "truncate -s 1 {}/broken_arh.{}".format(data["folder_neg"], data["type"]), "Everything is Ok")
    yield "broken_arh"
    ssh_checkout(data["ip"],
                 data["user"],
                 data["passwd"],
                 "rm -f {}/broken_arh.{}".format(data["folder_neg"], data["type"]), "")


@pytest.fixture(autouse=True)
def stat_log():
    yield
    time = datetime.now().strftime("%H:%M:%S.%f")
    stat = ssh_getout(data["ip"],
                      data["user"],
                      data["passwd"],
                      "cat /proc/loadavg")
    ssh_checkout(data["ip"],
                 data["user"],
                 data["passwd"],
                 "echo 'time: {} count: {} size: {} load: {}' >> stat.txt".format(time,
                                                                                  data["count"],
                                                                                  data["bs"],
                                                                                  stat), "")


@pytest.fixture()
def start_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")