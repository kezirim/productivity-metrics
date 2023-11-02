import os
import tempfile
from fpdf import FPDF
import matplotlib.pyplot as plt
import logging

import controller as Controller

logger = logging.getLogger("MetricsLogger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("report-gen.log")
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

METRIC_MAPPING = {
    "Closed Issues": "closed_issues",
    "Open Issues": "open_issues",
    "Merged Pull Requests": "merged_prs",
    "Open Pull Requests": "open_prs",
    "Issue Cycle Time": "issue_cycle_time",
    "Code Review Time": "code_review_time",
    "Commits": "commits",
    "Lines of Code": "lines_of_code",
}


class ReportGenerator:
    def __init__(self, report_metrics):
        self.report_metrics = report_metrics

    def generate_report(self):
        metrics_data = {}
        for metric in METRIC_MAPPING:
            metrics_data[metric] = {"last_modified": []}

        # Prep data for report
        for row in self.report_metrics:
            username = row["username"]
            last_modified = row["last_modified"].strftime("%m/%d/%Y")
            for metric in METRIC_MAPPING:
                if username not in metrics_data[metric]:
                    metrics_data[metric][username] = []
                col_name = METRIC_MAPPING[metric]
                metrics_data[metric][username].append(row[col_name])
                if last_modified not in metrics_data[metric]["last_modified"]:
                    metrics_data[metric]["last_modified"].append(last_modified)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("arial", "B", 15)
        pdf.cell(75, 10, "Productivity Report", 0, 2, "C")

        # Create temp folder to store images
        temp_dir = tempfile.mkdtemp()

        for metric, data in metrics_data.items():
            plt.figure(figsize=(8, 4))
            for key in data:
                if key != "last_modified":
                    plt.plot(data["last_modified"], data[key], marker="o", label=key)
            plt.xlabel("Last Modified")
            plt.ylabel(metric)
            plt.title(f"{metric} Productivity Metrics")
            plt.legend()

            image_filename = f"{temp_dir}/chart_{metric}.png"
            plt.savefig(image_filename)
            plt.close()
            pdf.image(image_filename, x=10, y=None, w=190)

        # Save the PDF
        pdf_output = pdf.output(dest="S").encode("latin1")

        # Clean up
        self.remove_directory_and_files(temp_dir)

        return pdf_output

    def remove_directory_and_files(self, directory):
        if not os.path.exists(directory):
            return
        try:
            files = os.listdir(directory)
            for file in files:
                file_path = os.path.join(directory, file)
                os.remove(file_path)

            os.rmdir(directory)
        except OSError as e:
            logger.error(e)
