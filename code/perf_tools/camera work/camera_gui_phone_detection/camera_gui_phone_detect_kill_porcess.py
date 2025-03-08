import sys
import os
import cv2
import psutil  # <-- For enumerating and killing processes
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox
)

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera UI Example (Detect Cell Phone)")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Label to display video frames
        self.video_label = QLabel("Camera Feed", self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.video_label)

        # Status label to show detection info
        self.status_label = QLabel("No Phone Detected", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # Create horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Start/Stop camera buttons
        self.start_button = QPushButton("Start Camera", self)
        self.start_button.clicked.connect(self.start_camera)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera", self)
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        # Start/Stop recording buttons
        self.record_button = QPushButton("Start Recording", self)
        self.record_button.clicked.connect(self.start_recording)
        self.record_button.setEnabled(False)
        button_layout.addWidget(self.record_button)

        self.stop_record_button = QPushButton("Stop Recording", self)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.stop_record_button.setEnabled(False)
        button_layout.addWidget(self.stop_record_button)

        self.main_layout.addLayout(button_layout)

        # Initialize camera variables
        self.cap = None           # OpenCV VideoCapture
        self.timer = QTimer()     # Timer to update frames
        self.timer.timeout.connect(self.update_frame)

        self.is_recording = False
        self.out = None
        self.fps = 30

        # -----------------------------------------------------------
        # 1. LOAD YOLO MODEL FILES
        # -----------------------------------------------------------
        # Adjust these paths to where you've saved your YOLO files:
        script_dir = os.path.dirname(os.path.abspath(__file__))

        model_cfg = os.path.join(script_dir, "yolov3.cfg")
        model_weights = os.path.join(script_dir, "yolov3.weights")
        coco_names = os.path.join(script_dir, "coco.names")

        # Read class names from coco.names
        with open(coco_names, "r") as f:
            self.class_names = [cname.strip() for cname in f.readlines()]

        # Initialize DNN
        self.net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)

        # Optional: set preferable backend/target
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)  # or CUDA if available

        # Create a DetectionModel for easier usage
        self.model = cv2.dnn_DetectionModel(self.net)
        self.model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

        print("YOLO model loaded. Ready to detect cell phones.")

        # Track if we've already killed the Azure Virtual Desktop process
        self.already_killed = False

    def start_camera(self):
        """Open the default camera with DirectShow, fallback to default if needed."""
        if self.cap is not None and self.cap.isOpened():
            QMessageBox.warning(self, "Warning", "Camera is already running!")
            return

        print("Trying to open camera with DirectShow (CAP_DSHOW)...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("DirectShow failed. Trying default backend.")
            self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Cannot open camera (index 0).")
            self.cap = None
            return

        # Optionally set resolution
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.timer.start(int(1000 / self.fps))
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)

        print("Camera started successfully.")

    def stop_camera(self):
        """Stop updating frames and release the camera."""
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

        self.video_label.clear()
        self.status_label.setText("No Phone Detected")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.record_button.setEnabled(False)
        self.stop_record_button.setEnabled(False)

        if self.is_recording:
            self.stop_recording()

        print("Camera stopped.")

    def start_recording(self):
        """Initialize VideoWriter to start recording."""
        if not self.cap or not self.cap.isOpened():
            QMessageBox.warning(self, "Warning", "Camera is not running!")
            return

        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))
        self.is_recording = True

        self.record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)

        print(f"Recording started: {frame_width}x{frame_height}")

    def stop_recording(self):
        """Stop writing frames to the VideoWriter."""
        self.is_recording = False
        if self.out:
            self.out.release()
            self.out = None

        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        print("Recording stopped.")

    def kill_azure_app(self):
        """
        Kills any process whose exe path contains
        ''.
        Adjust the substring if the real path is different.
        """
        target_substring = r""

        print("Attempting to kill Azure Virtual Desktop process...")
        killed_any = False
        for proc in psutil.process_iter(['pid', 'exe']):
            exe_path = proc.info['exe']
            if exe_path and target_substring in exe_path:
                try:
                    proc.kill()
                    print(f"Killed process PID={proc.pid} exe={exe_path}")
                    killed_any = True
                except Exception as e:
                    print(f"Could not kill process PID={proc.pid}: {e}")

        if killed_any:
            # Show message once if we successfully killed at least one process
            QMessageBox.information(
                self,
                "Policy Enforcement",
                "Your organization prevents using phone while using logged in your remote environment."
            )

    def update_frame(self):
        """Grab a frame from the camera, detect cell phones, and display."""
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # 2. RUN YOLO DETECTION
        class_ids, confidences, boxes = self.model.detect(frame, confThreshold=0.5, nmsThreshold=0.4)

        found_phone = False
        for (class_id, confidence, box) in zip(class_ids, confidences, boxes):
            cname = self.class_names[class_id] if class_id < len(self.class_names) else None
            if cname == "cell phone":
                found_phone = True
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                label = f"{cname}: {confidence:.2f}"
                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Update status label
        if found_phone:
            self.status_label.setText("Cell Phone Detected!")
            # Attempt to kill the Azure app once
            if not self.already_killed:
                self.kill_azure_app()
                self.already_killed = True
        else:
            self.status_label.setText("No Phone Detected")

        # 3. RECORDING
        if self.is_recording and self.out is not None:
            self.out.write(frame)

        # 4. DISPLAY FRAME IN PyQt
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pix)

    def closeEvent(self, event):
        """Ensure resources are released if the user closes the window."""
        self.stop_camera()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
