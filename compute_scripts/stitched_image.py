import os
from PIL import Image

def stitch_images(image_files, rows, cols, save_path='stitched_image.png'):
    images = [Image.open(file) for file in image_files]
    
    widths, heights = zip(*(i.size for i in images))

    max_width = max(widths) * cols
    total_height = max(heights) * rows

    stitched_image = Image.new('RGB', (max_width, total_height))

    x_offset = 0
    y_offset = 0
    counter = 0

    for img in images:
        stitched_image.paste(img, (x_offset, y_offset))
        x_offset += img.width
        counter += 1
        
        if counter % cols == 0:
            x_offset = 0
            y_offset += img.height

    stitched_image.save(save_path)
    print(f"Image saved as {save_path}")

def find_png_images(directory):
    return [file for file in os.listdir(directory) if file.endswith('.png')]

def main():
    current_directory = os.getcwd()  
    png_files = find_png_images(current_directory)
    
    if len(png_files) != 12:
        print("Error: Expected exactly 12 PNG files in the directory.")
        return

    stitch_images(png_files, rows=4, cols=3)

if __name__ == "__main__":
    main()
