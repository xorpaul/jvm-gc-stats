import sys
import socket
import threading
import SocketServer
import SimpleHTTPServer

import Parser
import Tailer

class Server:
    def __init__(self, port, p, t):
        self.port = port
        self.t = t
        self.p = p
        sys.setcheckinterval(1000)

        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        self.httpd = SocketServer.ThreadingTCPServer(
                    (socket.gethostbyaddr(socket.gethostname())[0], self.port), 
                    #SimpleHTTPServer.SimpleHTTPRequestHandler)
                    CustomHandler)
        self.httpd.allow_reuse_address = True        # Ignore TIME_WAIT

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.serve)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        print "serving at port", self.port

        self.parser_thread = threading.Thread(target=self.p.parse(self.t))
        self.parser_thread.daemon = True
        self.parser_thread.start()

    def serve(self):
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print "Server thread exiting..."
            self.parser_thread._Thread__stop()
            self.server_thread._Thread__stop()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        self.p = Parser.Parser()
        result = self.p.getMetrics()

        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        self.wfile.write(result + "\n")
        return

    def finish(self):
        self.p.clearDatum()
        return


