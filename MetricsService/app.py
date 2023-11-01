from flask import Flask, request, jsonify
import controller as Controller

app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to the productivity metric API!"


# under development
@app.route("/report", methods=["GET"])
def generate_report():
    username = request.args.get("username")
    format = request.args.get("format")
    historical = request.args.get("historical") or True
    weekcount = request.args.gett("weekcount") or 1
    # generates from data in database - 1-week snapshot or historical metrics of n weeks
    return jsonify({"message": "OK"})


@app.route("/metrics", methods=["GET"])
def get_metrics():
    username = request.args.get("username")
    repository = request.args.get("repository")
    token = request.args.get("token")
    if username and repository:
        metrics = Controller.retrieve_metrics(username, repository, token)
        return jsonify({"developer": username, "metrics": metrics})
    else:
        return jsonify(
            {
                "error": "Both Github username and repository name are required. Please provide one."
            }
        )


if __name__ == "__main__":
    app.run(debug=True)
