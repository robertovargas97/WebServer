import socket
import sys
import datetime
import mimetypes
import threading

#WE NEED TO MODULARIZE THIS PART AND MAYBE MAKE A CLASS

#Notes : 
#        - The "Referer header" is sent by clients, server just need to process it
#        - The "Accept header" is sent by clients, server just need to process it
#        - The "Host header" is sent by clients, server just need to process it
#        - We need to process the received variables through the URL


class WebServer():
    
    def __init__(self):
        self.days = ["Sun,""Mon","Tue","Wed","Thu","Fri","Sat"]
        self.months = ["Dec","Jan","Feb","Mar","Apr","May","Jun","July","Aug","Sep","Oct","Nov"]
        self.buffer_size = 50000
        self.server_name = "Server: RobDanServer";

    """Gets the requested file.
        return: the file in bytes if it could be read, return code , None otherwise"""
    def read_file(self,file_name):
        file = bytearray()
        code = 404 #File not found code
        
        try:
            f = open(file_name,'rb')
            file = f.read(self.buffer_size)
            code = 200 #OK code
            f.close()

        except:
            pass

        return file , code


    """Gets the file extension.
        return: the file extension"""
    def get_file_extension(self,file_name):
        return ('.' + file_name.split('.')[1])
    
    def get_file_information(self,file,file_name):
        file_length = len(file)
        file_extension = self.get_file_extension(file_name)

        return file_length, file_extension

    """Verifies the return code and choose the correct message
        return : string with a code message"""
    def get_code_message(self,return_code):
        code_message = ""

        if return_code == 200:
                code_message = "OK"
        elif return_code == 404:
            code_message = "Forbidden"
        elif return_code == 406:
            code_message = "Not Acceptable"
        elif return_code == 501:
            code_message = "Not Implemented"

        return code_message
        
    """Builds the response from server to client
        return : the final response to client """
    def build_response(self,file_name,file,return_code):

        file_to_send = file
        final_response = bytearray()
        code_message = self.get_code_message(return_code)
        today_date = datetime.datetime.today()

        first_line = "HTTP/1.1 " + str(return_code) + " " + code_message
        date = "Date: " + self.days[today_date.weekday()] + ", " + str(today_date.day) + " " + self.months[today_date.month] + " " + str(today_date.hour) + ":" + str(today_date.minute) + ":" + str(today_date.second) + " GMT" ;
        content_length = "Content-Length: 0";
        content_type = ""

        if return_code == 200: 
            try:
                file_length , file_extension = self.get_file_information(file,file_name)
                content_length = content_length.replace("0", str(file_length));
                content_type = "Content-Type: " + mimetypes.types_map[file_extension]; # myme type, uses file extension
                file_to_send = file.decode("utf-8")
                final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n" + file_to_send ).encode()) 
                
            except:
                final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())
                final_response += file

        elif return_code == 404 :
            final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())

        # elif return_code == 406:
        #     pass #do something
                    
        # elif return_code == 501:
        #     pass #do something
         
        return final_response

    """Verifies if the request is by GET,POST OR HEAD (I think these conditions are just used to write in the log)"""
    def verify_request_methos(self,request_method):
        if (request_method == "GET"):
            pass
           #do something

        elif (request_method == "POST" ):
            pass
            #do something

        elif (request_method == "HEAD"):
            pass
            #do something

    """Processes the request coming from clients and sends the final response to them """
    def process_request(self,connection):
        data = None
        request = []
        file_name = ""
        file = bytearray()
        file_extension = ""
        file_length = 0
        return_code = 0
        data_string = ""
        request_method = ""
        server_response = ""

        try:       
            data = connection.recv(self.buffer_size)
            if data:
                data_string = data.decode("utf-8")  #Converts bites to String
                request = data_string.split( "\r\n")  #Splits the request in lines to put each line in an array (To analyze headers in the future)   
                request_method = request[0].split(' ')[0]
                file_name = "webRoot" + request[0].split(' ')[1]  #Gets the file name to open it from the webroot folder
                file , return_code = self.read_file(file_name)
                    
                # for header in request: #Just for test
                #     print(header , "\n")
                  
                server_response = self.build_response( file_name , file , return_code )
                # print( server_response )
                connection.send(server_response)

                self.verify_request_methos(request_method)

            else:
                connection.close()
                print("Connection closed")
                # break

        except KeyboardInterrupt:
            print("Connection Cancelled")
            connection.close()
            
        except ConnectionResetError :
            print("An existing connection was forcibly closed by the remote host")

    def start_server(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = ('localhost', 6549)
        print('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)
        # Listen for incoming connections
        sock.listen(5)

        try:
            # Receive the data 
            while True:
                # Wait for a connection
                print('waiting for a connection')
                connection, client_address = sock.accept()
                print('connection from', client_address,"\n")

                #Se levanta un thread que escucha la peticion https del cliente
                thread_https = threading.Thread(target=self.process_request,args=(connection,))
                thread_https.start()
                #self.process_request(connection)

        except KeyboardInterrupt:
            print("Connection Cancelled")
            connection.close()
                
        except ConnectionResetError :
            print("An existing connection was forcibly closed by the remote host")
    
#################################################################################################################################################################################

if __name__ == '__main__':
   
    server = WebServer()
    server.start_server()