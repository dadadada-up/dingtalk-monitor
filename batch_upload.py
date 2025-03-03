import os
import subprocess
from pathlib import Path
import time
import sys

def run_with_retry(cmd, max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            if attempt == max_retries - 1:
                raise
            print(f"命令执行失败，{retry_delay}秒后重试... ({attempt + 1}/{max_retries})")
            print(f"错误信息: {e.stderr}")
            time.sleep(retry_delay)

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
        
        # 获取所有变更的文件
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        files = []
        for line in result.stdout.split('\n'):
            if line.strip():
                # 跳过前两个字符（状态码）和空格
                files.append(line[3:])
        
        if not files:
            print("没有找到需要上传的文件")
            return
            
        print(f"共发现 {len(files)} 个文件需要上传")
        print("文件列表:")
        for f in files:
            print(f"  - {f}")
        
        # 分批处理
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            print(f"\n准备上传第 {i//batch_size + 1} 批文件 ({len(batch)} 个文件)")
            
            # 添加文件
            run_with_retry(['git', 'add'] + batch)
            
            # 提交
            commit_msg = f'Batch upload {i//batch_size + 1}'
            run_with_retry(['git', 'commit', '-m', commit_msg])
            
            # 推送（增加重试）
            print("正在推送到远程仓库...")
            run_with_retry(['git', 'push'])
            
            print(f'成功上传第 {i//batch_size + 1} 批文件')
            time.sleep(2)
            
    except Exception as e:
        print(f"错误: {str(e)}")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 运行 'git remote -v' 检查远程仓库配置")
        print("3. 如果使用代理，配置 git 代理设置:")
        print("   git config --global http.proxy http://127.0.0.1:端口号")
        print("   git config --global https.proxy https://127.0.0.1:端口号")
        sys.exit(1)

if __name__ == '__main__':
    repo_path = os.getcwd()
    batch_upload(repo_path) 