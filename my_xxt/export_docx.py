# -*- coding = utf-8 -*-
# @Time :2024/6/1
# @Author :Claude Code
# @File :  export_docx.py
"""
学习通作业导出为Word(docx)模块
支持将JSON格式的答案文件导出为格式化的Word文档
"""
import os
import re
from datetime import datetime
from json import JSONDecodeError

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from my_xxt.answer_files import answer_json_files, read_answer_json


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Return a filename safe for Windows, macOS, and Linux."""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, filename).strip()
    cleaned = cleaned.rstrip(". ")
    return cleaned or "未命名"


def course_matches_query(course_name: str, query: str) -> bool:
    query = query.strip()
    if not query:
        return False
    return query in course_name


def set_cell_shading(cell, color):
    """设置单元格背景色"""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color)
    shading_elm.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_border(cell, **kwargs):
    """设置单元格边框"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        if edge in kwargs:
            element = OxmlElement(f'w:{edge}')
            for attr, val in kwargs[edge].items():
                element.set(qn(f'w:{attr}'), str(val))
            tcBorders.append(element)
    tcPr.append(tcBorders)


def add_formatted_paragraph(doc, text, style=None, bold=False, font_size=None,
                            color=None, alignment=None, font_name='宋体',
                            space_after=None, space_before=None):
    """添加格式化段落"""
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    run.bold = bold

    if font_size:
        run.font.size = Pt(font_size)
    if color:
        run.font.color.rgb = RGBColor(*color)

    run.font.name = font_name
    # 设置中文字体
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), font_name)
    rPr.insert(0, rFonts)

    if alignment is not None:
        p.alignment = alignment

    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if space_before is not None:
        p.paragraph_format.space_before = Pt(space_before)

    return p


