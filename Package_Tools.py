#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理工具打包器 - PyInstaller独立可执行文件版本
使用方法: python3 package_tools.py
"""

import os
import sys
import subprocess
import shutil
import time

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("           🖼️  图像处理工具打包器 🖼️")
    print("=" * 60)
    print()

def print_menu():
    """打印菜单"""
    print("PyInstaller独立可执行文件打包方案")
    print()
    print("1. 🚀 构建所有工具为独立可执行文件")
    print("   - 优点：完全独立，无需Python环境")
    print("   - 缺点：文件较大，首次启动较慢")
    print()
    print("2. 🔧 安装/更新PyInstaller依赖")
    print()
    print("3. 📁 查看输出目录")
    print()
    print("0. ❌ 退出")
    print()

def setup_virtual_environment():
    """设置虚拟环境"""
    venv_dir = "venv_package"
    
    if not os.path.exists(venv_dir):
        print("创建虚拟环境...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print("✓ 虚拟环境创建成功")
        except subprocess.CalledProcessError as e:
            print(f"✗ 虚拟环境创建失败: {e}")
            return None
    
    # 获取虚拟环境中的Python路径
    if sys.platform == "win32":
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_path = os.path.join(venv_dir, "bin", "python")
    
    if not os.path.exists(python_path):
        print(f"✗ 虚拟环境Python路径不存在: {python_path}")
        return None
    
    return python_path

def install_dependencies():
    """安装依赖"""
    print("正在安装PyInstaller...")
    
    # 设置虚拟环境
    venv_python = setup_virtual_environment()
    if not venv_python:
        return False
    
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pyinstaller"])
        print("✓ PyInstaller安装/更新成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller安装失败: {e}")
        return False

def build_executable(venv_python, script_path, output_name, index, total):
    """构建单个可执行文件"""
    print(f"[{index}/{total}] 正在构建: {script_path}")
    
    # PyInstaller命令
    cmd = [
        venv_python, "-m", "PyInstaller",
        "--onefile",  # 单文件
        "--console",  # 有控制台窗口（macOS兼容）
        "--name", output_name,
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", "build",
        "--clean",  # 清理临时文件
        script_path
    ]
    
    start_time = time.time()
    
    try:
        # 显示详细输出以诊断问题
        result = subprocess.run(cmd, capture_output=True, text=True)
        build_time = time.time() - start_time
        
        if result.returncode == 0:
            # 检查输出文件
            output_file = os.path.join("dist", output_name)
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"✓ {output_name} 构建成功 ({size_mb:.1f} MB, {build_time:.1f}s)")
                return True
            else:
                print(f"✗ {output_name} 构建失败: 输出文件不存在")
                return False
        else:
            print(f"✗ {output_name} 构建失败:")
            print(f"  错误信息: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ {output_name} 构建失败: {e}")
        return False

def run_pyinstaller_build():
    """运行PyInstaller构建"""
    print("启动PyInstaller构建...")
    
    # 设置虚拟环境
    venv_python = setup_virtual_environment()
    if not venv_python:
        print("❌ 无法设置虚拟环境")
        return
    
    # 检查PyInstaller是否安装
    try:
        subprocess.check_call([venv_python, "-c", "import PyInstaller"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ PyInstaller已安装")
    except subprocess.CalledProcessError:
        print("PyInstaller未安装，正在安装...")
        if not install_dependencies():
            return
    
    # 创建输出目录
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # 需要打包的Python脚本列表
    scripts_to_build = [
        ("1_Facility_resize_rename_images/Facility_resize_rename_images.py", "Facility_Resizer"),
        ("2_ServiceResource_resize_rename_images/ServiceResource_resize_rename_images.py", "ServiceResource_Resizer"),
        ("3_FloorMap_resize_rename_images/FloorMap_resize_rename_images.py", "FloorMap_Resizer"),
        ("4_Layout_resize_rename_images/Layout_resize_rename_images.py", "Layout_Resizer"),
        ("5_Access_resize_rename_images/Access_resize_rename_images.py", "Access_Resizer"),
        ("6_Product_resize_rename_images/Product_singlefood_resize_rename_images.py", "Product_SingleFood_Resizer"),
        ("6_Product_resize_rename_images/Product_banner_resize_rename_images.py", "Product_Banner_Resizer"),
        ("7_Route_resize_rename_images/Route_resize_rename_images.py", "Route_Resizer"),
        ("9_900x600(3:2)_resize/3:2_resize_images.py", "3_2_Resizer"),
        ("10_960x540(16:9)_resize/16:9_resize_images.py", "16_9_Resizer"),
        ("11_960x720(4:3)_resize/4:3_resize_images.py", "4_3_Resizer"),
        ("12_(1:1)_resize/1:1_resize_images.py", "1_1_Resizer"),
    ]
    
    # 过滤存在的脚本
    existing_scripts = [(path, name) for path, name in scripts_to_build if os.path.exists(path)]
    
    if not existing_scripts:
        print("❌ 未找到任何Python脚本文件")
        return
    
    print(f"找到 {len(existing_scripts)} 个脚本文件，开始构建...")
    print()
    
    # 构建所有脚本
    success_count = 0
    total_scripts = len(existing_scripts)
    
    for i, (script_path, output_name) in enumerate(existing_scripts, 1):
        if build_executable(venv_python, script_path, output_name, i, total_scripts):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"构建完成！成功: {success_count}/{total_scripts}")
    print("=" * 60)
    
    if success_count > 0:
        print(f"输出目录: dist/")
        
        # 创建部署包
        create_deployment_package()
        
        print("\n🎉 构建成功！现在可以：")
        print("1. 将 dist/ 目录中的可执行文件复制到其他环境使用")
        print("2. 或者使用 Image_Resize_Tools_Standalone/ 部署包")
    else:
        print("❌ 所有构建都失败了，请检查错误信息")

def create_deployment_package():
    """创建部署包"""
    print("\n正在创建部署包...")
    
    # 创建部署目录
    deploy_dir = "Image_Resize_Tools_Standalone"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # 复制可执行文件
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            file_path = os.path.join("dist", file)
            
            # 处理不同类型的可执行文件
            if file.endswith(".exe"):  # Windows
                shutil.copy2(file_path, deploy_dir)
            elif file.endswith(".app"):  # macOS应用包
                # 复制整个.app文件夹
                shutil.copytree(file_path, os.path.join(deploy_dir, file))
            elif not file.endswith(".") and os.path.isfile(file_path):  # Unix可执行文件
                shutil.copy2(file_path, deploy_dir)
    
    # 复制启动脚本
    copy_starter_scripts(deploy_dir)
    
    # 复制用户手册
    if os.path.exists("★User_manual.xlsx"):
        shutil.copy2("★User_manual.xlsx", deploy_dir)
    
    # 创建README
    create_readme(deploy_dir)
    
    # 创建使用说明
    create_usage_guide(deploy_dir)
    
    print(f"✓ 部署包已创建: {deploy_dir}/")

def copy_starter_scripts(deploy_dir):
    """复制启动脚本"""
    scripts_dir = os.path.join(deploy_dir, "启动脚本")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # 复制所有.sh文件
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".sh"):
                # 创建相对路径
                rel_path = os.path.relpath(root, ".")
                target_dir = os.path.join(scripts_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(os.path.join(root, file), target_dir)

def create_readme(deploy_dir):
    """创建README文件"""
    readme_content = """# 图像处理工具 - 独立版本

