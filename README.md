# Riders Helmet Surveillance

Automatic detection of motorcyclists **not wearing helmets** from toll-plaza survey videos, with case evidence saved to disk and MongoDB.

The pipeline is: a custom **YOLOv3 (Darknet)** detector locates bikes and number plates in the video stream; a **CNN classifier** then inspects the rider's head region to check for a helmet. When a rider is found without a helmet, the frame evidence (bike, number plate, rider, rider-head crops) is written to a time-stamped case folder, which is later uploaded to MongoDB.

## How it works

```
survey video (.mp4)
        │  cv2.dnn — YOLOv3 detection (bike + number plate, 2-class)
        ▼
bike & plate bounding boxes
        │  CNN (helmet-nonhelmet_cnn.h5) on the rider-head region
        ▼
helmet   →  ignore
no helmet →  save case: Cases/<location>/ACN<datetime><rand>/
             bike.jpg · numberplate.jpg · rider.jpg · rider_head.jpg
        │  cases/Database_Feeder.py
        ▼
MongoDB (helmet_surv.surv_data, base64 images, fine = "Not Paid")
        │  cases/Database_Retriever.py (by accusation number)
        ▼
case folder reconstructed
```

## Repository structure

```
rider-helmet-detection/
├── Helmet_detect.py          # YOLOv3 + CNN helmet-surveillance loop
├── yolov3-custom.cfg         # 2-class Darknet/YOLOv3 config (bike, number plate)
├── run_detection.ipynb       # notebook launcher (%run Helmet_detect.py)
├── cases/
│   ├── Database_Feeder.py    # uploads case folders to MongoDB, then cleans them
│   └── Database_Retriever.py # looks up an accusation number and rebuilds the case folder
├── requirements.txt
└── .gitignore
```

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies: OpenCV (`opencv-python`), NumPy, `imutils`, TensorFlow/Keras (for the CNN model), PyMongo, and Jupyter for the notebook.

## Prerequisites

These trained model files are **not committed** (large) and must be supplied before running:

- `yolov3-custom_7000.weights` — YOLOv3 weights trained for the two classes (bike, number plate). Referenced alongside `yolov3-custom.cfg`.
- `helmet-nonhelmet_cnn.h5` — the CNN that classifies the rider's head region as helmet / non-helmet.

Place both next to `Helmet_detect.py` (or update the load paths in the script).

## Running

1. Start a MongoDB instance (needed only for the database scripts).
2. Edit the hard-coded machine-specific paths in `Helmet_detect.py`,
   `cases/Database_Feeder.py`, and `cases/Database_Retriever.py` to match your setup:
   - `save_dir` / `parent_dir` (case cache location)
   - `location` and the `.mp4` video path for the surveillance stream
3. Run the detection:

```bash
jupyter notebook   # open run_detection.ipynb
# or
python Helmet_detect.py
```

Cases are written to `Cases/<location>/ACN<timestamp>/`. After recording, feed them to the database:

```bash
cd cases
python Database_Feeder.py
```

and retrieve a specific case later with:

```bash
python Database_Retriever.py
```

## Notes and known limitations

- The detection loop uses the **CUDA** backend (`cv2.dnn.DNN_BACKEND_CUDA` / `DNN_TARGET_CUDA`) and expects a GPU; on CPU-only machines change the backend/target.
- All three scripts contain machine-specific absolute paths (`C:/Users/...`) and the survey videos are loaded from hard-coded locations — update them before running.
- The 5 toll-survey videos used for the demo and the recorded case photos are **removed from the repository** (size and privacy: they contain real riders and license plates). Re-run on your own footage.
- No custom license is included; Darknet/YOLOv3 and OpenCV carry their own licenses.

## Possible future improvements

These were part of the broader internship scope but are **not present in the committed code** — listed here for future development:

- **Number-plate recognition (ANPR/OCR)** — the plate is currently only detected and cropped as evidence; add OCR (e.g. Tesseract/EasyOCR) to also extract the plate text.
- **Challan web portal** — a Flask web layer (admin dashboard + rider portal) to replace the CLI `Database_Retriever` flow: view cases, check fine status, and manage accusations online.
- **Online payment** — integrate a payment gateway (e.g. Razorpay in test mode) so riders can pay fines tied to their unique accusation number.
- **SMS notifications** — notify riders via an SMS service (e.g. Twilio) with case details (timestamp, location, vehicle).
- **Vehicle verification** — validate plate ownership against a government registry (e.g. Parivahan API).
- **Cloud evidence storage** — offload case images to object storage (MinIO/S3/Azure) and keep only metadata in MongoDB.
- **Real-time processing** — the detector currently reads a recorded `.mp4`; support live camera streams (RTSP/Webcam) for true real-time operation.
- **Config-driven setup** — replace the hard-coded absolute paths, model files, location, and CUDA backend with a config file so the pipeline runs without code edits.