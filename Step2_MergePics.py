import os
import shutil
from PIL import Image
import imagehash


def move_and_rename_images():
    # 设置工作目录为脚本所在路径
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

    # 初始化图片编号
    img_count = 1

    # 存储图片哈希值的集合
    hash_set = set()

    # 遍历当前目录下的所有文件和文件夹
    for item in os.listdir(script_directory):
        item_path = os.path.join(script_directory, item)

        # 检查是否是文件夹
        if os.path.isdir(item_path):
            # 遍历文件夹中的所有文件
            for file in os.listdir(item_path):
                # 检查是否是JPG图片
                if file.lower().endswith('.jpg'):
                    file_path = os.path.join(item_path, file)

                    with Image.open(file_path) as img:
                        # 将图片缩放到256x256
                        img_resized = img.resize((256, 256))
                        h = imagehash.average_hash(img_resized)
            
                        # 检查哈希值是否已经存在
                        if h in hash_set:
                            # 如果图片是重复的，删除并继续下一个
                            os.remove(file_path)
                            continue
                        hash_set.add(h)

                    # 创建一个新的文件夹用于存储所有图片
                    merged_dir = os.path.join(script_directory, 'merged_images')
                    if not os.path.exists(merged_dir):
                        os.makedirs(merged_dir)

                    # 为图片生成新的路径和名称
                    new_file_name = f"{img_count}.jpg"
                    new_file_path = os.path.join(merged_dir, new_file_name)

                    # 移动图片
                    shutil.move(file_path, new_file_path)

                    # 调整图片分辨率
                    with Image.open(new_file_path) as img:
                        img = img.resize((320, 180))
                        img.save(new_file_path)

                    img_count += 1

            # 删除原有文件夹
            shutil.rmtree(item_path)


# 执行函数
move_and_rename_images()
