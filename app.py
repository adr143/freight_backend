from flask import Flask, request, jsonify, send_from_directory
from agents.vendor_email import send_email_to_all_vendors, simulate_send_email_to_all_vendor
from agents.markup import apply_markup
from agents.quote_summarizer import generate_quote_summary
from agents.pdf_generator import generate_pdf
from agents.logger import log_to_gsheet
import os

app = Flask(__name__)

@app.route("/api/quote", methods=["POST"])
def process_quote():
    data = request.json

    quotes = simulate_send_email_to_all_vendor(data)
    quotes = apply_markup(quotes)
    summary = generate_quote_summary(data, quotes)
    pdf_path = generate_pdf(data, quotes, summary)
    log_to_gsheet(data, quotes, summary)

    return jsonify({
        "status": "success",
        "summary": summary,
        "pdf_path": pdf_path,
        "quotes": quotes
    })

@app.route('/quotes/<filename>')
def serve_pdf(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'quotes'), filename)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
