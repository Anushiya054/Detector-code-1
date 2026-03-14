from ultralytics import YOLO
def main():
    model = YOLO("yolov8n.pt")  
    print("Starting training on dataset.yaml...")
    results = model.train(
        data="dataset.yaml",
        epochs=50,       
        imgsz=640,       
        batch=16,        
        device="cpu",     
        project="runs/detect",
        name="drug_detection_model"
    )
    print("Training finished! Best weights are saved in runs/detect/drug_detection_model/weights/best.pt")
if __name__ == "__main__":
    main()
