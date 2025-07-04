import os
import shutil
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def process_ab_file(src_path, dst_dir):
    try:
        result = subprocess.run(
            ['arkabconverter', '--input-files', src_path, '--output-dir', dst_dir],
            capture_output=True,
            text=True,
            check=True
        )
        return True, src_path
    except subprocess.CalledProcessError as e:
        print(f"转换失败：{src_path}\n错误信息：{e.stderr}")
        return False, src_path
    except Exception as e:
        print(f"未知错误：{src_path} - {str(e)}")
        return False, src_path

def copy_file(src_path, dst_path):
    try:
        shutil.copy2(src_path, dst_path)
        return True, src_path
    except Exception as e:
        print(f"复制失败：{src_path} -> {dst_path}\n错误：{str(e)}")
        return False, src_path

def process_file_entry(args):
    src_path, input_dir, output_dir = args
    rel_path = os.path.relpath(src_path, input_dir)
    dst_path = os.path.join(output_dir, rel_path)
    dst_dir = os.path.dirname(dst_path)
    
    os.makedirs(dst_dir, exist_ok=True)
    
    if src_path.endswith('.ab') or src_path.endswith('.bin'):
        return process_ab_file(src_path, dst_dir)
    else:
        return copy_file(src_path, dst_path)

def rename_uncompressed_file(file_tuple):
    root, filename = file_tuple
    src = os.path.join(root, filename)
    new_name = filename.replace(".uncompressed", "")
    dst = os.path.join(root, new_name)
    
    try:
        os.rename(src, dst)
        return True, src
    except Exception as e:
        print(f"重命名失败: {src} | 错误: {str(e)}")
        return False, src

def convert_ab_files(input_dir, output_dir, max_workers=8):
    start_time = time.time()
    file_count = 0
    
    file_entries = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            src_path = os.path.join(root, file)
            file_entries.append((src_path, input_dir, output_dir))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        total_files = len(file_entries)
        
        for entry in file_entries:
            future = executor.submit(process_file_entry, entry)
            futures[future] = entry[0]
        
        for i, future in enumerate(as_completed(futures), 1):
            success, path = future.result()
            file_count += 1
            if i % 10 == 0 or i == total_files:
                print(f"\r处理进度: {i}/{total_files} | 耗时: {time.time()-start_time:.2f}s", end='')
    
    print(f"\n转换完成，共处理 {file_count} 个文件")
    return file_count

def remove_uncompressed_suffix(output_dir, max_workers=8):
    start_time = time.time()
    rename_list = []
    
    for root, _, files in os.walk(output_dir):
        for filename in files:
            if ".uncompressed" in filename:
                rename_list.append((root, filename))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        total_files = len(rename_list)
        futures = executor.map(rename_uncompressed_file, rename_list)
        
        success_count = 0
        for i, (success, path) in enumerate(futures, 1):
            success_count += success
            if i % 10 == 0 or i == total_files:
                print(f"\r重命名进度: {i}/{total_files} | 耗时: {time.time()-start_time:.2f}s", end='')
    
    print(f"\n重命名完成，成功处理 {success_count}/{total_files} 个文件")
    return success_count

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_dir', help='输入目录路径')
    parser.add_argument('output_dir', help='输出目录路径')
    parser.add_argument('--threads', type=int, default=8, 
                      help='线程并发数 (默认: 8)')
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    convert_ab_files(args.input_dir, args.output_dir, args.threads)
    remove_uncompressed_suffix(args.output_dir, args.threads)
    
    print("全部处理完成！")