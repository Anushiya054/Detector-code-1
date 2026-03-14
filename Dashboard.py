from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime
import os
import base64
import time
app = Flask(__name__)
alerts = []
latest_frame_jpg = No
camera_active = True
@app.route('/')
def index();
    sorted_alerts = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
    return render_template('index.html', alerts=sorted_alerts, camera_active=camera_active)
@app.route('/api/camera_status', methods=['GET'])
def get_camera_status():
    return jsonify({"active": camera_active})
@app.route('/api/toggle_camera', methods=['POST'])
def toggle_camera():
    global camera_active
    camera_active = not camera_active
    return jsonify({"active": camera_active})

@app.route('/api/frame', methods=['POST'])
def receive_frame():
    """Receives continuous frame updates from detect.py."""
    global latest_frame_jpg
    try:
        data = request.json
        if data and 'image' in data:
            # We receive base64, so we decode it back to raw bytes for the MJPEG stream
            latest_frame_jpg = base64.b64decode(data['image'])
        return jsonify({"status": "ok"}), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 500
def generate_frames():
    """Generator function that yields the latest frame as an MJPEG stream."""
    while True:
        if latest_frame_jpg is not None:
            # Yield the frame in the MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame_jpg + b'\r\n')
        # If no frame just sleep briefly to avoid pegging CPU
        time.sleep(0.05)
@app.route('/video_feed')
def video_feed():
    """Route that serves the actual video stream to the HTML."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/api/alert', methods=['POST'])
def receive_alert():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        drug_class = data.get('class', 'Unknown')
        confidence = data.get('confidence', 0.0)
        image_base64 = data.get('image', '')
        alert = {
            'id': len(alerts) + 1,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'class': drug_class,
            'confidence': f"{float(confidence):.2f}",
            'image': image_base64
        }  
        alerts.append(alert)
        if len(alerts) > 50:
             alerts.pop(0)
        print(f" ALERT RECEIVED: Detected {drug_class} ({confidence}%)")
        return jsonify({"status": "success", "message": "Alert logged"}), 200
    except Exception as e:
        print("Error processing alert:", e)
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    print("Starting Main Dashboard on http://localhost:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)

        
