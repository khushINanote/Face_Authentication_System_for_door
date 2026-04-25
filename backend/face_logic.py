import cv2
import numpy as np
import os
import base64
import face_recognition

class FaceProcessor:
    def __init__(self, db_path="database"):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        
        self.known_encodings = []
        self.known_names = []
        self.load_known_faces()

    def load_known_faces(self):
        """Load all registered faces into memory."""
        self.known_encodings = []
        self.known_names = []
        for filename in os.listdir(self.db_path):
            if filename.endswith(".jpg"):
                path = os.path.join(self.db_path, filename)
                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(filename.split('.')[0])
        print(f"Loaded {len(self.known_names)} registered faces.")

    def decode_image(self, base64_string):
        try:
            encoded_data = base64_string.split(',')[1] if ',' in base64_string else base64_string
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # face_recognition uses RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return rgb_img
        except Exception as e:
            print(f"Error decoding image: {e}")
            return None

    def check_liveness(self, img):
        """
        Refined Anti-Spoofing logic.
        Lowered threshold for better compatibility with diverse webcams.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        print(f"Liveness Check - Laplacian Variance: {laplacian_var}")
        
        # Lowered to 20 to be more permissive for lower-quality webcams
        if laplacian_var < 20:
            return False
        return True

    def register_face(self, user_id, img):
        file_path = os.path.join(self.db_path, f"{user_id}.jpg")
        bgr_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(file_path, bgr_img)
        print(f"Registered new face for: {user_id}")
        self.load_known_faces() 
        return True

    def authenticate(self, img):
        try:
            if not self.check_liveness(img):
                print("Authentication Failed: Spoof Detected")
                return {"status": "fail", "reason": "Spoof detected (Liveness Check Failed)"}

            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)

            if not face_encodings:
                print("Authentication Failed: No face detected in frame")
                return {"status": "fail", "reason": "No face detected"}

            print(f"Detected {len(face_encodings)} face(s) in frame. Comparing with {len(self.known_names)} known faces.")
            
            for face_encoding in face_encodings:
                # Tolerance 0.6 is the standard default for face_recognition
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.6)
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_names[first_match_index]
                    
                    face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    distance = face_distances[best_match_index]
                    
                    print(f"Authentication Successful: {name} (Distance: {distance})")
                    return {
                        "status": "success", 
                        "identity": name, 
                        "distance": float(distance)
                    }
            
            print("Authentication Failed: No matching face found")
            return {"status": "fail", "reason": "Face not recognized"}
        except Exception as e:
            print(f"Authentication error: {e}")
            return {"status": "error", "message": str(e)}

processor = FaceProcessor()
