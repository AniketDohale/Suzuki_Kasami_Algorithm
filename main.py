from flask import Flask, request, jsonify
import queue
import threading

app = Flask(__name__)


token_holder = 1  # Initially, Node 1 holds the token
token_sn = [0, 0, 0]
request_queue = queue.Queue()
token_lock = threading.Lock()


@app.route("/request_token", methods=["POST"])
def request_token():
    # Get node ID and sequence number from the JSON body
    node_id = request.json.get("node_id")
    sn = request.json.get("sn")

    # Ensure that `node_id` and `sn` are not `None`
    if node_id is None or sn is None:
        return jsonify({"error": "Invalid data. `node_id` or `sn` missing"}), 400

    with token_lock:
        # Check if the request is outdated
        if token_sn[node_id - 1] >= sn:
            return jsonify({"status": "outdated request"}), 400

        # Update the sequence number for this node
        token_sn[node_id - 1] = sn

        # Add node to the queue if it's not already there
        if node_id not in list(request_queue.queue):
            request_queue.put(node_id)
            return jsonify({"status": "token requested"}), 200
        return jsonify({"status": "already requested"}), 200


@app.route("/release_token", methods=["POST"])
def release_token():
    global token_holder
    with token_lock:
        if not request_queue.empty():
            token_holder = request_queue.get()
            token_sn[token_holder - 1] += 1
            return jsonify({"status": "token released", "new_holder": token_holder}), 200
        return jsonify({"status": "no requests in queue"}), 200


@app.route("/check_token", methods=["GET"])
def check_token():
    with token_lock:
        queue_list = list(request_queue.queue)
    return jsonify({"token_holder": token_holder, "queue": queue_list}), 200


# Start the Flask server
if __name__ == "__main__":
    app.run(port=5000, debug=True)
