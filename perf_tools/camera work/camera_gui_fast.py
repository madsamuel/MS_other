"""
PyQt5 Camera UI (DirectShow Backend)
------------------------------------
This script creates a GUI to preview a webcam video using OpenCV (with DirectShow) 
and PyQt5. It supports:
- Starting/stopping the camera
- Real-time video preview
- Recording to an MP4 file
- Simple warm-up frames

Requirements:
  pip install opencv-python PyQt5
Tested on Windows. On other OSes, CAP_DSHOW likely won't work.
"""

import sys
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox
)

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera UI Example (DirectShow)")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Label to display video frames
        self.video_label = QLabel("Camera Feed", self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.video_label)

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
        self.cap = None            # OpenCV VideoCapture
        self.timer = QTimer()      # Timer to update frames
        self.timer.timeout.connect(self.update_frame)

        # For recording
        self.is_recording = False
        self.out = None

        # Desired frames per second for preview
        self.fps = 30

    def start_camera(self):
        """Open the default camera (index 0) with DirectShow. Fallback to default if it fails."""
        # If the camera is already running, don't start again
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

        # Optionally set a lower resolution for faster startup
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        # Warm up the camera by reading a few frames quickly
        # for _ in range(5):
        #     self.cap.read()

        # Start updating frames at ~30 FPS
        self.timer.start(int(1000 / self.fps))
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)

        print("Camera started successfully (DirectShow).")

    def stop_camera(self):
        """Stop updating frames and release the camera."""
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

        # Clear the video label
        self.video_label.clear()

        # Re-enable / disable buttons
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.record_button.setEnabled(False)
        self.stop_record_button.setEnabled(False)

        # If we were recording, stop it
        if self.is_recording:
            self.stop_recording()

        print("Camera stopped.")

    def start_recording(self):
        """Initialize the VideoWriter to start recording."""
        if not self.cap or not self.cap.isOpened():
            QMessageBox.warning(self, "Warning", "Camera is not running!")
            return

        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(
            'output.mp4', fourcc, 20.0,
            (frame_width, frame_height)
        )
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

    def update_frame(self):
        """Grab a frame from the camera and display it. If recording, write it to file."""
        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return  # skip if frame isn't valid

        # If recording, write the frame
        if self.is_recording and self.out is not None:
            self.out.write(frame)

        # Convert the frame (BGR -> RGB) for PyQt display
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        # Convert to QImage and display
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
