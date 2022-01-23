import os

from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    '''Handle HTTP requests by returning a fixed 'page'.'''

    # Page to send back.
    Page = '''\
<html>
<body>
<table>
<tr>  <td>Header</td>         <td>Value</td>          </tr>
<tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
<tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
<tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
<tr>  <td>Command</td>        <td>{command}</td>      </tr>
<tr>  <td>Path</td>           <td>{path}</td>         </tr>
</table>
</body>
</html>
'''

    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """
    
    # Handle a GET request
    def do_GET(self):
        # print(os.getcwd())  # this is from where the python cmd is executed
        try:
            # library always assigns path as self.path (with leading '/')
            full_path = os.getcwd() + self.path
            if not os.path.exists(full_path):
                raise ServerException(f"'{self.path}' not found")
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            else:
                raise ServerException(f"Unknown object: '{self.path}'")
        except Exception as e:
            self.handle_error(e)
    
    
    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as infile:
                content = infile.read()
            self.send_content(content)
        except IOError as e:
            e = f"'{self.path}' cannot be read: {e}"
            self.handle_error(e)


    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode(), 404)  # why the need to encode here? needs to be a bytes object?
    
    
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)  # no need to encode here?

    
    def create_page(self):
        values = {
            'date_time': self.date_time_string(),
            'client_host': self.client_address[0],
            'client_port': self.client_address[1],
            'command': self.command,
            'path': self.path
        }
        page = self.Page.format(**values)
        return page
    

    def send_page(self, page):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page.encode())
    

class ServerException(Exception):
    pass


if __name__ == '__main__':
    serverAddress = ('', 8787)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()