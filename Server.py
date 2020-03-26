import socket
import sys
import datetime


"""Gets the requested file.
    return: the file in bytes if it could be read, return code , None otherwise"""
def get_file(file_name):
    file = ""
    code = 404 #File not found code
    
    try:
        f = open(file_name,'rb')
        file = f.read(buffer_size)
        f.close()
        code = 200 #OK code

    except:
        pass

    return file , code


"""Gets the file extension.
    return: the file extension"""
def get_file_extension(file_name):
       return file_name.split('.')[1]
   
   
"""Verifies the return code and choose the correct message
    return : string with a code message"""
def get_code_message(return_code):
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
def build_response(file_extension,file_length,file,return_code):
    code_message = get_code_message(return_code)
    today_date = datetime.datetime.today()   
    file_to_send = ""
    
    #Try to decode the file that comes in bytes
    try:
       file_to_send = file.decode("utf-8")
    except:
        pass
        
    first_line = "HTTP/1.1 " + str(return_code) + " " + code_message
    date = "Date: " + days[today_date.weekday()] + ", " + str(today_date.day) + " " + months[today_date.month] + " " + str(today_date.hour) + ":" + str(today_date.minute) + ":" + str(today_date.second) + " GMT" ;
    server = "Server: RobDanServer";
    content_length = "Content-Length: " + str(file_length);
    content_type = "Content-Type: "; # myme type, uses file extension
    
    
    final_response = first_line + "\r\n" + date + "\r\n" + server + "\r\n" + content_length + "\r\n" + content_type + "\r\n" + "\r\n" + file_to_send ;
    return final_response

#################################################################################################################################################################################

#WE NEED TO MODULARIZE THIS PART AND MAYBE MAKE A CLASS

#Notes : 
#        - The "Referer header" is sent by clients, server just need to process it
#        - The "Accept header" is sent by clients, server just need to process it
#        - The "Host header" is sent by clients, server just need to process it

days = ["Sun,""Mon","Tue","Wed","Thu","Fri","Sat"]
months = ["Dec","Jan","Feb","Mar","Apr","May","Jun","July","Aug","Sep","Oct","Nov"]
buffer_size = 4096
data = None
request = []
file_name = ""
file = ""
file_extension = ""
file_length = 0
return_code = 0
petition_method = ""

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 6549)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

# Wait for a connection
print('waiting for a connection')
connection, client_address = sock.accept()

try:
    print('connection from', client_address,"\n")

    # Receive the data 
    while True:
        data = connection.recv(buffer_size)
        if data:
            data_string = data.decode("utf-8")  #Converts bites to String
            request = data_string.split( "\r\n")  #Splits the request in lines to put each line in an array (To analyze headers in the future)   
            request_method = request[0].split(' ')[0]
            file_name = "webRoot/" + request[0].split(' ')[1].replace('/','')  #Gets the file name to open it from the webroot folder
            file , return_code = get_file(file_name)
            
            
            # for header in request: #Just for test
            #     print(header , "\n")
            
            # print(request_method)
            # print(file_name)
            # print(file_extension)
            # print(file_length)
            # print(file)
    
            if(return_code == 200):
                file_length = len(file)
                file_extension = get_file_extension(file_name)
           
            elif return_code == 404:
                pass #do something
            
            elif return_code == 406:
                pass #do something
            
            elif return_code == 501:
                pass #do something
            
            print( build_response( file_extension , file_length , file , return_code ) )

            #Verifies if the request is by GET,POST OR HEAD (I think these conditions are just used to write in the log)
            # if (request_method == "GET"):
            #    pass
                
                # while (True):
                # conn.send(l)
                # print('Sent ',repr(l))
                # l = f.read(1024)

            # elif (request_method == "POST" ):
            #     print("Hay POST")

            # elif (request_method == "HEAD"):
            #     print("Hay HEAD")

        else:
            connection.close()
            print("Connection closed")
            break

except KeyboardInterrupt:
    print("Connection Ccncelled")
    connection.close()
    
except ConnectionResetError :
      print("An existing connection was forcibly closed by the remote host")
