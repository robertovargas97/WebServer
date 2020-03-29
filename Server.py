from File_processor import File_processor
from Log_writer import Log_writer
import socket
import sys
import datetime
import mimetypes
import threading


#WE NEED TO MODULARIZE THIS PART AND MAYBE MAKE A CLASS

class Web_server():
    
    def __init__(self , port , file_processor , log_writer):
        self.port = port
        self.file_processor = file_processor
        self.log_writer = log_writer
        self.days = ["Sun,""Mon","Tue","Wed","Thu","Fri","Sat"]
        self.months = ["Dec","Jan","Feb","Mar","Apr","May","Jun","July","Aug","Sep","Oct","Nov"]
        self.server_name = "Server: RobDanServer";
        self.buffer_size = 80000
        self.request_method = ""
        self.get_request_data = ""
        self.post_request_data = ""
        self.time_stamp = ""
        self.referer = ""
        self.url = ""


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
        accept_data = ""
        file_name = ""
        server_response = ""
        
        try:       
            data = connection.recv(self.buffer_size)
            if data:  
            
                file_name , accept_data , accepted_exist  = self.get_request_file_information ( data )
                server_response = self.build_response( file_name , accept_data , accepted_exist  )
                # print( server_response )

                connection.send(server_response)

            else:
                connection.close()
                print("Connection closed")

        except KeyboardInterrupt:
            print("Connection Cancelled")
            connection.close()
            
        except ConnectionResetError :
            print("An existing connection was forcibly closed by the remote host")





    
    def set_return_code_information(self, successful_read , accept_data , file_mime_type , accepted_exist ):
        return_code = 0
        code_message = ""

        if (successful_read == True):
            if (accepted_exist > -1 ): 
                if( accept_data != file_mime_type and accept_data != "*/*"):
                    return_code = 406
                    code_message = "Not Acceptable"
                else:
                    return_code = 200
                    code_message = "OK"
            else:
                return_code = 200
                code_message = "OK"
                
        elif (successful_read == False ):
            return_code = 404
            code_message = "Forbidden"

        return return_code,code_message
        
    """Builds the response from server to client
        return : the final response to client """
    def build_response(self , file_name , accept_data , accepted_exist ):

        final_response = bytearray()
        file_to_send  , successful_read = self.file_processor.read_file(file_name)
        file_extension = self.file_processor.get_file_extension(file_name)
        try:
            file_mime_type = mimetypes.types_map[file_extension]
        except:
            file_mime_type = ""

        return_code , code_message = self.set_return_code_information(successful_read , accept_data , file_mime_type , accepted_exist )
        first_line = "HTTP/1.1 " + str(return_code) + " " + code_message
        today_date = datetime.datetime.today()
        date = "Date: " + self.days[today_date.weekday()] + ", " + str(today_date.day) + " " + self.months[today_date.month] + " " + str(today_date.hour) + ":" + str(today_date.minute) + ":" + str(today_date.second) + " GMT" ;
        content_length = "Content-Length: 0";
        content_type = ""
 
        if(successful_read == True ):

            if (return_code == 200) : 
                try:
                    file_length = self.file_processor.get_file_length(file_to_send)
                    content_length = content_length.replace("0", str(file_length));
                    content_type = "Content-Type: " + mimetypes.types_map[file_extension]; # myme type, uses file extension
                    file_to_send = file_to_send.decode("utf-8")
                    final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n" + file_to_send ).encode()) 
                    self.log_writer.write_server_log(self.request_method,self.server_name.split(" ")[1], self.referer , self.url , self.request_data)
 
                except:
                    final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())
                    final_response += file_to_send
                    self.log_writer.write_server_log(self.request_method,self.server_name.split(" ")[1], self.referer , self.url , self.request_data)


            elif (return_code == 406) :
                final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())
        else:
            final_response += ((first_line + "\r\n" + date + "\r\n" + self.server_name + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n").encode())

        return final_response

    """Verifies if the request is by GET,POST OR HEAD (I think these conditions are just used to write in the log)"""
    def process_by_request_method(self,request_method,request):
        file_address = "webRoot" + (request[0].split(' ')[1])  #Gets the file name to open it from the webroot folder
        self.request_data = ""
        if (self.request_method == "GET"):
            self.get_request_data = ""
            if(file_address.find('?') > -1):
                variables_and_file_name = file_address.split('?')
                file_address = variables_and_file_name[0]
                self.request_data = variables = variables_and_file_name[1]
                
            self.url = file_address 
            #self.log_writer.write_server_log(self.request_method,self.server_name.split(" ")[1],self.referer , self.url , self.get_request_data)

        elif( self.request_method == "POST"):
            self.url = file_address
            self.request_data = request[ len(request) - 1 ]
            #self.log_writer.write_server_log(self.request_method,self.server_name.split(" ")[1],self.referer , self.url , self.post_request_data)
          
        elif ( self.request_method == "HEAD"):
            self.url = file_address
            #self.log_writer.write_server_log(self.request_method,self.server_name.split(" ")[1],self.referer , self.url , "")

            pass
       
        return file_address
        
    def set_referer(self,request):
        self.referer = ""
        for header in request: #Just for test
            if (header.find("Referer:") > -1 ): 
                self.referer = header.split()[1]
               
    def verify_accept(self,request):
        accepted_file_extesion = request[3].split(' ')[1]
        accepted_exist = request[3].find("Accept:")
        return accepted_file_extesion , accepted_exist

    """Processes the request coming from clients and sends the final response to them """
    def get_request_file_information (self , data) : 
        data_string = data.decode("utf-8")  #Converts bites to String
        request = data_string.split( "\r\n")  #Splits the request in lines to put each line in an array (To analyze headers in the future) 

        for l in request:
            print(l)

        self.request_method = request[0].split(' ')[0]
        self.set_referer(request)
        accepted_file_extesion , accepted_exist = self.verify_accept(request)
        file_name = self.process_by_request_method(self.request_method,request)
    
        return file_name , accepted_file_extesion , accepted_exist

   

  
