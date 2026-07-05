from tensorflow.keras.models import load_model

model = load_model("backend/models/modelfinal.h5")

print("Input Shape :", model.input_shape)
print("Output Shape:", model.output_shape)