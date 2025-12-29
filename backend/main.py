from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import boto3
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"}), 200

@app.route("/api/todos", methods=["GET"])
def list_todos():
    try:
        response = table.scan()
        return jsonify(response.get("Items", [])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/todos", methods=["POST"])
def create_todo():
    try:
        data = request.get_json()
        item = {
            "id": str(uuid.uuid4()),
            "title": data.get("title"),
            "done": False
        }
        table.put_item(Item=item)
        return jsonify(item), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/todos/<string:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    try:
        data = request.get_json()
        table.update_item(
            Key={"id": todo_id},
            UpdateExpression="SET title = :title, done = :done",
            ExpressionAttributeValues={
                ":title": data.get("title"),
                ":done": data.get("done")
            }
        )
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/todos/<string:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    try:
        table.delete_item(Key={"id": todo_id})
        return jsonify({"status": "deleted"}), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)