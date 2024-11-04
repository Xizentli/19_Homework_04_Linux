"""
Автотест архиватора 7z
Файл с позитивными тестами (проверками)

"""

import yaml
from checkers import ssh_checkout, upload_files, ssh_getout

with open('config.yaml') as f:
    data = yaml.safe_load(f)


def save_log(starttime, name):
    with open(name, 'w') as s:
        s.write(ssh_getout(data["ip"], data["user"], data["passwd"], "journalctl --since '{}'".format(starttime)))


# тестовый класс
class TestPositive:

    def test_step1(self, start_time):
        # test1 - автодеплой для user2
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
        assert all(res), "test1 FAIL"


    def test_step2(self, make_folders, clear_folders, make_files, start_time):
        # test2 - создание архива
        res1 = ssh_checkout(data["ip"],
                            data["user"],
                            data["passwd"],
                            "cd {}; 7z a {}/arh".format(data["folder_from"], data["folder_out"]),
                            "Everything is Ok")
        res2 = ssh_checkout(data["ip"],
                            data["user"],
                            data["passwd"],
                            "ls {}".format(data["folder_out"]),
                            "arh.{}".format(data["type"]))
        save_log(start_time, "log_test2.txt")
        assert res1 and res2, "test2 FAIL"

    def test_step3(self, clear_folders, make_files, start_time):
        # test3 - разархивация
        res = []
        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "cd {}; 7z a {}/arh".format(data["folder_from"],
                                                            data["folder_out"]),
                                "Everything is Ok"))
        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "cd {}; 7z e arh.{} -o{} -y".format(data["folder_out"],
                                                                    data["type"],
                                                                    data["folder_in"]),
                                "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"],
                                    data["user"],
                                    data["passwd"],
                                    "ls {}".format(data["folder_in"]),
                                    item))
        save_log(start_time, "log_test3.txt")
        assert all(res), "test3 FAIL"


    def test_step4(self, start_time):
        # test4 - проверка целостности архива
        save_log(start_time, "log_test4.txt")
        assert ssh_checkout(data["ip"],
                            data["user"],
                            data["passwd"],
                            "cd {}; 7z t arh.{}".format(data["folder_out"],
                                                        data["type"]),
                            "Everything is Ok"), "test4 FAIL"


    def test_step5(self, start_time):
        # test5 - обновление файлов в архиве
        save_log(start_time, "log_test5.txt")
        assert ssh_checkout(data["ip"],
                            data["user"],
                            data["passwd"],
                            "cd {}; 7z u arh.{}".format(data["folder_from"],
                                                        data["type"]),
                            "Everything is Ok"), "test5 FAIL"


    def test_step6(self, clear_folders, make_files, start_time):
        # test6 - список содержимого архива
        res = []
        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "cd {}; 7z a {}/arh".format(data["folder_from"],
                                                            data["folder_out"]),
                                "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"],
                                    data["user"],
                                    data["passwd"],
                                    "cd {}; 7z l arh.{}".format(data["folder_out"],
                                                                data["type"]),
                                    item))
        save_log(start_time, "log_test6.txt")
        assert all(res), "test6 FAIL"


    def test_step7(self, clear_folders, make_files, make_subfolder, start_time):
        # test7 - извлечение файлов с полными путями
        res = []
        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "cd {}; 7z a {}/arh".format(data["folder_from"],
                                                            data["folder_out"]),
                                "Everything is Ok"))
        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "cd {}; 7z x arh.{} -o{} -y".format(data["folder_out"],
                                                                    data["type"],
                                                                    data["folder_in"]),
                                "Everything is Ok"))

        for item in make_files:
            res.append(ssh_checkout(data["ip"],
                                    data["user"],
                                    data["passwd"],
                                    "ls {}".format(data["folder_in"]),
                                    item))

        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "ls {}".format(data["folder_in"]),
                                make_subfolder[0]))

        res.append(ssh_checkout(data["ip"],
                                data["user"],
                                data["passwd"],
                                "ls {}/{}".format(data["folder_in"], make_subfolder[0]),
                                make_subfolder[1]))

        save_log(start_time, "log_test7.txt")
        assert all(res), "test7 FAIL"


    def test_step8(self, start_time):
        # test8 - удаление файлов из архива
        save_log(start_time, "log_test8.txt")
        assert ssh_checkout(data["ip"],
                            data["user"],
                            data["passwd"],
                            "cd {}; 7z d arh.{}".format(data["folder_out"],
                                                        data["type"]),
                            "Everything is Ok"), "test8 FAIL"


    def test_step9(self, clear_folders, make_files, start_time):
        # test9 - проверка хэша
        res = []
        for item in make_files:
            res.append(ssh_checkout(data["ip"],
                                    data["user"],
                                    data["passwd"],
                                    "cd {}; 7z h {}".format(data["folder_from"], item),
                                    "Everything is Ok"))
            hash = ssh_getout(data["ip"],
                              data["user"],
                              data["passwd"],
                              "cd {}; crc32 {}".format(data["folder_from"], item)).upper()
            res.append(ssh_checkout(data["ip"],
                                    data["user"],
                                    data["passwd"],
                                    "cd {}; 7z h {}".format(data["folder_from"], item),
                                    hash))
        save_log(start_time, "log_test9.txt")
        assert all(res), "test9 FAIL"


    def test_step10(self, clear_folders, start_time):
        # test 10 - удаление директорий
        save_log(start_time, "log_test10.txt")
        assert ssh_checkout(data["ip"],
                            data["user"],
                            data["passwd"],
                            "rmdir {} {} {} {}".format(data["folder_in"],
                                                       data["folder_out"],
                                                       data["folder_from"],
                                                       data["folder_neg"]), ""), "test10 FAIL"


    def test_step11(self, start_time):
        # test 10 - удаление пакета
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
        assert all(res), "test11 FAIL"