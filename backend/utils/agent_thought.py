import redis
import json
import time
from typing import Any
import os

class RedisConversationLogger:
    """
    Publishes each agent step to Redis pub/sub for real-time streaming.
    Reads REDIS_HOST/REDIS_PORT from environment to handle local vs. Docker.
    """
    def __init__(self, user_id="", run_id="", agent_name=""):
        # Read from env or default
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        try:
            self.r = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=0,
                decode_responses=True
            )
            self.r.ping()
            print(f"[RedisConversationLogger] Connected to Redis at {redis_host}:{redis_port} for {agent_name}")
        except redis.ConnectionError as e:
            print(f"[RedisConversationLogger] Redis connection failed: {e}")
        
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
                self.r.publish(channel, json.dumps(message))
        except Exception as e:
            print(f"Error publishing to Redis: {e}")
            print(f"Message attempted: {message if 'message' in locals() else 'No message created'}")

