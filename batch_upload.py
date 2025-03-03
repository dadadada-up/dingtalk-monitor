import os
import subprocess
from pathlib import Path
import time
import sys

def batch_upload(repo_path, batch_size=50):
    try:
        # 检查目录是否存在
        if not os.path.exists(repo_path):
            raise Exception(f"目录不存在: {repo_path}")
            
        # 切换到仓库目录
        os.chdir(repo_path)
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查是否是git仓库
        if not os.path.exists('.git'):
            raise Exception("当前目录不是git仓库")
        
        # 获取所有未跟踪的文件
        result = subprocess.run(['git', 'status', '-u', '--porcelain'], 
                              capture_output=True, text=True)
        untracked_files = [line[3:] for line in result.stdout.split('\n') 
                          if line.startswith('??')]
        
        if not untracked_files:
            print("没有找到需要上传的文件")
            return
            
        print(f"共发现 {len(untracked_files)} 个文件需要上传")
        
        # 分批处理
        for i in range(0, len(untracked_files), batch_size):
            batch = untracked_files[i:i + batch_size]
            print(f"\n准备上传第 {i//batch_size + 1} 批文件 ({len(batch)} 个文件)")
            
            # 添加文件
            subprocess.run(['git', 'add'] + batch, check=True)
            
            # 提交
            commit_msg = f'Batch upload {i//batch_size + 1}'
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # 推送
            subprocess.run(['git', 'push'], check=True)
            
            print(f'成功上传第 {i//batch_size + 1} 批文件')
            time.sleep(2)
            
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    repo_path = os.getcwd()  # 使用当前目录
    batch_upload(repo_path) 