def generate_docx_from_json(json_path: str, output_path: str = None) -> str:
    """
    将单个作业的JSON文件导出为Word文档

    :param json_path: JSON答案文件的路径
    :param output_path: 输出Word文件的路径（可选，默认与JSON同目录同文件名）
    :return: 生成的docx文件路径
    """
    # 读取JSON文件
    data = read_answer_json(json_path)

    # 提取信息
    info = data.get('info', {})
    course_name = info.get('course_name', '未知课程')
    work_name = info.get('work_name', '未知作业')

    # 提取题目列表（排除info字段）
    questions = None
    for key in data:
        if key != 'info' and isinstance(data[key], list):
            questions = data[key]
            break

    if not questions:
        raise ValueError(f"JSON文件中未找到题目数据: {json_path}")

    # 创建Word文档
    doc = Document()

    # 设置默认字体
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(11)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # ---- 封面/标题区域 ----
    # 添加空行
    for _ in range(2):
        doc.add_paragraph()

    # 主标题
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(course_name)
    title_run.bold = True
    title_run.font.size = Pt(22)
    title_run.font.name = '黑体'
    rPr = title_run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), '黑体')
    rPr.insert(0, rFonts)

    # 副标题
    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle_p.add_run(f'—— {work_name} ——')
    subtitle_run.font.size = Pt(16)
    subtitle_run.font.name = '黑体'
    subtitle_run.font.color.rgb = RGBColor(0x44, 0x62, 0x88)
    rPr = subtitle_run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), '黑体')
    rPr.insert(0, rFonts)

    doc.add_paragraph()

    # 导出信息
    info_p = doc.add_paragraph()
    info_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info_run = info_p.add_run(f'导出时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M")}    题目总数：{len(questions)} 题')
    info_run.font.size = Pt(10)
    info_run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # 分页
    doc.add_page_break()

    # ---- 题目内容 ----
    for idx, q in enumerate(questions, 1):
        question_type = q.get('type', '未知题型')
        question_title = q.get('title', '无题目')
        question_answer = q.get('answer', '无答案')
        question_options = q.get('option', [])

        # 题型标签
        type_colors = {
            '单选题': (0x40, 0x9E, 0xFF),
            '多选题': (0x67, 0xC2, 0x3A),
            '判断题': (0xE6, 0xA2, 0x3C),
            '填空题': (0x90, 0x94, 0x99),
            '简答题': (0x00, 0xB5, 0x78),
            '论述题': (0x9C, 0x27, 0xB0),
            '编程题': (0xF5, 0x6C, 0x6C),
            '其他': (0x60, 0x60, 0x60),
        }
        label_color = type_colors.get(question_type, (0x60, 0x60, 0x60))

        # 题目编号 + 题型标签
        q_header = doc.add_paragraph()
        q_header.paragraph_format.space_before = Pt(16)
        q_header.paragraph_format.space_after = Pt(6)

        # 题号
        num_run = q_header.add_run(f'第{idx}题 ')
        num_run.bold = True
        num_run.font.size = Pt(13)
        num_run.font.name = '微软雅黑'

        # 题型标签
        type_run = q_header.add_run(f' [{question_type}]')
        type_run.bold = True
        type_run.font.size = Pt(11)
        type_run.font.color.rgb = RGBColor(*label_color)
        type_run.font.name = '微软雅黑'

        # 题目文本
        q_text = doc.add_paragraph()
        q_text.paragraph_format.space_after = Pt(8)
        q_text.paragraph_format.left_indent = Cm(0.5)
        text_run = q_text.add_run(question_title)
        text_run.font.size = Pt(12)
        text_run.font.name = '宋体'

        # 选项（如果有的话）
        if question_options:
            # 创建选项表格
            num_cols = 2
            num_rows = (len(question_options) + 1) // 2
            if num_rows == 0:
                num_rows = 1

            table = doc.add_table(rows=num_rows, cols=num_cols)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            for i, opt in enumerate(question_options):
                row = i // 2
                col = i % 2
                cell = table.cell(row, col)

                # 清空默认段落
                cell.paragraphs[0].clear()

                opt_run = cell.paragraphs[0].add_run(opt)
                opt_run.font.size = Pt(10.5)
                opt_run.font.name = '宋体'

                # 如果是正确答案，高亮显示
                answer_letter = question_answer.strip()
                if question_type in ('单选题', '判断题') and opt.startswith(answer_letter):
                    set_cell_shading(cell, 'D4EDDA')  # 绿色背景
                    opt_run.bold = True
                    opt_run.font.color.rgb = RGBColor(0x15, 0x57, 0x24)
                elif question_type == '多选题':
                    opt_letter = opt.split('.')[0].strip() if '.' in opt else opt.split(' ')[0].strip()
                    if opt_letter in answer_letter:
                        set_cell_shading(cell, 'D4EDDA')
                        opt_run.bold = True
                        opt_run.font.color.rgb = RGBColor(0x15, 0x57, 0x24)

            doc.add_paragraph()  # 表格后的间距

        # 答案区域
        answer_p = doc.add_paragraph()
        answer_p.paragraph_format.space_before = Pt(4)
        answer_p.paragraph_format.left_indent = Cm(0.5)

        answer_label = answer_p.add_run('答案：')
        answer_label.bold = True
        answer_label.font.size = Pt(11)
        answer_label.font.color.rgb = RGBColor(0xC0, 0x44, 0x32)

        # 格式化答案
        if isinstance(question_answer, list):
            answer_text = '；'.join(str(a) for a in question_answer)
        else:
            answer_text = str(question_answer)

        answer_run = answer_p.add_run(answer_text)
        answer_run.font.size = Pt(11)
        answer_run.font.color.rgb = RGBColor(0xC0, 0x44, 0x32)
        answer_run.font.name = '宋体'

        # 分隔线
        if idx < len(questions):
            separator = doc.add_paragraph()
            separator.paragraph_format.space_before = Pt(8)
            separator.paragraph_format.space_after = Pt(2)
            sep_run = separator.add_run('─' * 50)
            sep_run.font.size = Pt(8)
            sep_run.font.color.rgb = RGBColor(0xDD, 0xDD, 0xDD)

    # ---- 页脚说明 ----
    doc.add_paragraph()
    footer_p = doc.add_paragraph()
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_p.add_run('— 本文件由 new_xxt 学习通助手自动生成 —')
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
    footer_run.italic = True

    # 确定输出路径
    if output_path is None:
        base_dir = os.path.dirname(json_path)
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        output_path = os.path.join(base_dir, f'{base_name}.docx')

    # 保存文档
    doc.save(output_path)
    return output_path


