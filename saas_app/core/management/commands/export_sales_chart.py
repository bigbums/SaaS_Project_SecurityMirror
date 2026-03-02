import sys
# Force UTF-8 encoding for stdout/stderr so Unicode symbols like ₦ work on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


import datetime
import os
import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from saas_app.core.models import SaleItem


class Command(BaseCommand):
    help = "Export monthly revenue chart and email it to stakeholders"

    def add_arguments(self, parser):
        parser.add_argument("--no-email", action="store_true", help="Generate charts but do not send emails")
        parser.add_argument("--recipients", nargs="+", type=str, help="List of recipient email addresses")
        parser.add_argument("--subject", type=str, help="Custom subject line for the email")
        parser.add_argument("--format", nargs="+", choices=["png", "pdf"], default=["png", "pdf"],
                            help="Choose export formats (png, pdf). Default is both.")
        parser.add_argument("--log-file", type=str, default="reports/export_log.txt",
                            help="Custom path for the log file (default: reports/export_log.txt)")
        parser.add_argument("--output-dir", type=str, default="reports",
                            help="Directory where charts will be saved (default: reports/)")
        parser.add_argument("--chart-type", choices=["bar", "line", "stacked"], default="bar",
                            help="Choose chart type: bar, line, or stacked (default: bar)")
        parser.add_argument("--title", type=str, default="Monthly Revenue by Product vs Service",
                            help="Custom chart title (default: Monthly Revenue by Product vs Service)")
        parser.add_argument("--xlabel", type=str, default="Months", help="Custom label for the X-axis (default: Months)")
        parser.add_argument("--ylabel", type=str, default="Revenue (₦)",
                            help="Custom label for the Y-axis (default: Revenue (₦))")
        parser.add_argument("--colors", nargs="+", type=str, default=["skyblue", "lightgreen", "orange"],
                            help="Custom colors for Product, Service, and Total (default: skyblue lightgreen orange)")
        parser.add_argument("--include-total", action="store_true",
                            help="Include Total Revenue line/bar in the chart")

    def handle(self, *args, **kwargs):
        try:
            # --- Generate chart data ---
            monthly_items = (
                SaleItem.objects
                .annotate(month=TruncMonth("sale__created_at"))
                .values("month", "product__name", "service__name")
                .annotate(total=Sum("line_total"))
                .order_by("month")
            )

            months = sorted(set(entry["month"].strftime("%b %Y") for entry in monthly_items))
            product_totals, service_totals = [], []

            for m in months:
                product_total = sum(entry["total"] for entry in monthly_items
                                    if entry["month"].strftime("%b %Y") == m and entry["product__name"])
                service_total = sum(entry["total"] for entry in monthly_items
                                    if entry["month"].strftime("%b %Y") == m and entry["service__name"])
                product_totals.append(product_total)
                service_totals.append(service_total)

            # Convert Decimals to floats
            product_totals = [float(p) for p in product_totals]
            service_totals = [float(s) for s in service_totals]
            total_revenue = [p + s for p, s in zip(product_totals, service_totals)]

            # --- Ensure output directory exists ---
            output_dir = kwargs.get("output_dir")
            os.makedirs(output_dir, exist_ok=True)

            # --- Save files with timestamp ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_filename = os.path.join(output_dir, f"monthly_revenue_{timestamp}")

            # --- Plot chart based on chart-type ---
            chart_type = kwargs.get("chart_type")
            chart_title = kwargs.get("title")
            xlabel = kwargs.get("xlabel")
            ylabel = kwargs.get("ylabel")
            colors = kwargs.get("colors")
            include_total = kwargs.get("include_total")

            plt.figure(figsize=(10, 6))

            if chart_type == "bar":
                plt.bar(range(len(months)), product_totals, label="Product", color=colors[0])
                plt.bar(range(len(months)), service_totals, bottom=product_totals, label="Service", color=colors[1])
                if include_total:
                    plt.plot(range(len(months)), total_revenue, marker="o", label="Total", color=colors[2])
            elif chart_type == "line":
                plt.plot(months, product_totals, marker="o", label="Product", color=colors[0])
                plt.plot(months, service_totals, marker="o", label="Service", color=colors[1])
                if include_total:
                    plt.plot(months, total_revenue, marker="o", label="Total", color=colors[2])
            elif chart_type == "stacked":
                plt.bar(range(len(months)), product_totals, label="Product", color=colors[0])
                plt.bar(range(len(months)), service_totals, bottom=product_totals, label="Service", color=colors[1])
                if include_total:
                    plt.plot(range(len(months)), total_revenue, marker="o", label="Total", color=colors[2])

            plt.xticks(range(len(months)), months, rotation=45)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(chart_title)
            plt.legend()

            # Export in chosen formats
            exported_files = []
            if "png" in kwargs["format"]:
                png_file = f"{base_filename}.png"
                plt.savefig(png_file, dpi=300, bbox_inches="tight")
                exported_files.append(png_file)
            if "pdf" in kwargs["format"]:
                pdf_file = f"{base_filename}.pdf"
                plt.savefig(pdf_file, dpi=300, bbox_inches="tight")
                exported_files.append(pdf_file)

            # --- Email the files (only if --no-email not used) ---
            if not kwargs.get("no_email"):
                recipients = kwargs.get("recipients") or ["stakeholder1@example.com", "stakeholder2@example.com"]
                subject = kwargs.get("subject") or f"Monthly Revenue Report - {timestamp}"

                email = EmailMessage(
                    subject=subject,
                    body="Attached are the latest revenue charts.",
                    from_email="reports@yourdomain.com",
                    to=recipients,
                )
                for f in exported_files:
                    email.attach_file(f)
                email.send()

                log_msg = f"[{timestamp}] SUCCESS: Charts exported ({', '.join(kwargs['format'])}, chart={chart_type}, title={chart_title}, xlabel={xlabel}, ylabel={ylabel}, colors={colors}, include_total={include_total}) and emailed to {', '.join(recipients)}.\n"
            else:
                log_msg = f"[{timestamp}] SUCCESS: Charts exported ({', '.join(kwargs['format'])}, chart={chart_type}, title={chart_title}, xlabel={xlabel}, ylabel={ylabel}, colors={colors}, include_total={include_total}, no email sent).\n"

            # --- Write success log ---
            log_file = kwargs.get("log_file")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_msg)

            self.stdout.write(self.style.SUCCESS(f"Charts exported successfully ({', '.join(kwargs['format'])}, chart={chart_type}, include_total={include_total})!"))

        except Exception as e:
            log_file = kwargs.get("log_file")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now()}] ERROR: {str(e)}\n")

            self.stdout.write(self.style.ERROR(f"Failed: {str(e)}"))
