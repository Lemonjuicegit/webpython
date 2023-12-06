import unittest
import zipfile
import os


class TestZipList(unittest.TestCase):
    def test_zip_list(self):
        filelist = [
            r"E:\exploitation\webpython\upload\main.py",
            r"E:\exploitation\webpython\upload\server.py",
            r"E:\exploitation\webpython\upload\sign.py",
        ]
        zipname = r"E:\exploitation\webpython\upload\test.zip"
        with zipfile.ZipFile(zipname, "w") as zip_file:
            for fpath in filelist:
                zip_file.write(fpath, arcname=fpath.split(os.sep)[-1])

        # Assert that the zip file is created
        self.assertTrue(os.path.exists(zipname))

        # Assert that the zip file is not empty
        zip_file = zipfile.ZipFile(zipname, "r")
        self.assertGreater(len(zip_file.infolist()), 0)

        # Clean up the created zip file
        # os.remove(zipname)


if __name__ == "__main__":
    unittest.main()
