from Application import Application


def main():
    app = Application(__name__)
    app.run(debug=True)


if __name__ == "__main__":
    main()
