import os
os.environ["IN_STREAMLIT"] = "true"
os.environ["PDFTEXT_CPU_WORKERS"] = "1"
SAVE_DIR = "output/SEC_EDGAR_FILINGS_MD"

import pypdfium2
from typing import Optional
import torch.multiprocessing as mp
from tqdm import tqdm
import math

# ========== 更新的导入部分 ==========
from marker.renderers.markdown import MarkdownRenderer  # 直接引用模块路径
# 修改导入语句
from marker.providers.registry import provider_from_ext
            
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict
# ==================================

from marker.settings import settings
from marker.logger import configure_logging
import traceback
import json

configure_logging()

def worker_init(shared_model):
    global model_refs
    model_refs = shared_model


def worker_exit():
    global model_refs
    del model_refs


def process_single_pdf(args):
    filepath, out_folder, metadata, min_length = args
    fname = os.path.basename(filepath)
    output_path = os.path.join(out_folder, fname.replace('.pdf', '.md'))
    if os.path.exists(output_path):
        return

    try:
        if min_length:
            # 在文件处理逻辑中修改
            # 修改文件类型检测逻辑
            provider = provider_from_ext(file_path)
            file_type = provider.__name__.replace('Provider', '').lower()  # 示例：PdfProvider -> pdf

            # 调整支持类型验证
            supported_types = ['pdf', 'doc', 'xls', 'ppt', 'epub', 'html']
            if file_type not in supported_types:
                #raise ValueError(f"不支持的文件类型: {file_type}")
                print(f"不支持的文件类型: {file_type}")
                return 0

            length = get_length_of_text(filepath)
            if length < min_length:
                return

        # ========== 更新的转换流程 ==========
        config = ConfigParser()
        converter = PdfConverter(config)
        rendered = converter.convert(filepath)
        renderer = MarkdownRenderer(config=config)  # 确保参数传递
        text = renderer.render(rendered)
        # ==================================

        if len(text.strip()) > 0:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        else:
            print(f"Empty file: {filepath})")
    except Exception as e:
        print(f"Error converting {filepath}: {e}")
        print(traceback.format_exc())

def run_marker_mp(
    in_folder,
    out_folder,
    chunk_idx=0,
    num_chunks=1,
    max_files=None,
    workers=5,
    metadata_file=None,
    min_length=None,
    inference_ram: Optional[int] = None,
    vram_per_task: Optional[int] = None,
):
    """
    Convert multiple PDFs to markdown using the provided parameters.

    Parameters:
    - in_folder: str
        Input folder containing PDF files.
    - out_folder: str
        Output folder where markdown files will be saved.
    - chunk_idx: int, optional
        Chunk index to convert. Default is 0.
    - num_chunks: int, optional
        Number of chunks being processed in parallel. Default is 1.
    - max_files: int, optional
        Maximum number of PDFs to convert. Default is None (no limit).
    - workers: int, optional
        Number of worker processes to use. Default is 5.
    - metadata_file: str, optional
        Path to metadata JSON file for filtering. Default is None.
    - min_length: int, optional
        Minimum length of PDF to convert. Default is None.
    """

    in_folder = os.path.abspath(in_folder)
    out_folder = os.path.abspath(out_folder)
    files = [os.path.join(in_folder, f) for f in os.listdir(in_folder)]
    files = [f for f in files if os.path.isfile(f)]
    os.makedirs(out_folder, exist_ok=True)

    # Handle chunks if we're processing in parallel
    # Ensure we get all files into a chunk
    chunk_size = math.ceil(len(files) / num_chunks)
    start_idx = chunk_idx * chunk_size
    end_idx = start_idx + chunk_size
    files_to_convert = files[start_idx:end_idx]

    # Limit files converted if needed
    if max:
        files_to_convert = files_to_convert[:max_files]

    metadata = {}
    if metadata_file:
        metadata_file = os.path.abspath(metadata_file)
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

    total_processes = min(len(files_to_convert), workers)

    # Dynamically set GPU allocation per task based on GPU ram
    if inference_ram is not None:
        settings.INFERENCE_RAM = inference_ram
    if vram_per_task is not None:
        settings.VRAM_PER_TASK = vram_per_task

    if settings.CUDA:
        tasks_per_gpu = (
            settings.INFERENCE_RAM // settings.VRAM_PER_TASK if settings.CUDA else 0
        )
        total_processes = int(min(tasks_per_gpu, total_processes))
    else:
        total_processes = int(total_processes)

    # ========== 更新的模型加载部分 ==========
    config = ConfigParser()
    model_dict = create_model_dict(config)
    
    mp.set_start_method("spawn")
    for model in model_dict.values():
        if model.device.type == "mps":
            raise ValueError("MPS设备不支持多进程")
        model.share_memory()
    # =====================================

    print(
        f"Converting {len(files_to_convert)} pdfs in chunk {chunk_idx + 1}/{num_chunks} with {total_processes} processes, and storing in {out_folder}"
    )
    task_args = [
        (f, out_folder, metadata.get(os.path.basename(f)), min_length)
        for f in files_to_convert
    ]

    # ========== 更新的进程池初始化 ==========
    with mp.Pool(
        processes=total_processes,
        initializer=worker_init,
        initargs=(model_dict,)
    ) as pool:
    # =====================================

        list(
            tqdm(
                pool.imap(process_single_pdf, task_args),
                total=len(task_args),
                desc="Processing PDFs",
                unit="pdf",
            )
        )

        pool._worker_handler.terminate = worker_exit

    # Delete all CUDA tensors
    # 新增资源清理
    for model in model_dict.values():
        if hasattr(model, 'close'):
            model.close()
    torch.cuda.empty_cache()
    del model_lst