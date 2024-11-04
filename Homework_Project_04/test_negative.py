"""
Автотест архиватора 7z
Файл с негативными тестами (проверками)

"""

import yaml
from checkers import ssh_getout, ssh_checkout_negative, ssh_checkout, upload_files

with open('config.yaml') as f:
    data = yaml.safe_load(f)


def save_log(starttime, name):
    # вспомогательная функция
    with open(name, 'w') as s:
        s.write(ssh_getout(data["ip"], data["user"], data["passwd"], "journalctl --since '{}'".format(starttime)))


class TestNegative:
    def save_log(self, starttime, name):
        with open(name, 'w') as s:
            s.write(ssh_getout(data["ip"],
                               data["user"],
                               data["passwd"],
                               "journalctl --since '{}'".format(starttime)))

    def test_nstep1(self, start_time):
        # test neg 1 - автодеплой для user2
        res = []
        upload_files(data["ip"],
                     data["user"],
                     data["passwd"],
                     "files/{}.deb".format(data["pkgname"]),
                     "/home/{}/{}.deb".format(data["user"], data["pkgname"]))
        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "echo {} | sudo -S dpkg -i /home/{}/{}.deb".format(data["passwd"],
                                                                                     data["user"],
                                                                                     data["pkgname"]),
                                "Настраивается пакет"))

        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "echo {} | sudo -S dpkg -s {}".format(data["passwd"], data["pkgname"]),
                                "Status: install ok installed"))
        save_log(start_time, "log_test1.txt")
        assert all(res), "test negative1 FAIL"


    def test_nstep2(self, make_folders, clear_folders, make_files, make_bad_arh, start_time):
        # test neg 2 - разархивация поврежденного архива
        self.save_log(start_time, "log_test_neg1.txt")
        assert ssh_checkout_negative(data["ip"],
                                     data["user"],
                                     data["passwd"],
                                     "cd {}; 7z e broken_arh.{} -o{} -y".format(data["folder_neg"],
                                                                                data["type"],
                                                                                data["folder_in"]),
                                     "ERRORS"), "test negative2 FAIL"


    def test_nstep3(self, make_bad_arh, start_time):
        # test neg 3 -тестирование файла в поврежденном архиве
        self.save_log(start_time, "log_test_neg2.txt")
        assert ssh_checkout_negative(data["ip"],
                                     data["user"],
                                     data["passwd"],
                                     "cd {}; 7z t broken_arh.{}".format(data["folder_neg"],
                                                                        data["type"]),
                                     "ERRORS"), "test negative3 FAIL"


    def test_nstep4(self, start_time):
        # test neg 3 - удаление пакета
        res = []
        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "echo {} | sudo -S dpkg -r {}".format(data["passwd"],
                                                                      data["pkgname"]), "Удаляется"))

        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "echo {} | sudo -S dpkg -s {}".format(data["passwd"], data["pkgname"]),
                                "Status: deinstall ok"))
        save_log(start_time, "log_test11.txt")
        assert all(res), "test negative4 FAIL"