def batch_export_to_docx(json_dir: str, output_dir: str = None, merge: bool = False) -> list:
    """
    批量将answers目录下的所有JSON文件导出为Word文档

    :param json_dir: JSON答案文件所在目录
    :param output_dir: 输出目录（可选，默认与json_dir相同）
    :param merge: 是否合并为一个文档（True=合并为一个文件，False=每个JSON单独导出）
    :return: 生成的docx文件路径列表
    """
    if output_dir is None:
        output_dir = json_dir

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 获取所有JSON文件
    json_files = answer_json_files(json_dir)

    if not json_files:
        raise FileNotFoundError(f"目录中未找到JSON文件: {json_dir}")

    generated_files = []

    if merge:
        # 合并导出：所有作业放到一个文档
        doc = Document()

        # 设置默认字体
        style = doc.styles['Normal']
        font = style.font
        font.name = '宋体'
        font.size = Pt(11)
        style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

        # 封面
        for _ in range(3):
            doc.add_paragraph()

        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run('学习通作业汇总')
        title_run.bold = True
        title_run.font.size = Pt(24)
        title_run.font.name = '黑体'

        doc.add_paragraph()
        info_p = doc.add_paragraph()
        info_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        info_run = info_p.add_run(f'导出时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M")}    共 {len(json_files)} 份作业')
        info_run.font.size = Pt(11)
        info_run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

        doc.add_page_break()

        for file_idx, json_file in enumerate(sorted(json_files), 1):
            json_path = os.path.join(json_dir, json_file)
            try:
                data = read_answer_json(json_path)
            except (OSError, JSONDecodeError, TypeError, ValueError) as e:
                print(f"导出失败 {json_file}: {e}")
                continue

            info = data.get('info', {})
            course_name = info.get('course_name', '未知课程')
            work_name = info.get('work_name', '未知作业')

            questions = None
            for key in data:
                if key != 'info' and isinstance(data[key], list):
                    questions = data[key]
                    break

            if not questions:
                continue

            # 作业标题
            h_p = doc.add_paragraph()
            h_p.paragraph_format.space_before = Pt(12)
            h_p.paragraph_format.space_after = Pt(6)
            h_run = h_p.add_run(f'{file_idx}. {course_name} — {work_name}（共{len(questions)}题）')
            h_run.bold = True
            h_run.font.size = Pt(16)
            h_run.font.name = '黑体'

            # 导出每道题
            for idx, q in enumerate(questions, 1):
                question_type = q.get('type', '未知题型')
                question_title = q.get('title', '无题目')
                question_answer = q.get('answer', '无答案')
                question_options = q.get('option', [])

                type_colors = {
                    '单选题': (0x40, 0x9E, 0xFF), '多选题': (0x67, 0xC2, 0x3A),
                    '判断题': (0xE6, 0xA2, 0x3C), '填空题': (0x90, 0x94, 0x99),
                    '简答题': (0x00, 0xB5, 0x78), '论述题': (0x9C, 0x27, 0xB0),
                    '编程题': (0xF5, 0x6C, 0x6C), '其他': (0x60, 0x60, 0x60),
                }
                label_color = type_colors.get(question_type, (0x60, 0x60, 0x60))

                q_header = doc.add_paragraph()
                q_header.paragraph_format.space_before = Pt(10)
                q_header.paragraph_format.space_after = Pt(4)

                num_run = q_header.add_run(f'第{idx}题 ')
                num_run.bold = True
                num_run.font.size = Pt(11)

                type_run = q_header.add_run(f' [{question_type}]')
                type_run.bold = True
                type_run.font.size = Pt(9)
                type_run.font.color.rgb = RGBColor(*label_color)

                q_text = doc.add_paragraph()
                q_text.paragraph_format.left_indent = Cm(0.5)
                q_text.paragraph_format.space_after = Pt(4)
                text_run = q_text.add_run(question_title)
                text_run.font.size = Pt(10.5)

                if question_options:
                    num_cols = 2
                    num_rows = (len(question_options) + 1) // 2 or 1
                    table = doc.add_table(rows=num_rows, cols=num_cols)
                    table.style = 'Table Grid'
                    table.alignment = WD_TABLE_ALIGNMENT.CENTER

                    for i, opt in enumerate(question_options):
                        row = i // 2
                        col = i % 2
                        cell = table.cell(row, col)
                        cell.paragraphs[0].clear()
                        opt_run = cell.paragraphs[0].add_run(opt)
                        opt_run.font.size = Pt(9)

                        answer_letter = str(question_answer).strip()
                        if question_type == '单选题' and opt.startswith(answer_letter):
                            set_cell_shading(cell, 'D4EDDA')
                            opt_run.bold = True
                        elif question_type == '多选题':
                            opt_letter = opt.split('.')[0].strip() if '.' in opt else opt.split(' ')[0].strip()
                            if opt_letter in answer_letter:
                                set_cell_shading(cell, 'D4EDDA')
                                opt_run.bold = True

                answer_p = doc.add_paragraph()
                answer_p.paragraph_format.left_indent = Cm(0.5)
                answer_label = answer_p.add_run('答案：')
                answer_label.bold = True
                answer_label.font.size = Pt(10)
                answer_label.font.color.rgb = RGBColor(0xC0, 0x44, 0x32)

                answer_text = '；'.join(str(a) for a in question_answer) if isinstance(question_answer, list) else str(question_answer)
                answer_run = answer_p.add_run(answer_text)
                answer_run.font.size = Pt(10)
                answer_run.font.color.rgb = RGBColor(0xC0, 0x44, 0x32)

            # 作业之间分页
            if file_idx < len(json_files):
                doc.add_page_break()

        # 页脚
        doc.add_paragraph()
        footer_p = doc.add_paragraph()
        footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer_p.add_run('— 本文件由 new_xxt 学习通助手自动生成 —')
        footer_run.font.size = Pt(9)
        footer_run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
        footer_run.italic = True

        output_path = os.path.join(output_dir, f'学习通作业汇总_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
        doc.save(output_path)
        generated_files.append(output_path)

    else:
        # 每个JSON单独导出
        for json_file in sorted(json_files):
            json_path = os.path.join(json_dir, json_file)
            try:
                output_path = generate_docx_from_json(json_path,
                    os.path.join(output_dir, os.path.splitext(json_file)[0] + '.docx'))
                generated_files.append(output_path)
            except Exception as e:
                print(f"导出失败 {json_file}: {e}")

    return generated_files


def export_course_assignments_to_docx(course_name: str, json_dir: str, output_path: str = None) -> str:
    """
    导出指定课程的所有作业到一个Word文档

    :param course_name: 课程名称（用于筛选JSON文件中的课程）
    :param json_dir: JSON答案文件目录
    :param output_path: 输出路径（可选）
    :return: 生成的docx文件路径
    """
    json_files = answer_json_files(json_dir)

    if not json_files:
        raise FileNotFoundError(f"目录中未找到JSON文件: {json_dir}")

    # 筛选属于该课程的JSON文件
    course_files = []
    for json_file in json_files:
        json_path = os.path.join(json_dir, json_file)
        try:
            data = read_answer_json(json_path)
        except (OSError, JSONDecodeError, TypeError, ValueError):
            continue
        info = data.get('info', {})
        if course_matches_query(info.get('course_name', ''), course_name):
            course_files.append(json_path)

    if not course_files:
        raise ValueError(f"未找到课程'{course_name}'的答案文件")

    # 创建文档
    doc = Document()

    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(11)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # 封面
    for _ in range(3):
        doc.add_paragraph()

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(course_name)
    title_run.bold = True
    title_run.font.size = Pt(22)
    title_run.font.name = '黑体'

    doc.add_paragraph()
    info_p = doc.add_paragraph()
    info_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info_run = info_p.add_run(f'作业汇总  ·  共 {len(course_files)} 份作业  ·  {datetime.now().strftime("%Y年%m月%d日")}')
    info_run.font.size = Pt(11)
    info_run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    doc.add_page_break()

    # 逐个作业导出
    for file_idx, json_path in enumerate(sorted(course_files), 1):
        data = read_answer_json(json_path)

        info = data.get('info', {})
        work_name = info.get('work_name', '未知作业')

        questions = None
        for key in data:
            if key != 'info' and isinstance(data[key], list):
                questions = data[key]
                break

        if not questions:
            continue

        # 作业标题
        h_p = doc.add_paragraph()
        h_p.paragraph_format.space_before = Pt(12)
        h_run = h_p.add_run(f'作业{file_idx}：{work_name}（共{len(questions)}题）')
        h_run.bold = True
        h_run.font.size = Pt(15)
        h_run.font.name = '黑体'

        for idx, q in enumerate(questions, 1):
            # ... (same as batch export logic)
            question_type = q.get('type', '未知题型')
            question_title = q.get('title', '无题目')
            question_answer = q.get('answer', '无答案')
            question_options = q.get('option', [])

            type_colors = {
                '单选题': (0x40, 0x9E, 0xFF), '多选题': (0x67, 0xC2, 0x3A),
                '判断题': (0xE6, 0xA2, 0x3C), '填空题': (0x90, 0x94, 0x99),
                '简答题': (0x00, 0xB5, 0x78), '论述题': (0x9C, 0x27, 0xB0),
                '编程题': (0xF5, 0x6C, 0x6C), '其他': (0x60, 0x60, 0x60),
            }
            label_color = type_colors.get(question_type, (0x60, 0x60, 0x60))

            q_header = doc.add_paragraph()
            q_header.paragraph_format.space_before = Pt(8)
            q_header.paragraph_format.space_after = Pt(4)

            num_run = q_header.add_run(f'{idx}. ')
            num_run.bold = True
            num_run.font.size = Pt(11)

            type_run = q_header.add_run(f'[{question_type}]')
            type_run.bold = True
            type_run.font.size = Pt(9)
            type_run.font.color.rgb = RGBColor(*label_color)

            q_text = doc.add_paragraph()
            q_text.paragraph_format.left_indent = Cm(0.5)
            q_text.paragraph_format.space_after = Pt(4)
            text_run = q_text.add_run(question_title)
            text_run.font.size = Pt(10.5)

            if question_options:
                num_cols = 2
                num_rows = (len(question_options) + 1) // 2 or 1
                table = doc.add_table(rows=num_rows, cols=num_cols)
                table.style = 'Table Grid'
                table.alignment = WD_TABLE_ALIGNMENT.CENTER

                for i, opt in enumerate(question_options):
                    row = i // 2
                    col = i % 2
                    cell = table.cell(row, col)
                    cell.paragraphs[0].clear()
                    opt_run = cell.paragraphs[0].add_run(opt)
                    opt_run.font.size = Pt(9)

                    answer_letter = str(question_answer).strip()
                    if question_type == '单选题' and opt.startswith(answer_letter):
                        set_cell_shading(cell, 'D4EDDA')
                        opt_run.bold = True
                    elif question_type == '多选题':
                        opt_letter = opt.split('.')[0].strip() if '.' in opt else opt.split(' ')[0].strip()
                        if opt_letter in answer_letter:
                            set_cell_shading(cell, 'D4EDDA')
                            opt_run.bold = True

            answer_p = doc.add_paragraph()
            answer_p.paragraph_format.left_indent = Cm(0.5)
            answer_label = answer_p.add_run('答案：')
            answer_label.bold = True
            answer_label.font.size = Pt(10)
            answer_label.font.color.rgb = RGBColor(0xC0, 0x44, 0x32)

            answer_text = '；'.join(str(a) for a in question_answer) if isinstance(question_answer, list) else str(question_answer)
            answer_run = answer_p.add_run(answer_text)
            answer_run.font.size = Pt(10)
            answer_run.font.color.rgb = RGBColor(0xC0, 0x44, 0x32)

        if file_idx < len(course_files):
            doc.add_page_break()

    # 页脚
    doc.add_paragraph()
    footer_p = doc.add_paragraph()
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_p.add_run('— 本文件由 new_xxt 学习通助手自动生成 —')
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
    footer_run.italic = True

    if output_path is None:
        output_path = os.path.join(json_dir, f'{sanitize_filename(course_name)}_作业汇总.docx')

    doc.save(output_path)
    return output_path
