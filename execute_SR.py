# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 14:33:09 2023

@author: Kunru Song
"""

import subprocess

def run_realesrgan_command():
    cmd = [
        'D:\\realesrgan-ncnn-vulkan-20220424-windows\\realesrgan-ncnn-vulkan.exe',
        '-i', 'D:\\selected_images_v2\\',
        '-o', 'D:\\selected_images_v2_enhanced\\',
        '-n', 'realesrgan-x4plus',
        '-s', '2',
        '-f', 'jpg',
        '-t', '32',
        '-x'
    ]
    
    # 使用subprocess运行命令
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    run_realesrgan_command()