## 说明
这是图像处理工具的独立版本，无需安装Python环境即可使用。

## 使用方法
1. 将整个文件夹复制到目标环境
2. 双击对应的可执行文件即可运行
3. 或者使用启动脚本（.sh文件）

## 工具列表
- Facility_Resizer: 设施图像处理
- ServiceResource_Resizer: 服务资源图像处理
- FloorMap_Resizer: 楼层地图图像处理
- Layout_Resizer: 布局图像处理
- Access_Resizer: 访问图像处理
- Product_SingleFood_Resizer: 产品单食品图像处理
- Product_Banner_Resizer: 产品横幅图像处理
- Route_Resizer: 路线图像处理
- 3_2_Resizer: 3:2比例图像处理
- 16_9_Resizer: 16:9比例图像处理
- 4_3_Resizer: 4:3比例图像处理
- 1_1_Resizer: 1:1比例图像处理

## 注意事项
- 首次运行可能需要几秒钟启动时间
- 确保有足够的磁盘空间
- 支持Windows、macOS和Linux系统

## 技术支持
如有问题，请查看原始项目文档。
"""
    
    with open(os.path.join(deploy_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

def create_usage_guide(deploy_dir):
    """创建使用说明"""
    usage_content = """# 使用说明

## 快速开始

### Windows用户
1. 双击可执行文件（.exe）直接运行
2. 按照提示输入参数

