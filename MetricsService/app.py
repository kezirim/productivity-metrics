from flask import Flask, request, make_response, jsonify
import controller as Controller
from report_generator import ReportGenerator

logger = Controller.logger

app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to the productivity metrics API!"


@app.route("/report", methods=["GET"])
def generate_report():
    usernames = request.args.get("usernames")
    repository = request.args.get("repository")
    if repository:
        try:
            metrics = Controller.retrieve_historical_metrics(repository, usernames)
            report = ReportGenerator(metrics).generate_report()
            response = make_response(report)
            response.headers[
                "Content-Disposition"
            ] = "attachment; filename=generated_pdf.pdf"
            response.headers["Content-Type"] = "application/pdf"
            return response
        except Exception as e:
            logger.error(e)
            return jsonify(
                {
                    "error": "Error occurred while generating report. See logs for details."
                }
            )

    else:
        return jsonify({"error": "Repository is required. Please provide one."})


@app.route("/snapshot", methods=["GET"])
def get_metrics():
    username = request.args.get("username")
    repository = request.args.get("repository")

    # retrieve token from header
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]

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
