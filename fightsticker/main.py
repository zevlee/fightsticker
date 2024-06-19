from .application import Application


def main():
    app = Application(title="Fightsticker")
    return app.run()
