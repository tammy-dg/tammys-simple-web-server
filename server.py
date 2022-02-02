import argparse
import os
import sys

import pandas as pd

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
    
    # def __init__(self, args):
    #     if args.root_dir is not None:
    #         self.base_path = args.root
    #     else:
    #         self.base_path = os.getcwd()

    
    # Handle a GET request
    def do_GET(self):  # how is this called?
        args = _parse_args()  # feel like this can be handled somehwere else
        if args.root_dir is not None:
            base_dir = args.root_dir
        else:
            base_dir = os.getcwd() # this is from where the python cmd is executed
        try:
            # library always assigns path as self.path (with leading '/')
            full_path = base_dir + self.path
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
            file_extension = full_path.split('.')[-1]
            if file_extension == "png":
                self.send_content(content, "image/png")
            elif file_extension == "jpeg":  # TODO: doesn't catch all (i.e., .jpg)
                self.send_content(content, "image/jpeg")
            elif file_extension == "csv":
                content = self.convert_table_to_html(full_path)
                self.send_content(content.encode(), "text/html")
            else:
                self.send_content(content, "text/html")
        except IOError as e:
            e = f"'{self.path}' cannot be read: {e}"
            self.handle_error(e)


    def convert_table_to_html(self, file_path):
        content = pd.read_csv(file_path)
        html_table = content.to_html(index=False, justify="left")
        return html_table


    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode(), 404)  # need to convert str message to bytes with encod
    
    
    def send_content(self, content, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)  # no encode because already in bytes

    
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
    

def _parse_args():
    parser = argparse.ArgumentParser(description='Initiate a web server')
    parser.add_argument(
        '--root-dir', '-dir', help=f"The root directory to deploy the server. If not provided then it will be the current dir: '{os.getcwd()}'")
    args = parser.parse_args()
    return args

class ServerException(Exception):
    pass


if __name__ == '__main__':
    serverAddress = ('', 8787)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()