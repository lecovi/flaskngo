from manage import app

if __name__ == "__main__":
    msg = " ".join(['DB:', app.config.get("SQLALCHEMY_DATABASE_URI")])
    app.logger.debug(msg)
    app.run(host='0.0.0.0', port=8000)
