from tabulate import tabulate
import datetime

class Log_writer:
    def __init__(self):
        pass
    
    def write_server_log(self,request_method , server_name , referer , url , request_data):
        message = {"Metodo": [request_method], "Estampilla de tiempo": [datetime.datetime.now()] , "Servidor": [server_name], "Refiere":[ referer] , "URL": [url] , "Datos" : [request_data] }
        information_to_write = "\n" +  str(tabulate( message, tablefmt='grid', headers='keys') ) + "\n"
        f = open("Server_log.txt",'a')
        f.write(information_to_write)  
        f.close()