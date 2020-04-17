from File_processor import File_processor
from Log_writer import Log_writer
import socket
import sys
import datetime
import mimetypes
import threading

class Web_server():
    
    def __init__(self , port , file_processor , log_writer):
        self.port = port
        self.file_processor = file_processor
        self.log_writer = log_writer
        self.days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
        self.months = ["Dec","Jan","Feb","Mar","Apr","May","Jun","July","Aug","Sep","Oct","Nov"]
        self.server_name = "Server: RobDanServer";
        self.buffer_size = 80000
    
    """Verifis if the request method is implemented"""
    def is_implemented ( self, request_method ):
        implemented = False
        if (request_method == "GET" or request_method == "POST" or request_method == "HEAD"):
            implemented = True

        return implemented

    """Starts to listen requests from clients"""
    def start_server(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = ('localhost', self.port)
        print('\nStarting up on {} port {}'.format(*server_address))
        sock.bind(server_address)
        # Listen for incoming connections
        sock.listen(5)

        try:
            # Receive the data 
            while True:
                # Wait for a connection
                print('Waiting for a connection')
                connection, client_address = sock.accept()
                print('Connection from', client_address,"\n")

                #Se levanta un thread que escucha la peticion https del cliente
                thread_https = threading.Thread(target=self.receive_request,args=(connection,))
                thread_https.start()

        except KeyboardInterrupt:
            print("Connection Cancelled\n")
            connection.close()
                
        except ConnectionResetError :
            print("An existing connection was forcibly closed by the remote host\n")

    """Processes the request coming from clients and sends the final response to them """
    def receive_request(self,connection):
        data = None
        accepted_data_types = ""
        file_name = ""
        server_response = ""
        accepted_exist = 0
        request_method  = ""
        referer = ""
        file_to_send = bytearray()
        successful_read = False
        file_extension = ""
        file_mime_type = ""
        file_length = 0
        
        try:       
            data = connection.recv(self.buffer_size)
            if data:  
            
                file_name , accepted_data_types , accepted_exist , request_method , referer , request_data  , url  = self.get_request_information ( data )
                file_extension ,  file_mime_type , file_to_send  , successful_read , file_length  = self.get_requested_file_information(file_name)
                mime_type_exist = self.verify_accepted_file_types(accepted_data_types, file_mime_type )
                return_code , code_message = self.get_return_code_information(successful_read , accepted_data_types , file_mime_type , accepted_exist , mime_type_exist , request_method  )

                if(return_code == 501):
                    file_length = 0

                else:
                    if( mime_type_exist == False ) :
                        if (return_code == 406):
                            file_length = 0
                        
                server_response = self.build_response( accepted_data_types , accepted_exist , request_method , referer , file_to_send  , successful_read , file_extension , file_mime_type, file_length , return_code , code_message , request_data  , url )

                #print( server_response )

                connection.send(server_response)

            else:
                connection.close()
                print("Connection closed")

        except KeyboardInterrupt:
            print("Connection Cancelled")
            connection.close()
            
        except ConnectionResetError :
            print("An existing connection was forcibly closed by the remote host")

    """Processes the request coming from clients and sends the final response to them"""
    def get_request_information (self , data) : 
        data_string = data.decode("utf-8")  #Converts bites to String
        request = data_string.split( "\r\n")  #Splits the request in lines to put each line in an array (To analyze headers in the future) 
        request_method = request[0].split(' ')[0]
        referer = self.get_referer_header_data(request)
        accepted_file_extesion , accepted_exist = self.get_accept_header_data(request)
        file_name , request_data  , url = self.process_by_request_method(request_method,request)
        if (file_name == "../webRoot/"):
            file_name += "index.html"
        
        return file_name , accepted_file_extesion , accepted_exist , request_method , referer , request_data  , url

    """Verifies if the request is by GET,POST OR HEAD (I think these conditions are just used to write in the log)"""
    def process_by_request_method(self,request_method , request):
        url = ""
        file_address = "../webRoot" + (request[0].split(' ')[1])  #Gets the file name to open it from the webroot folder
        request_data = ""

        if (request_method == "GET"):

            if(file_address.find('?') > -1):
                variables_and_file_name = file_address.split('?')
                file_address = variables_and_file_name[0]
                request_data = variables = variables_and_file_name[1]
            
            url = file_address.split("../webRoot/")[1]
            
        elif(request_method == "POST"):
            request_data = request[ len(request) - 1 ]
          
        url = file_address.split("../webRoot/")[1]
            
        return file_address , request_data  , url

    """Gets the requested file information to process it"""
    def get_requested_file_information(self,file_name):
        file_extension = ""
        file_mime_type = ""
        file_to_send  = bytearray () 
        successful_read = False
        file_length = 0

        try:
            file_extension = self.file_processor.get_file_extension(file_name)
            file_mime_type = mimetypes.types_map[file_extension]
            file_to_send  , successful_read = self.file_processor.read_file(file_name)
            file_length = self.file_processor.get_file_length(file_to_send)
        except:
            file_mime_type = ""

        return file_extension ,  file_mime_type , file_to_send  , successful_read , file_length 

    """Sets the retunr code of the request"""
    def get_return_code_information(self, successful_read , accepted_data_types , file_mime_type , accepted_exist , mime_type_exist , request_method):
        return_code = 0
        code_message = ""

        if( self.is_implemented (request_method ) == True):
            if( successful_read == True):
                if (accepted_exist > -1 and mime_type_exist == False):
                    return_code = 406
                    code_message = "Not Acceptable"

                else:
                    return_code = 200
                    code_message = "OK"
            else: 
                return_code = 404
                code_message = "Not Found"
        
        else :
            return_code = 501
            code_message = "Not Implemented"

        return return_code,code_message

    """Verifies if the request has the Referer Header, if it has some data returns it"""
    def get_referer_header_data(self,request):
        referer = ""
        for header in request:
            if (header.find("Referer:") > -1 ): 
                referer = header.split()[1]
                break
        return referer

    """Verifies if the request has the Accept Header, if it has some data returns it"""
    def get_accept_header_data(self,request):
        accepted_file_extesion = request[3].split(' ')[1].split(',')
        accepted_exist = request[3].find("Accept:")
        return accepted_file_extesion , accepted_exist

    """Verifies if accepted_data_types contains file_mime_type """
    def verify_accepted_file_types(self, accepted_data_types, file_mime_type  ):
        acceptable = False
                
        for type in accepted_data_types:
            if ( type == file_mime_type or type == "*/*" ):
                acceptable = True
                break

        return acceptable
        
    """Builds the response from server to client
        return : the final response to client """
    def build_response(self , accepted_data_types , accepted_exist , request_method , referer , file_to_send  , successful_read , file_extension , file_mime_type, file_length , return_code , code_message , request_data  , url):

        final_response = bytearray()
        first_line = "HTTP/1.1 " + str(return_code) + " " + code_message
        today_date = datetime.datetime.today()
        date = "Date: " + self.days[today_date.weekday()] + ", " + str(today_date.day) + " " + self.months[today_date.month] + " " + str(today_date.hour) + ":" + str(today_date.minute) + ":" + str(today_date.second) + " GMT" ;
        content_length = "Content-Length: " + str(file_length);
        content_type = ""
 
        if(successful_read == True and return_code != 501 ):
            if (return_code == 200) : 
                try:
                    content_type = "Content-Type: " + mimetypes.types_map[file_extension]; # myme type, uses file extension
                    file_to_send = file_to_send.decode("utf-8")
                    final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n" + file_to_send ).encode()) 
                    self.log_writer.write_server_log(request_method,self.server_name.split(" ")[1], referer , url , request_data)
 
                except:
                    final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())
                    final_response += file_to_send
                    self.log_writer.write_server_log(request_method,self.server_name.split(" ")[1], referer , url , request_data)

            elif (return_code == 406) :
                final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())
        else:
            errorFile , content_type , content_length = self.get_error_file()
            final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())
            final_response += errorFile
        return final_response

    def get_error_file (self):
        errorFile , error = self.file_processor.read_file("../webRoot/404Error.html")
        content_type = "Content-Type: " + mimetypes.types_map[".html"];
        content_length = "Content-Length: " + str(len(errorFile));
  
        return errorFile , content_type , content_length
    

    

   

  
