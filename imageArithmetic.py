import numpy as np
import matplotlib.pyplot as plt
import cv2

history = []
log = []

def display_images(original, edited, title=""):
    
    plt.figure(figsize=(10, 5))
    
    plt.subplot(121)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title("Previous")
    plt.axis('off')
    
    plt.subplot(122)
    plt.imshow(cv2.cvtColor(edited, cv2.COLOR_BGR2RGB))
    plt.title("Edited")
    plt.axis('off')

    plt.tight_layout()
    plt.show()

def adjust_brightness(img, value):
    # result = cv2.add(img, np.ones(img.shape, dtype="uint8") * value)
    result = cv2.convertScaleAbs(img, alpha=1, beta=value)
    log.append(f"brightness {value:+}")
    return result

def adjust_contrast(img, value):
    #result = cv2.multiply(img, np.ones(img.shape, dtype='uint8'), scale=value)
    result = cv2.convertScaleAbs(img, alpha=value, beta=0)
    log.append(f"contrast x{value}")
    return result

def convert_to_gray(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    log.append("converted to grayscale")
    return result

def addjust_padding(img, pad_y, pad_x, borderType, target_ratio=None):
    border_map = {
        "constant" : cv2.BORDER_CONSTANT,
        "replicate": cv2.BORDER_REPLICATE,
        "reflect": cv2.BORDER_REFLECT
    }

    pad_top = pad_bottom = pad_y
    pad_left = pad_right = pad_x

    border_type = border_map.get(borderType)

    if target_ratio:
        w, h = img.shape[:2]
        current_ratio = w / h
        desired_ratio = target_ratio[0] / target_ratio[1]

        if current_ratio < desired_ratio:
            new_width = int(h * desired_ratio)
            extra = new_width - w
            pad_left = extra // 2
            pad_right = extra - pad_left
        else:
            new_height = int(w * (1 / desired_ratio))
            extra = new_height - h
            pad_top = extra // 2
            pad_bottom = extra - pad_top
    
    result = cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, border_type, value=[0, 0, 0])
    log.append(f"padded Top/Bottom:{pad_top}px Left/Right:{pad_left}px ({border_type}) ratio {target_ratio if target_ratio else 'none'}")
    return result

def apply_threshold(img, low=127, high=255, thresh_strategy=cv2.THRESH_BINARY):
    _, thresh = cv2.threshold(img, low, high, thresh_strategy)
    log.append(f"thresholding ({thresh_strategy})")
    return thresh

def blend(img1, img2, alpha=0.5):
    if img2.shape != img1.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    img3 = cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)
    #  img3 = ((1 - alpha) * img1 + alpha * img2).astype(np.uint8)
    log.append(f"blended using cv2.addWeighted with alpha={alpha}")
    return img3

def main():
    
    path = input("Enter the path to the image: ").strip()
    img = cv2.imread(path)
    if img is None:
        print("❌ Failed to load image.")
        return

    history.append(img.copy())

    while True:
        print("\n==== Mini Photo Editor ====")
        print("1. Adjust Brightness")
        print("2. Adjust Contrast")
        print("3. Convert to Grayscale")
        print("4. Add Padding (choose border type)")
        print("5. Apply Thresholding (binary or inverse)")
        print("6. Blend with Another Image (manual alpha)")
        print("7. Undo Last Operation")
        print("8. View History of Operations")
        print("9. Save and Exit")

        choice = input('Choose an option (1–9): ').strip()

        if choice == '1':

            value = int(input("Enter brightness adjustment (-100 to 100): "))

            if value < -100 or value > 100:
                print("❌ Invalid Input.")
                continue

            edited = adjust_brightness(history[-1], value)

        elif choice == '2':

            value =  float(input("Enter contrast multiplier (e.g., 1.2): "))

            edited = adjust_contrast(history[-1], value)

        elif choice == '3':

            edited = convert_to_gray(history[-1])

        elif choice == '4':

            pad_y = int(input("Enter Top/Bottom padding size: ")) 
            pad_x = int(input("Enter Left/Right padding size: "))        
       
            print("\nChoose the border type: ")
            print("1. Constant")
            print("2. Reflect")
            print("3. Replicate")
            choice = input("> ").strip()
            
            if choice == "1":
                 border_type = "constant"
            elif choice == "2":
                 border_type = "reflect"
            elif choice == "3":
                 border_type = "replicate"
            else:
                print("❌ Invalid option.")
                continue
                

            print("\nChoose the Target ratio: ")
            print("1. Square")
            print("2. Rectangle 4:3")
            print("3. Custome")
            print("4. None")
            choice = input("> ").strip()
            
            if choice == "1":
                 ratio = (1, 1)
            elif choice == "2":
                 ratio = (4, 3)
            elif choice == "3":
                 r1 = int(input("Enter width ratio: "))
                 r2 = int(input("Enter height ratio: "))
                 ratio = (r1, r2)
            else:
                ratio= None

            edited = addjust_padding(history[-1], pad_y, pad_x, border_type, ratio)

        elif choice == '5':
            print("Theshold Strategy:")
            print("1. THRESH BINARY:")
            print("2. THRESH BINARY INV:")
            choice = input("> ")
            if choice == "1":
                thresh_strategy = cv2.THRESH_BINARY
            elif choice == "2":
                thresh_strategy = cv2.THRESH_BINARY_INV
            else:
                print("❌ Invalid option.")
                continue

            low_thresh = int(input("Enter low Threshold (0 - 255): "))
            high_thresh = int(input("Enter low Threshold (0 - 255): "))

            if not(low_thresh >= 0 and low_thresh <= 255) or not(high_thresh >= 0 and high_thresh <= 255):
                print("❌ Invalid Input.")
                continue


            edited = apply_threshold(history[-1], low_thresh, high_thresh, thresh_strategy)

        elif choice == '6':
            path = input("relative path to the second image: ").strip()
            img2 = cv2.imread(path)
            if img2 is None:
                print("❌ Invalid pat.")
                continue
            alpha = float(input("weighted factor for first image ( 0 - 1): "))
            edited = blend(history[-1], img2, alpha)
        elif choice == '7':
            if len(history) > 1:
                history.pop()
                print("Undone last operation")
                continue
            else:
                print("Nothing to undo.")
                continue
        elif choice == '8':
            print("\n=== History of Operations ===")
            for i, entry in enumerate(log, 1):
                print(f"{i}. {entry}")
            continue
        elif choice == '9':
            save = input("Save the final image? (y/n): ").lower()
            if save == 'y':
                filename = input("Enter filename (e.g., output.jpg): ")
                cv2.imwrite(filename, history[-1])
                print("✅ Image saved.")
            print("\n=== Final Operation Log ===")
            for action in log:
                print(f"- {action}")
            break
        else:
            print("❌ Invalid option.")
            continue

        display_images(history[-1], edited, "Preview")
        history.append(edited)

main()
