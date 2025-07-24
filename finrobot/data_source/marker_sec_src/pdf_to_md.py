import os
import torch
import traceback  # 新增：用于捕获完整异常堆栈
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict
from marker.output import text_from_rendered

SAVE_DIR = "output/SEC_EDGAR_FILINGS_MD"

def run_marker(
    input_ticker_year_path: str,
    output_ticker_year_path: str,
    batch_multiplier: int = 2
):
    # 初始化配置（保持默认markdown输出）
    #config = {
    #    "batch_multiplier": batch_multiplier,
    #    "langs": ["English"]
    #}
    #config_parser = ConfigParser(config)
    
    #print(f"[INFO] 正在加载模型... 配置参数: {config_parser}")  
    print(f"[INFO] 正在加载模型... ")
    import psutil
    print(f"当前内存占用: {psutil.virtual_memory().percent}%")
    artifact_dict = create_model_dict()  
    import psutil
    print(f"当前内存占用: {psutil.virtual_memory().percent}%")
    print(f"[INFO] 加载模型完成")  

    converter = PdfConverter(
        artifact_dict,
    )

    print(f"[INFO] PDF转换器初始化完成，处理流程: {converter}")
    #输出
    

    # 保持原有目录创建逻辑（新增目录检查提示）
    os.makedirs(output_ticker_year_path, exist_ok=True)
    print(f"[INFO] 输出目录已准备: {output_ticker_year_path}")

    # 保持原有文件遍历逻辑（新增文件统计提示）
    pdf_files = [f for f in os.listdir(input_ticker_year_path) if f.endswith(".pdf")]
    print(f"[INFO] 发现待处理PDF文件: {len(pdf_files)} 个（路径: {input_ticker_year_path}）")

    for pdf_file in pdf_files:
        # 新增文件处理开始提示
        print(f"\n[PROCESS] 开始处理文件: {pdf_file}")
        
        pdf_path = os.path.join(input_ticker_year_path, pdf_file)
        
        # 新增转换开始提示
        print(f"[CONVERT] 正在转换PDF -> Markdown... 路径: {pdf_path}")
        rendered = converter(pdf_path)
        full_text, _, images = text_from_rendered(rendered)
        # 新增转换结果提示
        print(f"[CONVERT] 转换完成！生成文本长度: {len(full_text)} 字符，检测到图片数量: {len(images)}")

        # 保持原文件保存方式（新增保存路径提示）
        fname = os.path.basename(pdf_path)
        subfolder_path = os.path.join(output_ticker_year_path, fname.replace('.pdf', ''))
        os.makedirs(subfolder_path, exist_ok=True)
        
        file_name, _ = os.path.splitext(fname)
        output_file_path = os.path.join(subfolder_path, f"{file_name}.MD")
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # 新增保存成功提示
        print(f"[SAVE] Markdown已保存至: {os.path.join(subfolder_path, 'output.md')}")

    # 保持显存释放机制（新增资源释放提示）
    del artifact_dict
    print(f"\n[FINISH] 所有文件处理完成！总处理文件数: {len(pdf_files)}")