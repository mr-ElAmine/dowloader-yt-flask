# By moi
from website import create_app
from wsgiref.simple_server import make_server

app = create_app()

if __name__ == '__main__':
    #app.run(debug=True)
    
    httpd = make_server('', 5000, create_app())
    httpd.serve_forever()
    httpd.handle_request()