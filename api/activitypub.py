from typing import Dict, Any, Optional
from datetime import datetime
import json
import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from base64 import b64encode
from urllib.parse import urlparse
from fastapi import HTTPException

class ActivityPubProtocol:
    def __init__(self, domain: str, private_key: Optional[str] = None):
        self.domain = domain
        if private_key:
            self.private_key = serialization.load_pem_private_key(
                private_key.encode(),
                password=None
            )
        else:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )

    def get_public_key_pem(self) -> str:
        public_key = self.private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def sign_message(self, message: str) -> str:
        signature = self.private_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return b64encode(signature).decode()

    def create_story_activity(self, story: Dict[str, Any], author: Dict[str, Any]) -> Dict[str, Any]:
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "actor": f"https://{self.domain}/users/{author['username']}",
            "object": {
                "type": "Article",
                "id": f"https://{self.domain}/stories/{story['id']}",
                "attributedTo": f"https://{self.domain}/users/{author['username']}",
                "content": json.dumps({
                    "title": story["title"],
                    "takeoff": story["takeoff"],
                    "turbulence": story["turbulence"],
                    "touchdown": story["touchdown"]
                }),
                "published": datetime.utcnow().isoformat(),
                "to": ["https://www.w3.org/ns/activitystreams#Public"]
            }
        }
        return activity

    async def deliver_to_inbox(self, activity: Dict[str, Any], target_inbox: str) -> None:
        headers = {
            "Content-Type": "application/activity+json",
            "User-Agent": f"PMOT-Stories/{self.domain}",
        }
        
        date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        string_to_sign = f"(request-target): post {urlparse(target_inbox).path}\nhost: {urlparse(target_inbox).netloc}\ndate: {date}"
        signature = self.sign_message(string_to_sign)
        
        headers["Date"] = date
        headers["Signature"] = f'keyId="https://{self.domain}/users/{activity["actor"]}/key",headers="(request-target) host date",signature="{signature}"'

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(target_inbox, json=activity, headers=headers)
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise HTTPException(status_code=502, detail=f"Failed to deliver activity: {str(e)}")

    def process_incoming_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        if activity["type"] not in ["Create", "Update", "Delete", "Follow", "Accept", "Reject"]:
            raise HTTPException(status_code=400, detail="Unsupported activity type")
            
        # Process based on activity type
        if activity["type"] == "Create":
            return self.process_create_activity(activity)
        elif activity["type"] == "Follow":
            return self.process_follow_activity(activity)
        
        return {"status": "processed"}

    def process_create_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        if activity["object"]["type"] != "Article":
            raise HTTPException(status_code=400, detail="Unsupported object type")
            
        try:
            content = json.loads(activity["object"]["content"])
            return {
                "type": "Story",
                "title": content["title"],
                "takeoff": content["takeoff"],
                "turbulence": content["turbulence"],
                "touchdown": content["touchdown"],
                "remote_id": activity["object"]["id"],
                "remote_author": activity["actor"]
            }
        except (json.JSONDecodeError, KeyError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid content format: {str(e)}")

    def process_follow_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "Follow",
            "follower": activity["actor"],
            "following": activity["object"]
        }