from flask import Flask, jsonify, request
from modules.logger import fetch_logs
from main import process_incoming_emails

app = Flask(__name__)

@app.route('/logs', methods=['GET'])
def get_logs():
    logs = fetch_logs(100)
    # Convert tuples to dicts
    keys = ['uid','sender','city','timestamp','attachments','status']
    return jsonify([dict(zip(keys, row)) for row in logs])

@app.route('/trigger', methods=['POST'])
def trigger():
    try:
        process_incoming_emails()
        return 'Processing triggered', 200
    except Exception as e:
        return str(e), 500

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)