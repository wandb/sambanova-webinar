import redis
import json
import time
from typing import Any


class RedisConversationLogger:
    """
    Publishes each agent step to Redis pub/sub for real-time streaming.
    """
    def __init__(self, redis_host="localhost", redis_port=6379, user_id="", run_id="", agent_name=""):
        try:
            self.r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
            # Test connection
            self.r.ping()
            print(f"Redis connected successfully for {agent_name}")
        except redis.ConnectionError as e:
            print(f"Redis connection failed: {e}")
        
        # Ensure proper string conversion and handle potential JSON objects
        if isinstance(user_id, (dict, list)):
            try:
                self.user_id = json.dumps(user_id)
            except:
                self.user_id = str(user_id)
        else:
            self.user_id = str(user_id) if user_id else ""
            
        self.run_id = str(run_id) if run_id else ""
        self.agent_name = agent_name
        
        print(f"Initialized logger with user_id: {self.user_id}, run_id: {self.run_id}")  # Debug log

    def __call__(self, output: Any):
        try:
            if hasattr(output, 'text'):
                message = {
                    "user_id": self.user_id,
                    "run_id": self.run_id,
                    "agent_name": self.agent_name,
                    "text": output.text,
                    "timestamp": time.time()
                }
                channel = f"agent_thoughts:{self.user_id}:{self.run_id}"
                print(f"Publishing to channel (formatted): {channel}")  # Debug log
                print(f"Message content: {json.dumps(message)}")  # Debug log
                self.r.publish(channel, json.dumps(message))
        except Exception as e:
            print(f"Error publishing to Redis: {e}")
            print(f"Message attempted: {message if 'message' in locals() else 'No message created'}")

