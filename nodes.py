from flask import Flask, request, jsonify
import requests
import time
import threading
token_lock = threading.Lock()

app = Flask(__name__)

# Sequence numbers for each node (1-indexed)
RN_i = [0, 0, 0]

shared_file = "file.txt"


@app.route("/request_token", methods=["POST"])
def request_token():
    node_id = request.json.get("node_id")
    # Increment the request number for this node
    RN_i[node_id - 1] += 1
    sn = RN_i[node_id - 1]

    # Request the token from the token server
    response = requests.post(
        "http://localhost:5000/request_token", json={"node_id": node_id, "sn": sn})
    return jsonify(response.json()), response.status_code


@app.route("/write_to_file", methods=["POST"])
def write_to_file():
    node_id = request.json.get("node_id")
    data = request.json.get("data")

    # Check if this node holds the token
    response = requests.get("http://localhost:5000/check_token")
    if response.json()["token_holder"] != node_id:
        return jsonify({"status": "does not have token"}), 403

    # Perform the write operation in the critical section
    with open(shared_file, "a") as f:
        f.write(f"{data}\n")

    # Simulate time in the critical section
    time.sleep(2)

    # Release the token after completing operations
    requests.post("http://localhost:5000/release_token",
                  json={"node_id": node_id})
    return jsonify({"status": "data written, token released"}), 200


@app.route("/read_from_file", methods=["GET"])
def read_from_file():
    node_id = request.json.get("node_id")

    # Check if this node holds the token
    response = requests.get("http://localhost:5000/check_token")
    if response.json()["token_holder"] != node_id:
        return jsonify({"status": "does not have token"}), 403

    # Read from the shared file
    with open(shared_file, "r") as f:
        content = f.read()

    # Release the token after reading
    requests.post("http://localhost:5000/release_token",
                  json={"node_id": node_id})
    return jsonify({"status": "data read", "content": content}), 200


@app.route("/show_request_numbers", methods=["GET"])
def show_request_numbers():
    # Return the current RN_i values in JSON format
    with token_lock:
        return jsonify({"RN_i": RN_i}), 200


# Run the Flask-based node client
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python node_client.py <node_id>")
        sys.exit(1)

    node_id = int(sys.argv[1])

    app.run(port=8000 + node_id, debug=True)
