class File_processor():

    def __init__(self):
        pass

    """Gets the requested file.
        return: the file in bytes if it could be read, True for successful read or False otherwise"""
    def read_file(self,file_name):
        file = bytearray()
        successful_read = False
        try:
            f = open(file_name,'rb')
            file = f.read(80000)
            successful_read = True
            f.close()
        except:
            pass

        return file , successful_read 

    """Gets the file extension.
        return: the file extension"""
    def get_file_extension(self,file_name):
        file_extension = ""
        try:
            file_extension = ('.' + file_name.split('.')[1])
        except:
            file_extension = ".null"
    
        return file_extension
    
    """Gets the file length.
        return: the file length"""
    def get_file_length(self,file):
        return len(file)
        
      