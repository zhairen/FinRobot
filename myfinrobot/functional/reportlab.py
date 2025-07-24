from datetime import datetime
import os
import traceback
import pandas as pd
import pandas as pd
from reportlab.lib import colors
from reportlab.lib import pagesizes
from reportlab.platypus import (
    SimpleDocTemplate,
    Frame,
    Paragraph,
    Image,
    PageTemplate,
    FrameBreak,
    Spacer,
    Table,
    TableStyle,
    NextPageTemplate,
    PageBreak,
)
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

from myfinrobot.data_source.fmp_utils import FMPUtils
from myfinrobot.data_source.yfinance_utils import YFinanceUtils
from myfinrobot.functional.json_parse import parse_relaxed_json
from .analyzer import ReportAnalysisUtils
from typing import Annotated

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfdoc

class ReportLabUtils:
    """ Utility class for generating equity research reports in PDF format using ReportLab."""
    def build_annual_report(
        ticker_symbol: Annotated[str, "ticker symbol"],
        save_path: Annotated[str, "path to save the annual report pdf"],
        operating_results: Annotated[
            str,
            "a paragraph of text: the company's income summarization from its financial report",
        ],
        market_position: Annotated[
            str,
            "a paragraph of text: the company's current situation and end market (geography), major customers (blue chip or not), market share from its financial report, avoid similar sentences also generated in the business overview section, classify it into either of the two",
        ],
        business_overview: Annotated[
            str,
            "a paragraph of text: the company's description and business highlights from its financial report",
        ],
        risk_assessment: Annotated[
            str,
            "a paragraph of text: the company's risk assessment from its financial report",
        ],
        competitors_analysis: Annotated[
            str,
            "a paragraph of text: the company's competitors analysis from its financial report and competitors' financial report",
        ],
        share_performance_image_path: Annotated[
            str, "path to the share performance image"
        ],
        pe_eps_performance_image_path: Annotated[
            str, "path to the PE and EPS performance image"
        ],
        filing_date: Annotated[str, "filing date of the analyzed financial report"],
    ) -> str:
        """
        Aggregate a company's business_overview, market_position, operating_results,
        risk assessment, competitors analysis and share performance, PE & EPS performance charts all into a PDF report.
        """

        try:
            # 2. 创建PDF并插入图像
            # 页面设置
            page_width, page_height = pagesizes.A4
            left_column_width = page_width * 2 / 3
            right_column_width = page_width - left_column_width
            margin = 4

            # 创建PDF文档路径
            pdf_path = (
                os.path.join(save_path, f"{ticker_symbol}_Equity_Research_report.pdf")
                if os.path.isdir(save_path)
                else save_path
            )
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            doc = SimpleDocTemplate(pdf_path, pagesize=pagesizes.A4)
        
            # 定义两个栏位的Frame
            frame_left = Frame(
                margin,
                margin,
                left_column_width - margin * 2,
                page_height - margin * 2,
                id="left",
            )
            frame_right = Frame(
                left_column_width,
                margin,
                right_column_width - margin * 2,
                page_height - margin * 2,
                id="right",
            )

            single_frame = Frame(margin, margin, page_width-margin*2, page_height-margin*2, id='single')
            single_column_layout = PageTemplate(id='OneCol', frames=[single_frame])

            left_column_width_p2 = (page_width - margin * 3) // 2
            right_column_width_p2 = left_column_width_p2
            frame_left_p2 = Frame(
                margin,
                margin,
                left_column_width_p2 - margin * 2,
                page_height - margin * 2,
                id="left",
            )
            frame_right_p2 = Frame(
                left_column_width_p2,
                margin,
                right_column_width_p2 - margin * 2,
                page_height - margin * 2,
                id="right",
            )

            #创建PageTemplate，并添加到文档
            page_template = PageTemplate(
                id="TwoColumns", frames=[frame_left, frame_right]
            )
            page_template_p2 = PageTemplate(
                id="TwoColumns_p2", frames=[frame_left_p2, frame_right_p2]
            )

             #Define single column Frame
            single_frame = Frame(
                margin,
                margin,
                page_width - 2 * margin,
                page_height - 2 * margin,
                id="single",
            )

            # Create a PageTemplate with a single column
            single_column_layout = PageTemplate(id="OneCol", frames=[single_frame])

            doc.addPageTemplates([page_template, single_column_layout, page_template_p2])

            styles = getSampleStyleSheet()

            # 自定义样式
            custom_style = ParagraphStyle(
                name="Custom",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                # leading=15,
                alignment=TA_JUSTIFY,
            )

            title_style = ParagraphStyle(
                name="TitleCustom",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=16,
                leading=20,
                alignment=TA_LEFT,
                spaceAfter=10,
            )

            subtitle_style = ParagraphStyle(
                name="Subtitle",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=12,
                alignment=TA_LEFT,
                spaceAfter=6,
            )

            table_style2 = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 14),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # 所有单元格左对齐
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    # 标题栏下方添加横线
                    ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
                    # 表格最下方添加横线
                    ("LINEBELOW", (0, -1), (-1, -1), 2, colors.black),
                ]
            )

            name = YFinanceUtils.get_stock_info(ticker_symbol)["shortName"]

            # 准备左栏和右栏内容
            content = []
            # 标题
            content.append(
                Paragraph(
                    f"Equity Research Report: {name}",
                    title_style,
                )
            )

            # 子标题
            content.append(Paragraph("Business Overview", subtitle_style))
            content.append(Paragraph(business_overview, custom_style))

            content.append(Paragraph("Market Position", subtitle_style))
            content.append(Paragraph(market_position, custom_style))
            
            content.append(Paragraph("Operating Results", subtitle_style))
            content.append(Paragraph(operating_results, custom_style))

            # content.append(Paragraph("Summarization", subtitle_style))
            df = FMPUtils.get_financial_metrics(ticker_symbol, years=5)
            df.reset_index(inplace=True)
            currency = YFinanceUtils.get_stock_info(ticker_symbol)["currency"]
            df.rename(columns={"index": f"FY ({currency} mn)"}, inplace=True)
            table_data = [["Financial Metrics"]]
            table_data += [df.columns.to_list()] + df.values.tolist()

            col_widths = [(left_column_width - margin * 4) / df.shape[1]] * df.shape[1]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(table_style2)
            content.append(table)

            content.append(FrameBreak())  # 用于从左栏跳到右栏

            table_style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 12),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # 第一列左对齐
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                    # 第二列右对齐
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    # 标题栏下方添加横线
                    ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
                ]
            )
            full_length = right_column_width - 2 * margin

            data = [
                ["FinRobot"],
                ["https://robotmusk.com/"],
                ["https://github.com/zhairen"],
                [f"Report date: {filing_date}"],
            ]
            col_widths = [full_length]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            # content.append(Paragraph("", custom_style))
            content.append(Spacer(1, 0.15 * inch))
            key_data = ReportAnalysisUtils.get_key_data(ticker_symbol, filing_date)
            # 表格数据
            data = [["Key data", ""]]
            data += [[k, v] for k, v in key_data.items()]
            col_widths = [full_length // 3 * 2, full_length // 3]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            # 将Matplotlib图像添加到右栏

            # 历史股价
            data = [["Share Performance"]]
            col_widths = [full_length]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            plot_path = share_performance_image_path
            width = right_column_width
            height = width // 2
            content.append(Image(plot_path, width=width, height=height))

            # 历史PE和EPS
            data = [["PE & EPS"]]
            col_widths = [full_length]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            plot_path = pe_eps_performance_image_path
            width = right_column_width
            height = width // 2
            content.append(Image(plot_path, width=width, height=height))

            # # 开始新的一页
            content.append(NextPageTemplate("OneCol"))
            content.append(PageBreak())
            
            content.append(Paragraph("Risk Assessment", subtitle_style))
            #content.append(Paragraph(risk_assessment, custom_style))
            content.append(Paragraph(parse_relaxed_json(risk_assessment), custom_style))

            content.append(Paragraph("Competitors Analysis", subtitle_style))
            #content.append(Paragraph(competitors_analysis, custom_style))
            content.append(Paragraph(parse_relaxed_json(competitors_analysis), custom_style))
            
            # def add_table(df, title):
            #     df = df.applymap(lambda x: "{:.2f}".format(x) if isinstance(x, float) else x)
            #     # df.columns = [col.strftime('%Y') for col in df.columns]
            #     # df.reset_index(inplace=True)
            #     # currency = ra.info['currency']
            #     df.rename(columns={"index": "segment"}, inplace=True)
            #     table_data = [[title]]
            #     table_data += [df.columns.to_list()] + df.values.tolist()

            #     table = Table(table_data)
            #     table.setStyle(table_style2)
            #     num_columns = len(df.columns)

            #     column_width = (page_width - 4 * margin) / (num_columns + 1)
            #     first_column_witdh = column_width * 2
            #     table._argW = [first_column_witdh] + [column_width] * (num_columns - 1)

            #     content.append(table)
            #     content.append(Spacer(1, 0.15 * inch))

            # if os.path.exists(f"{ra.project_dir}/outer_resource/"):
            #     Revenue10Q = pd.read_csv(
            #         f"{ra.project_dir}/outer_resource/Revenue10Q.csv",
            #     )
            #     # del Revenue10K['FY2018']
            #     # del Revenue10K['FY2019']
            #     add_table(Revenue10Q, "Revenue")

            #     Ratio10Q = pd.read_csv(
            #         f"{ra.project_dir}/outer_resource/Ratio10Q.csv",
            #     )
            #     # del Ratio10K['FY2018']
            #     # del Ratio10K['FY2019']
            #     add_table(Ratio10Q, "Ratio")

            #     Yoy10Q = pd.read_csv(
            #         f"{ra.project_dir}/outer_resource/Yoy10Q.csv",
            #     )
            #     # del Yoy10K['FY2018']
            #     # del Yoy10K['FY2019']
            #     add_table(Yoy10Q, "Yoy")

            #     plot_path = os.path.join(f"{ra.project_dir}/outer_resource/", "segment.png")
            #     width = page_width - 2 * margin
            #     height = width * 3 // 5
            #     content.append(Image(plot_path, width=width, height=height))

            # # 第二页及之后内容，使用单栏布局
            # df = ra.get_income_stmt()
            # df = df[df.columns[:3]]
            # def convert_if_money(value):
            #     if np.abs(value) >= 1000000:
            #         return value / 1000000
            #     else:
            #         return value

            # # 应用转换函数到DataFrame的每列
            # df = df.applymap(convert_if_money)

            # df.columns = [col.strftime('%Y') for col in df.columns]
            # df.reset_index(inplace=True)
            # currency = ra.info['currency']
            # df.rename(columns={'index': f'FY ({currency} mn)'}, inplace=True)  # 可选：重命名索引列为“序号”
            # table_data = [["Income Statement"]]
            # table_data += [df.columns.to_list()] + df.values.tolist()

            # table = Table(table_data)
            # table.setStyle(table_style2)
            # content.append(table)

            # content.append(FrameBreak())  # 用于从左栏跳到右栏

            # df = ra.get_cash_flow()
            # df = df[df.columns[:3]]

            # df = df.applymap(convert_if_money)

            # df.columns = [col.strftime('%Y') for col in df.columns]
            # df.reset_index(inplace=True)
            # currency = ra.info['currency']
            # df.rename(columns={'index': f'FY ({currency} mn)'}, inplace=True)  # 可选：重命名索引列为“序号”
            # table_data = [["Cash Flow Sheet"]]
            # table_data += [df.columns.to_list()] + df.values.tolist()

            # table = Table(table_data)
            # table.setStyle(table_style2)
            # content.append(table)
            # # content.append(Paragraph('This is a single column on the second page', custom_style))
            # # content.append(Spacer(1, 0.2*inch))
            # # content.append(Paragraph('More content in the single column.', custom_style))

            # 构建PDF文档
            doc.build(content)

            return "Annual report generated successfully."

        except Exception:
            return traceback.format_exc()

    def build_annual_report_cn(
        ticker_symbol: Annotated[str, "ticker symbol"],
        save_path: Annotated[str, "path to save the annual report pdf"],
        operating_results: Annotated[
            str,
            "a paragraph of text: the company's income summarization from its financial report",
        ],
        market_position: Annotated[
            str,
            "a paragraph of text: the company's current situation and end market (geography), major customers (blue chip or not), market share from its financial report, avoid similar sentences also generated in the business overview section, classify it into either of the two",
        ],
        business_overview: Annotated[
            str,
            "a paragraph of text: the company's description and business highlights from its financial report",
        ],
        risk_assessment: Annotated[
            str,
            "a paragraph of text: the company's risk assessment from its financial report",
        ],
        competitors_analysis: Annotated[
            str,
            "a paragraph of text: the company's competitors analysis from its financial report and competitors' financial report",
        ],
        share_performance_image_path: Annotated[
            str, "path to the share performance image"
        ],
        pe_eps_performance_image_path: Annotated[
            str, "path to the PE and EPS performance image"
        ],
        filing_date: Annotated[str, "filing date of the analyzed financial report"],
    ) -> str:
        """
        生成中文股票研究报告PDF Aggregate a company's business_overview, market_position, operating_results,
        risk assessment, competitors analysis and share performance, PE & EPS performance charts all into a PDF report.
        """
        # 注册中文字体 - 修改后的方案
        try:
            # 尝试使用Noto Sans SC字体（简体中文）
            font_path_regular = "/usr/share/fonts/truetype/noto-sc/notosanscjksc-regular.ttf"
            font_path_bold = "/usr/share/fonts/truetype/noto-sc/notosansmonocjksc-bold.ttf"
            
            pdfmetrics.registerFont(TTFont("NotoSansSC", font_path_regular, _fonttype="CID"))  # 关键参数‌:ml-citation{ref="8,17" data="citationList"}
            #font.addSubset(0, 0xffff)
            pdfmetrics.registerFont(TTFont("NotoSansSC-Bold", font_path_bold, _fonttype="CID"))
                        
            pdfdoc.PDFDocumentDictionary.EmbeddedFiles = True 
            # 添加字体映射
            from reportlab.lib import fonts
            fonts.addMapping("NotoSansSC", 0, 0, "NotoSansSC")       # 常规
            fonts.addMapping("NotoSansSC", 0, 1, "NotoSansSC-Bold")  # 粗体
            
            # 设置全局中文字体
            main_cn_font = "NotoSansSC"
            main_cn_bold_font = "NotoSansSC-Bold"
            print("使用 Noto Sans SC 字体生成中文报告")
            
        except Exception as e:
            print(f"Noto Sans SC 字体注册失败: {e}")
            print("尝试使用 ReportLab 内置 CID 字体")
            
            try:
                # 尝试使用 ReportLab 内置的 CID 中文字体
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
                
                main_cn_font = "STSong-Light"
                main_cn_bold_font = "STSong-Light"  # CID 字体通常没有单独的粗体
                print("使用内置 STSong-Light CID 字体")
            except Exception as cid_error:
                print(f"CID 字体注册失败: {cid_error}")
                print("回退到 Helvetica 字体 (可能无法正确显示中文)")
                
                # 使用 Helvetica 作为最后回退
                main_cn_font = "Helvetica"
                main_cn_bold_font = "Helvetica-Bold"

        try:
            # 2. 创建PDF并插入图像
            # 页面设置
            page_width, page_height = pagesizes.A4
            left_column_width = page_width * 2 / 3
            right_column_width = page_width - left_column_width
            margin = 4

            # 创建PDF文档路径
            pdf_path = (
                os.path.join(save_path, f"{ticker_symbol}_Equity_Research_report.pdf")
                if os.path.isdir(save_path)
                else save_path
            )
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            doc = SimpleDocTemplate(pdf_path, pagesize=pagesizes.A4)
        
            # 定义两个栏位的Frame
            frame_left = Frame(
                margin,
                margin,
                left_column_width - margin * 2,
                page_height - margin * 2,
                id="left",
            )
            frame_right = Frame(
                left_column_width,
                margin,
                right_column_width - margin * 2,
                page_height - margin * 2,
                id="right",
            )

            single_frame = Frame(margin, margin, page_width-margin*2, page_height-margin*2, id='single')
            single_column_layout = PageTemplate(id='OneCol', frames=[single_frame])

            left_column_width_p2 = (page_width - margin * 3) // 2
            right_column_width_p2 = left_column_width_p2
            frame_left_p2 = Frame(
                margin,
                margin,
                left_column_width_p2 - margin * 2,
                page_height - margin * 2,
                id="left",
            )
            frame_right_p2 = Frame(
                left_column_width_p2,
                margin,
                right_column_width_p2 - margin * 2,
                page_height - margin * 2,
                id="right",
            )

            #创建PageTemplate，并添加到文档
            page_template = PageTemplate(
                id="TwoColumns", frames=[frame_left, frame_right]
            )
            page_template_p2 = PageTemplate(
                id="TwoColumns_p2", frames=[frame_left_p2, frame_right_p2]
            )

             #Define single column Frame
            single_frame = Frame(
                margin,
                margin,
                page_width - 2 * margin,
                page_height - 2 * margin,
                id="single",
            )

            # Create a PageTemplate with a single column
            single_column_layout = PageTemplate(id="OneCol", frames=[single_frame])

            doc.addPageTemplates([page_template, single_column_layout, page_template_p2])

            styles = getSampleStyleSheet()

            # 自定义样式
            custom_style = ParagraphStyle(
                name="Custom",
                parent=styles["Normal"],
                fontName=main_cn_font,
                fontSize=10,
                # leading=15,
                alignment=TA_JUSTIFY,
            )

            title_style = ParagraphStyle(
                name="TitleCustom",
                parent=styles["Title"],
                fontName=main_cn_bold_font,
                fontSize=16,
                leading=20,
                alignment=TA_LEFT,
                spaceAfter=10,
            )

            subtitle_style = ParagraphStyle(
                name="Subtitle",
                parent=styles["Heading2"],
                fontName=main_cn_bold_font,
                fontSize=14,
                leading=12,
                alignment=TA_LEFT,
                spaceAfter=6,
            )

            table_style2 = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                    ("FONT", (0, 0), (-1, -1), main_cn_font, 7),
                    ("FONT", (0, 0), (-1, 0), main_cn_bold_font, 14),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # 所有单元格左对齐
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    # 标题栏下方添加横线
                    ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
                    # 表格最下方添加横线
                    ("LINEBELOW", (0, -1), (-1, -1), 2, colors.black),
                ]
            )

            name = YFinanceUtils.get_stock_info(ticker_symbol)["shortName"]

            # 准备左栏和右栏内容
            content = []
            # 标题
            content.append(
                Paragraph(
                    f"股票研究报告: {name}",
                    title_style,
                )
            )

            # 子标题
            content.append(Paragraph("业务概况", subtitle_style))
            content.append(Paragraph(business_overview, custom_style))

            content.append(Paragraph("市场地位", subtitle_style))
            content.append(Paragraph(market_position, custom_style))

            content.append(Paragraph("经营业绩", subtitle_style))
            content.append(Paragraph(operating_results, custom_style))

            # content.append(Paragraph("Summarization", subtitle_style))
            df = FMPUtils.get_financial_metrics(ticker_symbol, years=5)
            df.reset_index(inplace=True)
            currency = YFinanceUtils.get_stock_info(ticker_symbol)["currency"]
            df.rename(columns={"index": f"FY ({currency} mn)"}, inplace=True)
            table_data = [["Financial Metrics"]]
            table_data += [df.columns.to_list()] + df.values.tolist()

            col_widths = [(left_column_width - margin * 4) / df.shape[1]] * df.shape[1]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(table_style2)
            content.append(table)

            content.append(FrameBreak())  # 用于从左栏跳到右栏

            table_style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                    ("FONT", (0, 0), (-1, -1), main_cn_font, 8),
                    ("FONT", (0, 0), (-1, 0), main_cn_bold_font, 12),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # 第一列左对齐
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                    # 第二列右对齐
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    # 标题栏下方添加横线
                    ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
                ]
            )
            full_length = right_column_width - 2 * margin

            data = [
                ["RobotMusk"],
                ["https://robotmusk.com/"],
                ["https://github.com/zhairen"],
                [f"Report date: {filing_date}"],
            ]
            col_widths = [full_length]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            # content.append(Paragraph("", custom_style))
            content.append(Spacer(1, 0.15 * inch))
            key_data = ReportAnalysisUtils.get_key_data(ticker_symbol, filing_date)
            # 表格数据
            data = [["Key data", ""]]
            data += [[k, v] for k, v in key_data.items()]
            col_widths = [full_length // 3 * 2, full_length // 3]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            # 将Matplotlib图像添加到右栏

            # 历史股价
            data = [["Share Performance"]]
            col_widths = [full_length]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            plot_path = share_performance_image_path
            width = right_column_width
            height = width // 2
            content.append(Image(plot_path, width=width, height=height))

            # 历史PE和EPS
            data = [["PE & EPS"]]
            col_widths = [full_length]
            table = Table(data, colWidths=col_widths)
            table.setStyle(table_style)
            content.append(table)

            plot_path = pe_eps_performance_image_path
            width = right_column_width
            height = width // 2
            content.append(Image(plot_path, width=width, height=height))

            # # 开始新的一页
            content.append(NextPageTemplate("OneCol"))
            content.append(PageBreak())

            content.append(Paragraph("风险评估", subtitle_style))
            #content.append(Paragraph(risk_assessment, custom_style))
            content.append(Paragraph(parse_relaxed_json(risk_assessment), custom_style))

            content.append(Paragraph("竞争对手分析", subtitle_style))
            #content.append(Paragraph(competitors_analysis, custom_style))
            content.append(Paragraph(parse_relaxed_json(competitors_analysis), custom_style))
            
            # def add_table(df, title):
            #     df = df.applymap(lambda x: "{:.2f}".format(x) if isinstance(x, float) else x)
            #     # df.columns = [col.strftime('%Y') for col in df.columns]
            #     # df.reset_index(inplace=True)
            #     # currency = ra.info['currency']
            #     df.rename(columns={"index": "segment"}, inplace=True)
            #     table_data = [[title]]
            #     table_data += [df.columns.to_list()] + df.values.tolist()

            #     table = Table(table_data)
            #     table.setStyle(table_style2)
            #     num_columns = len(df.columns)

            #     column_width = (page_width - 4 * margin) / (num_columns + 1)
            #     first_column_witdh = column_width * 2
            #     table._argW = [first_column_witdh] + [column_width] * (num_columns - 1)

            #     content.append(table)
            #     content.append(Spacer(1, 0.15 * inch))

            # if os.path.exists(f"{ra.project_dir}/outer_resource/"):
            #     Revenue10Q = pd.read_csv(
            #         f"{ra.project_dir}/outer_resource/Revenue10Q.csv",
            #     )
            #     # del Revenue10K['FY2018']
            #     # del Revenue10K['FY2019']
            #     add_table(Revenue10Q, "Revenue")

            #     Ratio10Q = pd.read_csv(
            #         f"{ra.project_dir}/outer_resource/Ratio10Q.csv",
            #     )
            #     # del Ratio10K['FY2018']
            #     # del Ratio10K['FY2019']
            #     add_table(Ratio10Q, "Ratio")

            #     Yoy10Q = pd.read_csv(
            #         f"{ra.project_dir}/outer_resource/Yoy10Q.csv",
            #     )
            #     # del Yoy10K['FY2018']
            #     # del Yoy10K['FY2019']
            #     add_table(Yoy10Q, "Yoy")

            #     plot_path = os.path.join(f"{ra.project_dir}/outer_resource/", "segment.png")
            #     width = page_width - 2 * margin
            #     height = width * 3 // 5
            #     content.append(Image(plot_path, width=width, height=height))

            # # 第二页及之后内容，使用单栏布局
            # df = ra.get_income_stmt()
            # df = df[df.columns[:3]]
            # def convert_if_money(value):
            #     if np.abs(value) >= 1000000:
            #         return value / 1000000
            #     else:
            #         return value

            # # 应用转换函数到DataFrame的每列
            # df = df.applymap(convert_if_money)

            # df.columns = [col.strftime('%Y') for col in df.columns]
            # df.reset_index(inplace=True)
            # currency = ra.info['currency']
            # df.rename(columns={'index': f'FY ({currency} mn)'}, inplace=True)  # 可选：重命名索引列为“序号”
            # table_data = [["Income Statement"]]
            # table_data += [df.columns.to_list()] + df.values.tolist()

            # table = Table(table_data)
            # table.setStyle(table_style2)
            # content.append(table)

            # content.append(FrameBreak())  # 用于从左栏跳到右栏

            # df = ra.get_cash_flow()
            # df = df[df.columns[:3]]

            # df = df.applymap(convert_if_money)

            # df.columns = [col.strftime('%Y') for col in df.columns]
            # df.reset_index(inplace=True)
            # currency = ra.info['currency']
            # df.rename(columns={'index': f'FY ({currency} mn)'}, inplace=True)  # 可选：重命名索引列为“序号”
            # table_data = [["Cash Flow Sheet"]]
            # table_data += [df.columns.to_list()] + df.values.tolist()

            # table = Table(table_data)
            # table.setStyle(table_style2)
            # content.append(table)
            # # content.append(Paragraph('This is a single column on the second page', custom_style))
            # # content.append(Spacer(1, 0.2*inch))
            # # content.append(Paragraph('More content in the single column.', custom_style))

            # 构建PDF文档
            doc.build(content)

            return "Annual report generated successfully."

        except Exception:
            return traceback.format_exc()
        
    def build_annual_report_abandon_autogen(
        ticker_symbol: Annotated[str, "ticker symbol"],
        save_path: Annotated[str, "path to save the annual report pdf"],
        operating_results: Annotated[
            str,
            "a paragraph of text: the company's income summarization from its financial report",
        ],
        market_position: Annotated[
            str,
            "a paragraph of text: the company's current situation and end market (geography), major customers (blue chip or not), market share from its financial report, avoid similar sentences also generated in the business overview section, classify it into either of the two",
        ],
        business_overview: Annotated[
            str,
            "a paragraph of text: the company's description and business highlights from its financial report",
        ],
        risk_assessment: Annotated[
            str,
            "a paragraph of text: the company's risk assessment from its financial report",
        ],
        competitors_analysis: Annotated[
            str,
            "a paragraph of text: the company's competitors analysis from its financial report and competitors' financial report",
        ],
        share_performance_image_path: Annotated[
            str, "path to the share performance image"
        ],
        pe_eps_performance_image_path: Annotated[
            str, "path to the PE and EPS performance image"
        ],
        filing_date: Annotated[str, "filing date of the analyzed financial report"],
    ) -> str:
        """
        Aggregate a company's business_overview, market_position, operating_results,
        risk assessment, competitors analysis and share performance, PE & EPS performance charts all into a PDF report.
        Chinese version.
        """
        """
        生成中文股票研究报告PDF
        
        参数:
        ticker_symbol: 股票代码
        save_path: PDF保存路径
        operating_results: 经营业绩总结
        market_position: 市场地位分析
        business_overview: 业务概述
        risk_assessment: 风险评估
        competitors_analysis: 竞争对手分析
        share_performance_image_path: 股价走势图路径
        pe_eps_performance_image_path: PE/EPS走势图路径
        filing_date: 报告日期
        
        返回:
        生成成功信息或错误跟踪
        """
        # 注册中文字体 - 修改后的方案
        try:
            # 尝试使用Noto Sans SC字体（简体中文）
            font_path_regular = "/usr/share/fonts/truetype/noto-sc/notosanscjksc-regular.ttf"
            font_path_bold = "/usr/share/fonts/truetype/noto-sc/notosansmonocjksc-bold.ttf"
            
            pdfmetrics.registerFont(TTFont("NotoSansSC", font_path_regular, _fonttype="CID"))  # 关键参数‌:ml-citation{ref="8,17" data="citationList"}
            #font.addSubset(0, 0xffff)
            pdfmetrics.registerFont(TTFont("NotoSansSC-Bold", font_path_bold, _fonttype="CID"))
                        
            pdfdoc.PDFDocumentDictionary.EmbeddedFiles = True 
            # 添加字体映射
            from reportlab.lib import fonts
            fonts.addMapping("NotoSansSC", 0, 0, "NotoSansSC")       # 常规
            fonts.addMapping("NotoSansSC", 0, 1, "NotoSansSC-Bold")  # 粗体
            
            # 设置全局中文字体
            main_cn_font = "NotoSansSC"
            main_cn_bold_font = "NotoSansSC-Bold"
            print("使用 Noto Sans SC 字体生成中文报告")
            
        except Exception as e:
            print(f"Noto Sans SC 字体注册失败: {e}")
            print("尝试使用 ReportLab 内置 CID 字体")
            
            try:
                # 尝试使用 ReportLab 内置的 CID 中文字体
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
                
                main_cn_font = "STSong-Light"
                main_cn_bold_font = "STSong-Light"  # CID 字体通常没有单独的粗体
                print("使用内置 STSong-Light CID 字体")
            except Exception as cid_error:
                print(f"CID 字体注册失败: {cid_error}")
                print("回退到 Helvetica 字体 (可能无法正确显示中文)")
                
                # 使用 Helvetica 作为最后回退
                main_cn_font = "Helvetica"
                main_cn_bold_font = "Helvetica-Bold"

        try:
            # 页面设置
            page_width, page_height = pagesizes.A4
            margin = 4
            
            # 创建PDF路径
            pdf_path = os.path.join(save_path, f"{ticker_symbol}_中文研究报告.pdf") \
                if os.path.isdir(save_path) else save_path
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            # 创建文档模板
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=pagesizes.A4,
                leftMargin=0.5*inch,
                rightMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # 创建中文样式
            styles = getSampleStyleSheet()
            
            # 中文正文样式
            cn_normal_style = ParagraphStyle(
                name="ChineseNormal",
                parent=styles["Normal"],
                fontName=main_cn_font,
                fontSize=10,
                leading=15,  # 行高
                alignment=TA_JUSTIFY,
                wordWrap='CJK',  # 中文换行
                spaceAfter=6
            )
            
            # 中文标题样式
            cn_title_style = ParagraphStyle(
                name="ChineseTitle",
                parent=styles["Title"],
                fontName=main_cn_bold_font,
                fontSize=18,
                leading=22,
                alignment=TA_CENTER,
                spaceAfter=12
            )
            
            # 中文副标题样式
            cn_subtitle_style = ParagraphStyle(
                name="ChineseSubtitle",
                parent=styles["Heading2"],
                fontName=main_cn_bold_font,
                fontSize=14,
                leading=18,
                alignment=TA_LEFT,
                spaceAfter=8,
                textColor=colors.HexColor("#1E3F66")  # 深蓝色
            )
            
            # 表格样式
            table_style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D6E4F0")),  # 表头背景
                    ("FONT", (0, 0), (-1, 0), main_cn_bold_font, 11),
                    ("FONT", (0, 1), (-1, -1), main_cn_font, 9),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1E3F66")),
                ]
            )
            
            # 右侧信息框样式
            info_table_style = TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), main_cn_font, 9),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                ]
            )
            
            # 获取股票信息
            stock_info = YFinanceUtils.get_stock_info(ticker_symbol)
            name = stock_info.get("shortName", ticker_symbol)
            currency = stock_info.get("currency", "")
            
            # 准备报告内容
            content = []
            
            # ============== 封面页 ==============
            content.append(Spacer(1, 2*inch))
            
            # 标题
            content.append(Paragraph(f"{name} 股票研究报告", cn_title_style))
            content.append(Spacer(1, 0.5*inch))
            
            # 副标题
            content.append(Paragraph("专业股票分析报告", ParagraphStyle(
                name="CoverSubtitle",
                parent=cn_normal_style,
                fontName=main_cn_bold_font,
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#3A6EA5")
            )))
            
            # 报告日期
            content.append(Spacer(1, 1.5*inch))
            content.append(Paragraph(f"报告日期: {filing_date}", ParagraphStyle(
                name="CoverDate",
                parent=cn_normal_style,
                fontName=main_cn_font,
                fontSize=11,
                alignment=TA_CENTER,
                textColor=colors.darkgrey)
            ))
            
            content.append(PageBreak())
            
            # ============== 内容页 ==============
            # 报告标题
            content.append(Paragraph(f"{name} ({ticker_symbol}) 分析报告", cn_subtitle_style))
            
            # 公司简介
            content.append(Paragraph("公司简介", cn_subtitle_style))
            content.append(Paragraph(business_overview, cn_normal_style))
            content.append(Spacer(1, 0.2*inch))
            
            # 市场地位
            content.append(Paragraph("市场地位", cn_subtitle_style))
            content.append(Paragraph(market_position, cn_normal_style))
            content.append(Spacer(1, 0.2*inch))
            
            # 经营业绩
            content.append(Paragraph("经营业绩", cn_subtitle_style))
            content.append(Paragraph(operating_results, cn_normal_style))
            content.append(Spacer(1, 0.2*inch))
            
            # 财务数据表格
            content.append(Paragraph("财务摘要 (百万" + currency + ")", cn_subtitle_style))
            df = FMPUtils.get_financial_metrics(ticker_symbol, years=5)
            if df is None:
                df = pd.DataFrame({"财务指标": [], "数值": []})
            df.reset_index(inplace=True)
            df.rename(columns={"index": "财务指标"}, inplace=True)
            
            # 格式化数值
            for col in df.columns[1:]:
                try:
                    x = df[col].astype(float)
                    #df[col] = df[col].apply(lambda x: f"{x/1e6:,.2f}" if abs(x) > 1e6 else f"{x:,.2f}")
                    df[col] = x.apply(lambda x: f"{x/1e6:,.2f}" if abs(x) > 1e6 else f"{x:,.2f}")
                except ValueError:
                    continue
                
            
            table_data = [df.columns.tolist()] + df.values.tolist()
            col_widths = [1.5*inch] + [1.2*inch] * (len(df.columns)-1)
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(table_style)
            content.append(table)
            content.append(Spacer(1, 0.3*inch))
            
            # ============== 图表页 ==============
            # 股价走势图
            content.append(Paragraph("股价走势", cn_subtitle_style))
            img_width = page_width - inch
            img_height = img_width * 0.5
            content.append(Image(share_performance_image_path, width=img_width, height=img_height))
            content.append(Spacer(1, 0.2*inch))
            
            # PE/EPS走势图
            content.append(Paragraph("估值指标 (PE/EPS)", cn_subtitle_style))
            content.append(Image(pe_eps_performance_image_path, width=img_width, height=img_height))
            
            content.append(PageBreak())
            
            # ============== 风险与竞争分析页 ==============
            # 风险评估
            content.append(Paragraph("风险评估", cn_subtitle_style))
            risk_content = parse_relaxed_json(risk_assessment)
            if not risk_content.strip():
                risk_content = "未提供风险评估内容"
            content.append(Paragraph(risk_content, cn_normal_style))
            content.append(Spacer(1, 0.3*inch))
            
            # 竞争对手分析
            content.append(Paragraph("竞争对手分析", cn_subtitle_style))
            comp_content = parse_relaxed_json(competitors_analysis)
            if not comp_content.strip():
                comp_content = "未提供竞争对手分析内容"
            content.append(Paragraph(comp_content, cn_normal_style))
            
            # 关键数据表
            content.append(Spacer(1, 0.3*inch))
            content.append(Paragraph("关键指标", cn_subtitle_style))
            #没有获取到ticker_symbol的关键数据时，返回空表格
            key_data = ReportAnalysisUtils.get_key_data(ticker_symbol, filing_date)
            #print(f"获取到的关键数据: {key_data}")

            table_data = []
            for key, value in key_data.items():
                if isinstance(value, (int, float)):
                    value = f"{value:,.2f}"
                    table_data.append([Paragraph(key, cn_normal_style), Paragraph(value, cn_normal_style)])
            #print(f"生成的表格数据: {table_data}")
            if table_data and len(key_data) > 0:
                key_table = Table(table_data, colWidths=[2*inch, 3*inch])
                key_table.setStyle(TableStyle([
                    ("FONT", (0, 0), (-1, -1), main_cn_font, 10),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ]))
                content.append(key_table)
            
            # ============== 页脚 ==============
            content.append(Spacer(1, 0.5*inch))
            footer = [
                Paragraph("免责声明: 本报告仅供参考，不构成任何投资建议", 
                            ParagraphStyle(name="Footer", parent=cn_normal_style, fontSize=8)),
                Paragraph(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                            ParagraphStyle(name="FooterDate", parent=cn_normal_style, fontSize=8)),
                Paragraph("数据来源: Yahoo Finance, Financial Modeling Prep", 
                            ParagraphStyle(name="FooterSource", parent=cn_normal_style, fontSize=8))
            ]
            footer_table = Table([footer], colWidths=[page_width - inch])
            footer_table.setStyle(TableStyle([
                ("FONT", (0, 0), (-1, -1), main_cn_font, 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.grey),
            ]))
            content.append(footer_table)
            
            # 生成PDF
            doc.build(content)
            return f"中文研究报告已成功生成: {os.path.abspath(pdf_path)}"
    
        except Exception as e:
            print(f"生成中文研究报告时发生错误: {e}")
            return traceback.format_exc()
            