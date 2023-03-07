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
    # TODO(Project 1): Implement additional routes according to the project requirements.
