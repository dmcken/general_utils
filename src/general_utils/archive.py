'''General archive file functions'''

# System imports
import os
import shutil
import zipfile

# Functions
def zipdir(dir_path: str, output_zip_file: str = None,
           file_ext: str = 'zip', include_dir_in_zip: bool = True,
           include_pattern: str = None, exclude_pattern: str = None) -> None:
    """Archive a directory to a zip file.

    Args:
        dir_path (str, optional): Directory to archive.
        output_zip_file (str, optional): Output zip filename (overrides the automatically generated one). Defaults to None.
        file_ext (str, optional): File extension when automatically generating zip filename. Defaults to 'zip'.
        include_dir_in_zip (bool, optional): Whether to include the directory in the zip file paths. Defaults to True.
        include_pattern (str, optional): _description_. Defaults to None.
        exclude_pattern (str, optional): _description_. Defaults to None.

    Raises:
        OSError: _description_

    Examples:
        # Archive the foo directory to foo.zip "<directory>.<file_ext>"
        zipdir("foo")
        # Foo can be somewhere else
        zipdir("../test1/foo", "foo4nopardirs.zip")
        # Archive the foo to bar.zip
        zipdir("foo", "bar.zip")
        # Assuming there is a bar.txt in the foo directory
        # True (default) - The zip file places the file at foo/bar.txt within the zip file
        # False - The zip file has the file as bar.txt
        zipdir("foo", include_dir_in_zip=False)

    """
    if not os.path.isdir(dir_path):
        raise OSError(f"'{dir_path}' must be a directory")

    if not output_zip_file:
        output_zip_file = dir_path + "." + file_ext

    # Test for output_zip_file already existing

    parentDir, dirToZip = os.path.split(dir_path)

    #Little nested function to prepare the proper archive path
    def trim_path(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not include_dir_in_zip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)


    outFile = zipfile.ZipFile(
        output_zip_file,
        "w",
        compression=zipfile.ZIP_DEFLATED
    )

    # Add contents of dir_path
    for (archiveDirPath, dir_names, fileNames) in os.walk(dir_path):
        for fileName in fileNames:
            if fileName in ['Thumbs.db']: # Replace with exclude_pattern
                continue
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trim_path(filePath))
        #Make sure we get empty directories as well
        if not fileNames and not dir_names:
            zipInfo = zipfile.ZipInfo(trim_path(archiveDirPath) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            outFile.writestr(zipInfo, "")
    outFile.close()

    return
