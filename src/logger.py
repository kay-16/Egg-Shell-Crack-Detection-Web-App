import csv
import os

CSV_FILE = "tap_logs44100.csv"

def log_egg_data(metadata, filename):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "filename",
                "fold",
                "target_status",
                "target",
                "point",
                "sv",
            ])

        writer.writerow([
            filename,
            metadata["fold"],
            metadata["target_status"],
            metadata["target"],
            metadata["point"],
            metadata["sv"],
        ])