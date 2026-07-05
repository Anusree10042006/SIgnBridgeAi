from models import History
from database import db
from datetime import datetime

import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

# Load trained model
model = load_model("backend/models/modelfinal.h5")

# Labels
labels = [
    "A","B","C","D","E","F","G","H","I","J",
    "K","L","M","N","O","P","Q","R","S","T",
    "U","V","W","X","Y","Z","SPACE","DELETE","NOTHING"
]

# MediaPipe
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


def start_camera():

    sentence = ""
    last_prediction = ""
    stable_count = 0

    cap = cv2.VideoCapture(0)

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands.process(rgb)

        prediction = ""

        if result.multi_hand_landmarks:

            for hand in result.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    hand,
                    mp_hands.HAND_CONNECTIONS
                )

                # Create input (63 values)
                data = []

                for lm in hand.landmark:
                    data.extend([lm.x, lm.y, lm.z])

                data = np.array(data).reshape(1, 63, 1)

                pred = model.predict(data, verbose=0)

                index = np.argmax(pred)

                prediction = labels[index]

                # Stable prediction
                if prediction == last_prediction:
                    stable_count += 1
                else:
                    stable_count = 0
                    last_prediction = prediction

                # Accept prediction after 15 frames
                if stable_count >= 15:

                    if prediction == "SPACE":

                        sentence += " "

                    elif prediction == "DELETE":

                        if len(sentence) > 0:
                            sentence = sentence[:-1]

                    elif prediction != "NOTHING":

                        sentence += prediction

                        # Save to database
                        history = History(
                            text=sentence,
                            date=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                        )

                        db.session.add(history)
                        db.session.commit()

                    stable_count = 0

        # Display current letter
        cv2.putText(
            frame,
            "Letter : " + prediction,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Display sentence
        cv2.putText(
            frame,
            "Word : " + sentence,
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

        # Instructions
        cv2.putText(
            frame,
            "C = Clear | Q = Quit",
            (20, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.imshow("SignBridge AI", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            sentence = ""

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()