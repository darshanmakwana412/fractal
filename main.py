from argparse import ArgumentParser
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

def hilbert(nIterations, i, x, y, px, py, quadrant, childNumber, rotation, oppositeDirection, inversion, margin, size, imgs, threshold):

    n = nIterations - i

    x = 2 * x if (quadrant == 0 or quadrant == 1) else 2 * x + 1
    y = 2 * y if (quadrant == 1 or quadrant == 2) else 2 * y + 1
    px = px if (quadrant == 0 or quadrant == 1) else px + size
    py = py if (quadrant == 1 or quadrant == 2) else py + size

    rotation += (-1 if inversion else 1) if childNumber == 0 else ( 0 if (childNumber == 1 or childNumber == 2) else (1 if inversion else -1))
    oppositeDirection += 0 if (childNumber == 1 or childNumber == 2) else 1
    inversion = inversion if (childNumber == 1 or childNumber == 2) else (not inversion)
    
    gray = imgs[n - 1][x, y] if (n - 1 > 0 and n - 1 < len(imgs)) else -1
    quadrants = []
    addInOppositeDirection = oppositeDirection % 2 == 1

    # If addInOppositeDirection is true then add quadrants in opposite direction
    for j in ([3, 2, 1, 0] if addInOppositeDirection else [0, 1, 2, 3]):
        rj = rotation + j if (rotation + j >= 0) else 4 + ((rotation + j) % 4)
        corner = rj % 4
        quadrants.append(corner)

    path = []

    if gray >= 0 and gray < 256 - threshold:

        for j in range(4):
            q = quadrants[j]
            path += hilbert(nIterations, i+1, x, y, px, py, q, j, rotation, oppositeDirection, inversion, margin, size / 2, imgs, threshold)
        
    else:

        for j in range(4):
            if quadrants[j] == 1:
                path.append((px + margin, py + margin))
            elif quadrants[j] == 0:
                path.append((px + margin, py + margin + size - 2 * margin))
            elif quadrants[j] == 3:
                path.append((px + margin + size - 2 * margin, py + margin + size - 2 * margin))
            elif quadrants[j] == 2:
                path.append((px + margin + size - 2 * margin, py + margin))

    return path

def main(args) -> None:

    total_path = []
    
    for layer in range(1):

        size = 2 ** (args.niters - 1)
        img = Image.open(args.img).convert("L").resize((size, size))
        img = img.rotate(-90)

        imgs = [np.array(img)]
        for _ in range(args.niters - 1):
            [h, w] = img.size
            img = img.resize((h//2, w//2))
            imgs.append(np.array(img, dtype=np.float32))

        path = hilbert(args.niters, 0, 0, 0, 0, 0, 1, 1, 0, 0, False, args.margin, args.size, imgs, args.threshold)
        total_path.append(path)
        fig, ax = plt.subplots(1, 1)

        for i in range(1, len(path)):
            [x1, y1] = path[i-1]
            [x2, y2] = path[i]
            ax.plot([x1, x2], [y1, y2], linewidth=0.5, color="blue")

        ax.autoscale_view()
        plt.savefig("out.png")

    if args.gcode != "":
        from gcode import GcodeWriter
        gc = GcodeWriter(args.gcode, 1)
        gc.convert_print(total_path)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--img", type=str, required=True, help="Path of the Image")
    parser.add_argument("-n", "--niters", type=int, default=6, help="Number of Iterations to perform")
    parser.add_argument("-m", "--margin", type=float, default=0, help="Margin Size")
    parser.add_argument("-s", "--size", type=int, default=1024, help="Size of the Fill")
    parser.add_argument("-t", "--threshold", type=int, default=21, help="Threshold for binarization")
    parser.add_argument("-g", "--gcode", type=str, default="", help="Path to save the gcode")
    args = parser.parse_args()
    main(args)