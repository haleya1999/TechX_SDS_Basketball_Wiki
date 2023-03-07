from flask import render_template
from flaskr.backend import Backend
def make_endpoints(app):
    backend = Backend()
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template('main.html')
    @app.route("/pages")
    def pages():
        pages = backend.get_all_page_names()
        return render_template('pages.html', pages=pages)

    @app.route("/about")
    def about():
        haley = backend.get_image('ironheart.jpg')
        #khloe = backend.get_image() -> add image
        #maize = backend.get_image() -> add image
        return render_template('about.html', haley_img = haley)

    @app.route("/login")
    def login():
        return render_template('login.html')

    @app.route("/signup")
    def signup():
        return render_template('signup.html')
    # TODO(Project 1): Implement additional routes according to the project requirements.
