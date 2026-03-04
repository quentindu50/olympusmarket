# Entry point for the ambulance/transport management application

import os
from app import create_app


def main():
    app = create_app()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()