from File_processor import File_processor
from Log_writer import Log_writer
from Server import Web_server

if __name__ == '__main__':
    port = int(input('Type a number of port to establish a connection: '))
    file_processor = File_processor() 
    log_writer = Log_writer()
    server = Web_server(port , file_processor , log_writer)
    server.start_server()