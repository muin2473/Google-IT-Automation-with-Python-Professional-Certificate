import json
import locale
import sys
import emails
import reports
import os
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def load_data(filename):
    """Loads the contents of filename as a JSON file."""
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def format_car(car):
    """Given a car dictionary, returns a nicely formatted name."""
    return "{} {} ({})".format(
        car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
    """Analyzes the data, looking for maximums.

    Returns a list of lines that summarize the information.
    """
    locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
    max_revenue = {"revenue": 0}
    max_sales = {'total_sales': 0}
    year = {}
    for item in data:
        # Calculate the revenue generated by this model (price * total_sales)
        # We need to convert the price from "$1234.56" to 1234.56
        item_price = locale.atof(item["price"].strip("$"))
        item_revenue = item["total_sales"] * item_price
        if item_revenue > max_revenue["revenue"]:
            item["revenue"] = item_revenue
            max_revenue = item

        if item["total_sales"] > max_sales["total_sales"]:
            max_sales = item
        if not item["car"]["car_year"]in year.keys():
            year[item["car"]["car_year"]] = item["total_sales"]
        else:
            year[item["car"]["car_year"]] = year[item["car"]
                                                 ["car_year"]]+item["total_sales"]

        # TODO: also handle max sales
        # TODO: also handle most popular car_year

    all_values = year.values()
    max_value = max(all_values)
    max_key = max(year, key=year.get)
#  print(max_value)

    summary = [
        "The {} generated the most revenue: ${}".format(
            format_car(max_revenue["car"]), max_revenue["revenue"]),
        "The {} had the most sales: {}".format(
            format_car(max_sales["car"]), max_sales["total_sales"]),
        "The most poular year was {} with {} sales.".format(max_key, max_value)
    ]
    return summary


def cars_dict_to_table(car_data):
    """Turns the data in car_data into a list of lists."""
    table_data = [["ID", "Car", "Price", "Total Sales"]]
    for item in car_data:
        table_data.append([item["id"], format_car(
            item["car"]), item["price"], item["total_sales"]])
    return table_data


def main(argv):
    """Process the JSON data and generate a full report out of it."""
    data = load_data("/home/student-03-93d8b896b999/car_sales.json")
    summary = process_data(data)
    print(summary)
    table_data = cars_dict_to_table(data)
    styles = getSampleStyleSheet()
    report = SimpleDocTemplate("//tmp/cars.pdf")
    report_title = Paragraph(". ".join(summary), styles["h1"])
    table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black)]
    report_table = Table(data=table_data, style=table_style, hAlign="LEFT")
    report.build([report_title, report_table])
    sender = "automation@example.com"

    receiver = "{}@example.com".format(os.environ.get('USER'))

    subject = "Sales summary for last month"

    body = summary

    message = emails.generate(sender, receiver, subject, body, "/tmp/cars.pdf")

    emails.send(message)

    # TODO: turn this into a PDF report

    # TODO: send the PDF report as an email attachment


if __name__ == "__main__":
    main(sys.argv)