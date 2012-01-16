import sys
import socket
import time
import thread
import threading
import Queue
import SocketServer
import SimpleHTTPServer

import Parser
import Tailer

class Server:
    """ HTTP server for serving the parsed GC data """
    def __init__(self, port, services):
        self.p = Parser.Parser()
        sys.setcheckinterval(1000)

        listeningHost = socket.gethostbyaddr(socket.gethostname())[0]

        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        self.httpd = SocketServer.ThreadingTCPServer( (listeningHost, port), 
                    #SimpleHTTPServer.SimpleHTTPRequestHandler)
                    CustomHandler)
        self.httpd.allow_reuse_address = True        # Ignore TIME_WAIT

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        #self.server_thread = threading.Thread(name='server', target=self.serve)
        ## Exit the server thread when the main thread terminates
        #self.server_thread.daemon = True
        #self.server_thread.start()
        print "serving at %s:%i" % (listeningHost, port)


        for service in services:
            #print "service:", service
            t = Tailer.Tailer(service['name'], service['logfile'], service['sleep'])
            thread.start_new_thread(self.p.follow, (t, service['name']))

            # Couldn't get it to work with thread module :/
            #t = Tailer.Tailer(service['logfile'], q)
            #thread = threading.Thread(name=service['name'],
            #                    target=self.p.follow(t))
            #thread.daemon = True
            #threads.append(thread)
            #thread.start()

        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print "exiting..."
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
            pass

        return

class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        p = Parser.Parser()

        #print "path:", self.path
        if "reset=1" in self.path:
            p.clearData()

        result = p.getMetrics()

        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        self.wfile.write(result + "\n")
        return