### macOS/Linux用户
1. 在终端中运行可执行文件
2. 或者使用启动脚本

## 详细使用步骤

### 1. 设施图像处理
- 运行: Facility_Resizer
- 输入: 设施ID和图像编号
- 输出: Facility_XXX_image_N.webp

### 2. 服务资源图像处理
- 运行: ServiceResource_Resizer
- 输入: 服务资源ID
- 输出: ServiceResource_XXXX_N.webp

### 3. 楼层地图图像处理
- 运行: FloorMap_Resizer
- 输入: 楼层ID和区域编号
- 输出: FloorMap_XX_XX_N.webp

### 4. 路线图像处理
- 运行: Route_Resizer
- 输入: 设施ID和路线编号
- 输出: Route_XXX_X_XXX_NN.webp

### 5. 比例调整工具
- 3:2比例: 3_2_Resizer
- 16:9比例: 16_9_Resizer
- 4:3比例: 4_3_Resizer
- 1:1比例: 1_1_Resizer

## 输入输出目录
- 输入图像: 0_input_images/
- 临时文件: 1_temp_images/
- 输出图像: 2_output_images/

## 故障排除
1. 确保输入目录有图像文件
2. 检查输出目录权限
3. 首次运行可能需要等待
"""
    
    with open(os.path.join(deploy_dir, "使用说明.md"), "w", encoding="utf-8") as f:
        f.write(usage_content)

def show_output_directories():
    """显示输出目录"""
    print("输出目录信息：")
    print()
    
    if os.path.exists("dist"):
        print("📁 dist/ 目录 (可执行文件):")
        files = os.listdir("dist")
        if files:
            for file in files:
                size = os.path.getsize(os.path.join("dist", file))
                size_mb = size / (1024 * 1024)
                print(f"   - {file} ({size_mb:.1f} MB)")
        else:
            print("   (空)")
    else:
        print("📁 dist/ 目录不存在")
    
    print()
    
    if os.path.exists("Image_Resize_Tools_Standalone"):
        print("📁 Image_Resize_Tools_Standalone/ 目录 (部署包):")
        files = os.listdir("Image_Resize_Tools_Standalone")
        if files:
            for file in files:
                print(f"   - {file}")
        else:
            print("   (空)")
    else:
        print("📁 Image_Resize_Tools_Standalone/ 目录不存在")
    
    print()
    print("💡 提示：构建完成后，可以将 Image_Resize_Tools_Standalone/ 目录")
    print("   复制到其他环境使用，无需安装Python")

def main():
    """主函数"""
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("请输入选择 (0-3): ").strip()
            
            if choice == "0":
                print("\n👋 再见！")
                break
            elif choice == "1":
                print("\n🚀 开始构建独立可执行文件...")
                run_pyinstaller_build()
            elif choice == "2":
                print("\n🔧 安装/更新依赖...")
                install_dependencies()
            elif choice == "3":
                print("\n📁 查看输出目录...")
                show_output_directories()
            else:
                print("\n❌ 无效选择，请输入0-3")
            
            if choice in ["1", "2", "3"]:
                input("\n按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()
