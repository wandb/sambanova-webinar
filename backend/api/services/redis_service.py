import redis
from typing import Any, Dict, List
from .encryption_service import EncryptionService

class SecureRedisService:
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize the secure Redis service.
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.encryption = EncryptionService()

    def ping(self) -> bool:
        """
        Ping the Redis server.
        
        Returns:
            bool: True if successful
        """
        return self.redis.ping()

    def set(self, key: str, value: Any, user_id: str) -> bool:
        """
        Set a value in Redis with encryption.
        
        Args:
            key: Redis key
            value: Value to store
            user_id: User ID for encryption key derivation
            
        Returns:
            bool: True if successful
        """
        encrypted_value = self.encryption.encrypt(value, user_id)
        return self.redis.set(key, encrypted_value)

    def get(self, key: str, user_id: str) -> Any:
        """
        Get and decrypt a value from Redis.
        
        Args:
            key: Redis key
            user_id: User ID for decryption key derivation
            
        Returns:
            Decrypted value
        """
        encrypted_value = self.redis.get(key)
        if encrypted_value is None:
            return None
        return self.encryption.decrypt(encrypted_value, user_id)

    def hset(self, name: str, mapping: Dict[str, Any], user_id: str) -> int:
        """
        Set multiple hash fields with encryption.
        
        Args:
            name: Hash name
            mapping: Dictionary of field/value pairs
            user_id: User ID for encryption key derivation
            
        Returns:
            int: Number of fields that were added
        """
        encrypted_mapping = self.encryption.encrypt_dict(mapping, user_id)
        return self.redis.hset(name, mapping=encrypted_mapping)

    def hget(self, name: str, key: str, user_id: str) -> Any:
        """
        Get and decrypt a hash field.
        
        Args:
            name: Hash name
            key: Field name
            user_id: User ID for decryption key derivation
            
        Returns:
            Decrypted value
        """
        encrypted_value = self.redis.hget(name, key)
        if encrypted_value is None:
            return None
        return self.encryption.decrypt(encrypted_value, user_id)

    def hgetall(self, name: str, user_id: str) -> Dict[str, Any]:
        """
        Get and decrypt all fields in a hash.
        
        Args:
            name: Hash name
            user_id: User ID for decryption key derivation
            
        Returns:
            dict: Dictionary of decrypted field/value pairs
        """
        encrypted_dict = self.redis.hgetall(name)
        if not encrypted_dict:
            return {}
        return self.encryption.decrypt_dict(encrypted_dict, user_id)

    def sadd(self, name: str, *values: str, user_id: str) -> int:
        """
        Add encrypted values to a set.
        
        Args:
            name: Set name
            *values: Values to add
            user_id: User ID for encryption key derivation
            
        Returns:
            int: Number of elements added
        """
        encrypted_values = [self.encryption.encrypt(v, user_id) for v in values]
        return self.redis.sadd(name, *encrypted_values)

    def smembers(self, name: str, user_id: str) -> set:
        """
        Get and decrypt all members of a set.
        
        Args:
            name: Set name
            user_id: User ID for decryption key derivation
            
        Returns:
            set: Set of decrypted values
        """
        encrypted_values = self.redis.smembers(name)
        if not encrypted_values:
            return set()
        return {self.encryption.decrypt(v, user_id) for v in encrypted_values}

    def zadd(self, name: str, mapping: Dict[str, float], user_id: str) -> int:
        """
        Add encrypted values to a sorted set.
        
        Args:
            name: Sorted set name
            mapping: Dictionary of member/score pairs
            user_id: User ID for encryption key derivation
            
        Returns:
            int: Number of elements added
        """
        encrypted_mapping = {
            self.encryption.encrypt(k, user_id): v 
            for k, v in mapping.items()
        }
        return self.redis.zadd(name, encrypted_mapping)

    def zrevrange(self, name: str, start: int, end: int, user_id: str) -> List[str]:
        """
        Get and decrypt a range of members from a sorted set by index.
        
        Args:
            name: Sorted set name
            start: Start index
            end: End index
            user_id: User ID for decryption key derivation
            
        Returns:
            list: List of decrypted values
        """
        encrypted_values = self.redis.zrevrange(name, start, end)
        if not encrypted_values:
            return []
        
        # Decrypt the values and convert bytes to strings if needed
        decrypted_values = []
        for v in encrypted_values:
            decrypted = self.encryption.decrypt(v, user_id)
            # Convert bytes to string if the decrypted value is bytes
            if isinstance(decrypted, bytes):
                decrypted = decrypted.decode('utf-8')
            decrypted_values.append(decrypted)
        
        return decrypted_values

    def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: Redis key
            
        Returns:
            bool: True if key exists
        """
        return bool(self.redis.exists(key))

    def delete(self, *names: str) -> int:
        """
        Delete one or more keys.
        
        Args:
            *names: Key names to delete
            
        Returns:
            int: Number of keys deleted
        """
        return self.redis.delete(*names)

    def lrange(self, name: str, start: int, end: int, user_id: str) -> List[Any]:
        """
        Get and decrypt a range of elements from a list.
        
        Args:
            name: List name
            start: Start index
            end: End index
            user_id: User ID for decryption key derivation
            
        Returns:
            list: List of decrypted values
        """
        encrypted_values = self.redis.lrange(name, start, end)
        if not encrypted_values:
            return []
        return [self.encryption.decrypt(v, user_id) for v in encrypted_values]

    def rpush(self, name: str, value: Any, user_id: str) -> int:
        """
        Append one or more values to a list, encrypting them first.
        
        Args:
            name: List name
            value: Value to append
            user_id: User ID for encryption key derivation
            
        Returns:
            int: Length of list after push
        """
        encrypted_value = self.encryption.encrypt(value, user_id)
        return self.redis.rpush(name, encrypted_value)

    def pubsub(self, **kwargs) -> redis.client.PubSub:
        """
        Return a pubsub object.
        
        Args:
            **kwargs: Arguments to pass to Redis pubsub
            
        Returns:
            PubSub: Redis PubSub object
        """
        return self.redis.pubsub(**kwargs)

    def publish(self, channel: str, message: Any) -> int:
        """
        Publish a message to a channel. Note: No encryption is used for pub/sub
        as channels are already user-scoped and messages are transient.
        
        Args:
            channel: Channel to publish to
            message: Message to publish
            
        Returns:
            int: Number of clients that received the message
        """
        return self.redis.publish(channel, message)

    def sismember(self, name: str, value: Any, user_id: str) -> bool:
        """
        Check if value is a member of set.
        
        Args:
            name: Set name
            value: Value to check
            user_id: User ID for encryption key derivation
            
        Returns:
            bool: True if member exists in set
        """
        encrypted_value = self.encryption.encrypt(value, user_id)
        return bool(self.redis.sismember(name, encrypted_value))

    def srem(self, name: str, value: Any, user_id: str) -> int:
        """
        Remove value from set.
        
        Args:
            name: Set name
            value: Value to remove
            user_id: User ID for encryption key derivation
            
        Returns:
            int: Number of elements removed
        """
        encrypted_value = self.encryption.encrypt(value, user_id)
        return self.redis.srem(name, encrypted_value)

    def zrem(self, name: str, *values: Any, user_id: str) -> int:
        """
        Remove one or more members from a sorted set.
        
        Args:
            name: Sorted set name
            *values: Values to remove
            user_id: User ID for encryption key derivation
            
        Returns:
            int: Number of members removed
        """
        encrypted_values = [self.encryption.encrypt(v, user_id) for v in values]
        return self.redis.zrem(name, *encrypted_values) 