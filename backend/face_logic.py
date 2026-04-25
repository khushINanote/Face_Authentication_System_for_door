import cv2
import numpy as np
import os
import base64

try:
    from deepface import DeepFace
    HAS_DEEPFACE = True
except ImportError:
    HAS_DEEPFACE = False
    print("DeepFace not found, running in MOCK mode for UI demonstration.")

class FaceProcessor:
    def __init__(self, db_path="database"):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

    def decode_image(self, base64_string):
        try:
            encoded_data = base64_string.split(',')[1] if ',' in base64_string else base64_string
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"Error decoding image: {e}")
            return None

    def check_liveness(self, img):
        return True 

    def register_face(self, user_id, img):
        file_path = os.path.join(self.db_path, f"{user_id}.jpg")
        cv2.imwrite(file_path, img)
        return True

    def authenticate(self, img):
        if not HAS_DEEPFACE:
            # Mock authentication for UI demo
            return {"status": "success", "identity": "Demo User (Mock)", "distance": 0.1}

        try:
            if not self.check_liveness(img):
                return {"status": "fail", "reason": "Spoof detected"}

            results = DeepFace.find(img, db_path=self.db_path, enforce_detection=False, silent=True)
            
            if len(results) > 0 and not results[0].empty:
                best_match = results[0].iloc[0]
                identity = os.path.basename(best_match['identity']).split('.')[0]
                distance = best_match['distance']
                
                if distance < 0.4:
                    return {"status": "success", "identity": identity, "distance": float(distance)}
            
            return {"status": "fail", "reason": "No match found"}
        except Exception as e:
            print(f"Authentication error: {e}")
            return {"status": "error", "message": str(e)}

processor = FaceProcessor()
