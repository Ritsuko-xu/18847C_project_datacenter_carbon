import os
from PIL import Image

def stitch_images(image_files, rows, cols, save_path='stitched_image.png'):
    images = [Image.open(file) for file in image_files]

    # 如果图像数量不满足完整的网格，剩余位置添加空白图像
    num_missing = rows * cols - len(images)
    if num_missing > 0:
        empty_img = Image.new('RGB', images[0].size, (255, 255, 255))  # 创建一个白色的空白图像
        images += [empty_img] * num_missing
    
    # 确定每张图像的尺寸
    widths, heights = zip(*(i.size for i in images))

    # 确定总图像的最大宽度和总高度
    max_width = max(widths) * cols
    total_height = max(heights) * rows

    # 创建一个新的图像，用于拼接
    stitched_image = Image.new('RGB', (max_width, total_height))

    x_offset = 0
    y_offset = 0
    counter = 0

    # 按照行和列拼接图像
    for img in images:
        stitched_image.paste(img, (x_offset, y_offset))
        x_offset += img.width
        counter += 1
        
        # 如果达到列的末端，则移动到下一行
        if counter % cols == 0:
            x_offset = 0
            y_offset += img.height

    # 保存拼接后的图像
    stitched_image.save(save_path)
    print(f"Image saved as {save_path}")

def find_png_images(directory):
    # 获取目录下所有 PNG 图像
    return [file for file in os.listdir(directory) if file.endswith('.png')]

def main():
    current_directory = os.getcwd()  # 获取当前目录
    png_files = find_png_images(current_directory)
    
    if len(png_files) != 5:
        print("Error: Expected exactly 5 PNG files in the directory.")
        return

    # 按照 2 行 3 列的布局拼接图像
    stitch_images(png_files, rows=3, cols=2)

if __name__ == "__main__":
    main()
