from ultralytics import YOLO


"""import torch

print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))
"""

def main():
    model = YOLO('yolov8s.pt')
    model.train(
        data='config.yaml',
        epochs=100,
        batch=16,
        imgsz=256,
        device='cuda',
        optimizer='AdamW',
        lr0= 0.002,
        lrf=0.1,
        weight_decay=0.0005,
        momentum=0.9,
        patience=10
    )

if __name__ == '__main__':
    main()

