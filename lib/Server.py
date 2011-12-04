"""
Serves files out of its current directory.
Doesn't handle POST requests.
"""
import SocketServer
import SimpleHTTPServer

import Parser
import Tailer

class Server:
    def __init__(self, port):
        self.port = port

    def serve(self):
        httpd = SocketServer.ThreadingTCPServer(('localhost', self.port), 
                    SimpleHTTPServer.SimpleHTTPRequestHandler)
        print "serving at port", self.port

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print "exiting..."
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

#    def move():
#        """ sample function to be called via a URL"""
#        p = Parser()
#
#    class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
#        def do_GET(self):
#            #Sample values in self for URL: http://localhost:8080/jsxmlrpc-0.3/
#            #self.path  '/jsxmlrpc-0.3/'
#            #self.raw_requestline   'GET /jsxmlrpc-0.3/ HTTP/1.1rn'
#            #self.client_address    ('127.0.0.1', 3727)
#            if self.path=='/move':
#                #This URL will trigger our sample function and send what it returns back to the browser
#                self.send_response(200)
#                self.send_header('Content-type','text/html')
#                self.end_headers()
#                self.wfile.write(move()) #call sample function here
#                return
#            else:
#                #serve files, and directory listings by following self.path from
#                #current working directory
#                SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
#
