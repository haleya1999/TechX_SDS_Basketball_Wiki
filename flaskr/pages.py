from flask import render_template, request, redirect
from flaskr.backend import Backend
import os
from werkzeug.utils import secure_filename

def make_endpoints(app):
    backend = Backend()
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template('main.html', user = backend.user)
    @app.route("/pages")
    def pages():
        pages = backend.get_all_page_names()
        return render_template('pages.html', pages=pages, user = backend.user)

    @app.route("/about")
    def about():
        haley = backend.get_image('ironheart.jpg')
        khloe = backend.get_image('HeadshotKhloeWrightFINAL.jpg')
        maize = backend.get_image('anon.png')
        return render_template('about.html', haley_img = haley, khloe_img = khloe, maize_img = maize, user = backend.user)

    @app.route("/upload", methods=['Get', 'POST'])
    def upload_file():
        if request.method == 'POST':
            allowed_extensions = {"txt", "jpg", "jpeg", "png", "gif"}
        # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file
            if file.filename == '':
                return redirect(request.url)
            if file and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                filename = secure_filename(file.filename)
                file.save(os.path.abspath(filename))
                backend.upload(file.filename)
                return redirect(request.url)
        return render_template('uploads.html', user = backend.user)
        
    @app.route("/login")
    def login():
        return render_template('login.html')

    @app.route("/signup")
    def signup():
        return render_template('signup.html')
    # TODO(Project 1): Implement additional routes according to the project requirements.
