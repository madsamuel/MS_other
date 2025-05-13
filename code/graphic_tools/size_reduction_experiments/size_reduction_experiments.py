import os
from PIL import Image


def reduce_image_size(input_path, output_path, target_ratio=0.5, tolerance=0.05):
    original_size = os.path.getsize(input_path)
    target_size = original_size * target_ratio

    img = Image.open(input_path)

    quality_min = 10
    quality_max = 95
    quality_mid = quality_max

    while quality_max - quality_min > 1:
        quality_mid = (quality_min + quality_max) // 2

        img.save(output_path, 'JPEG', quality=quality_mid, optimize=True)
        current_size = os.path.getsize(output_path)

        if abs(current_size - target_size) / target_size < tolerance:
            break
        elif current_size > target_size:
            quality_max = quality_mid
        else:
            quality_min = quality_mid

    print(f"Final quality used: {quality_mid}, size reduction achieved: {100 - (current_size / original_size * 100):.2f}%")


# Example Usage
if __name__ == "__main__":
    input_image = 'input.jpg'   # Replace with your input image path
    output_image = 'output.jpg'  # Replace with your desired output path
    reduce_image_size(input_image, output_image, target_ratio=0.5)
