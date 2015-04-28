from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import json
import pygments.lexers
import pygments.styles
from pygments.formatters.terminal256 import Terminal256Formatter

PORT = 8003
FILE_PREFIX = "."

if __name__ == "__main__":
    try:
        import argparse

        parser = argparse.ArgumentParser(description='A simple fake server for testing your API client.')
        parser.add_argument('-p', '--port', type=int, dest="PORT",
                            help='the port to run the server on; defaults to 8003')
        parser.add_argument('--path', type=str, dest="PATH",
                            help='the folder to find the json files')

        args = parser.parse_args()

        if args.PORT:
            PORT = args.PORT
        if args.PATH:
            FILE_PREFIX = args.PATH

    except Exception:
        # Could not successfully import argparse or something
        pass


class JSONRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        # send response code:
        self.send_response(200)
        #send headers:
        self.send_header("Content-type", "application/json")
        # send a blank line to end headers:
        self.wfile.write("\n")

        try:
            output = open(FILE_PREFIX + "/" + self.path[1:] + ".json", 'r').read()
        except Exception:
            output = "{'error': 'Could not find file " + self.path[1:] + ".json'" + "}"
        self.wfile.write(output)

    def do_POST(self):
        if self.path == "/success":
            response_code = 200
        elif self.path == "/error":
            response_code = 500
        else:
            try:
                response_code = int(self.path[1:])
            except Exception:
                response_code = 201

        try:
            self.send_response(response_code)
            self.wfile.write('Content-Type: application/json\n')
            self.wfile.write('Client: %s\n' % str(self.client_address))
            self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
            self.wfile.write('Path: %s\n' % self.path)

            self.end_headers()

            content_len = int(self.headers.getheader('content-length', 0))
            raw_body = self.rfile.read(content_len)

            self._print_body(raw_body)

            self.wfile.write(raw_body)

        except Exception as e:
            self.send_response(500)

    def _print_body(self, raw_body):
        body = json.loads(raw_body)
        body = json.dumps(body,
                          ensure_ascii=False,
                          indent=4,
                          sort_keys=True)

        formatter = self._get_formatter()
        lexer = self._get_lexer()
        print pygments.highlight(body, lexer, formatter)


    def _get_formatter(self):
        style_class = pygments.styles.get_style_by_name('monokai')
        return Terminal256Formatter(style=style_class)


    def _get_lexer(self):
        return pygments.lexers.get_lexer_by_name('json')


server = HTTPServer(("localhost", PORT), JSONRequestHandler)
server.serve_forever()
