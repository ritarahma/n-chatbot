"""Run Project."""
from nflask import Nflask
# from werkzeug import SharedDataMiddleware

# Create new app
app = Nflask()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
