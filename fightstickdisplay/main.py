from .application import Application


def main():
    app = Application(title="Hello World")
    return app.run()
