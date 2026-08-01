from pathlib import Path
import subprocess
import sys
import argparse
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import multiprocessing

parser = argparse.ArgumentParser(description='并发编译LaTeX项目（自动CPU优化）')
parser.add_argument('--sub', type=str, default='true', 
                       help='是否为子项目编译 (true/false，默认为true)')
parser.add_argument('--c', type=str, default='false', 
                       help='是否是计算机 (true/false，默认为false)')
    
args = parser.parse_args()

is_sub = args.sub.lower() == 'true'
is_c = args.c.lower() == 'true'

pad_template_tex = r'''\documentclass[oneside]{book}

\usepackage[fontset=ubuntu,heading=true,zihao=-4]{ctex}
\usepackage[landscape,
    width = 250mm,
    height=178mm,
    margin=1.8cm,      % 均匀边距
    includefoot,
    footskip=0.8cm,
    headheight=15pt]{geometry}
\usepackage[bookmarksnumbered]{hyperref}
\usepackage{exam-zh-chinese-english}
\usepackage{exam-zh-font}
\usepackage{exam-zh-symbols}
\usepackage{exam-zh-question}
\usepackage{exam-zh-choices}
\usepackage{exam-zh-textfigure}
\usepackage{setspace}
\usepackage{fancyhdr}
\usepackage{xparse}
\usepackage{pifont}
\usepackage{nccmath}
\usepackage{tocloft}
\usepackage{multicol}
\usepackage{titlesec}
\usepackage{fancyvrb}
\UseTblrLibrary{diagbox}

\setlength{\cftsecindent}{1.5em}      % section缩进，默认2.2em
\setlength{\cftsubsecindent}{0em}   % subsection缩进，默认4.4em

\addtocontents{toc}{\protect\setstretch{1.3}} 


\hypersetup{
    hidelinks,
}
\ctexset{
    section = {
        name   = {第,章},           % 中文：第1节
        number =  \chinese{section},  % 阿拉伯数字
        aftername = \quad,          % 名称和标题之间的间距
        format = \Large\bfseries\centering
    },
    subsection = {
        name   = {},        % 去掉"节"字
        number = {},        % 去掉数字
        aftername = \ ,     % 无内容
        format = \large\bfseries\centering\newpage
    }
}

\NewDocumentEnvironment{mcol}{ O{0.45\textwidth} O{t} }{%
    \begin{minipage}[#2]{#1}%
}{%
    \end{minipage}%
    \hfill%
}

\newcommand{\cone}{\ding{172}}
\newcommand{\ctwo}{\ding{173}}
\newcommand{\cthree}{\ding{174}}
\newcommand{\cfour}{\ding{175}}

\DeclareMathOperator{\Cov}{Cov}
\DeclareMathOperator{\grad}{grad}
\DeclareMathOperator{\rot}{rot}
\DeclareMathOperator{\divop}{div}

\setstretch{1.5}

\everymath{\displaystyle}

\pagestyle{fancy}
\fancyhf{}  % 清除所有页眉页脚
\renewcommand{\headrulewidth}{0pt}  % 去掉页眉横线
\fancyfoot[C]{\thepage}

\newcommand{\pp}{(\quad)}
\newcommand{\blankline}{\rule[-1pt]{1.5cm}{0.4pt}}

\let\oldvfill\vfill  % 保存原来的\vfill命令
\renewcommand{\vfill}{\newpage}

\graphicspath{
  {./}        % 当前目录
  {../}       % 上一层
  {../../}    % 上两层
  {../../../} % 上三层
  {../../../../} % 上四层（通常足够）
}

\title{{title}}
\author{xiaochuan}
\date{}

\renewcommand{\contentsname}{目录}

\begin{document}

\frontmatter
\maketitle

\tableofcontents


\mainmatter

\input{main}

\end{document}

'''

exam_math_template_tex = r'''\let\stop\empty
\documentclass{exam-zh}

\usepackage{setspace}
\usepackage{fancyvrb}
\UseTblrLibrary{diagbox}
\usepackage{caption}

\examsetup{
  page/size=a4paper,
  paren/show-paren=true,
  paren/show-answer=true,
  fillin/type = line,
  fillin/no-answer-type=none,
  solution/show-solution=show-stay,
  solution/label-indentation=false,
}

\newcommand{\pp}{(\quad)}
\newcommand{\blankline}{\rule[-1pt]{1.5cm}{0.4pt}}

\DeclareMathOperator{\Cov}{Cov}
\DeclareMathOperator{\grad}{grad}
\DeclareMathOperator{\rot}{rot}
\DeclareMathOperator{\divop}{div}


\newcommand{\qrcode}{
  \begin{tikzpicture}
    \node[rectangle,
          draw=blue,            % 固定颜色
          dashed,
          line width=1pt,
          rounded corners=5pt,
          inner sep=10pt,
          fill=blue!20,         % 固定背景色
          minimum width=4cm,    % 固定宽度
          minimum height=2cm]   % 固定高度
    {试卷条形码};           % 固定内容
  \end{tikzpicture}
}

\newenvironment{normalfontmath}{%
    \everymath{\displaystyle\rm}%  行内公式正体（如需取消\displaystyle可去掉）
    \everydisplay{\rm}%           行间公式正体
}{}

\graphicspath{
  {./}        % 当前目录
  {../}       % 上一层
  {../../}    % 上两层
  {../../../} % 上三层
  {../../../../} % 上四层（通常足够）
}

\everymath{\displaystyle}

\title{{title}}

% \secret

\subject{数学(一)}

\begin{document}
\secret

\maketitle

\vspace{-10pt}
\begin{center}
\Large (科目代码：301)
\end{center}

\begin{notice}[label=\makebox[\textwidth][c]{\heiti\textnormal{考生注意事项}},top-sep=20pt]
  \item 答题前，考生须在试题册指定位置上填写考生姓名和考生编号；在答题卡指定位置上填写报考单位、考生姓名和考生编号，并涂写考生编号信息点。
  \item 考生须把试题册上的“试卷条形码”粘贴条取下，粘贴在答题卡的“试卷条形码粘贴位置”框中。不按规定粘贴条形码而影响评卷结果的，责任由考生自负。
  \item 选择题的答案必须涂写在答题卡相应题号的选项上，非选择题的答案必须书写在答题卡指定位置的边框区域内。超出答题区域书写的答案无效；在草稿纸、试题册上答题无效。
  \item 填（书）写部分必须使用黑色字迹签字笔或者钢笔书写，字迹工整、笔记清楚；涂写部分必须使用2B铅笔填涂。
  \item 考试结束，将答题卡和试题册按规定交回。
  \item 本次考试时长为3小时。
\end{notice}

\vspace{50pt}

\begin{center}

\qrcode

\vspace{20pt}

（以下信息考生必须认真填写）
\vspace{10pt}

\begin{tblr}{
width = 0.6\textwidth,
hlines,
vlines,
colspec = {Q[l, wd=1.6cm] *{15}{X[c]}},
cell{2}{2} = {r=1,c=15}{c}
}
考生编号 & & & & & & & & & & & & & & & \\
考生姓名 & & & & & & & & & & & & & & & \\
\end{tblr}
\end{center}

\newpage
{content}

\end{document}'''

exam_c_template_tex = r'''\let\stop\empty
\documentclass{exam-zh}

\usepackage{setspace}
\usepackage{fancyvrb}
\UseTblrLibrary{diagbox}

\examsetup{
  page/size=a4paper,
  paren/show-paren=true,
  paren/show-answer=true,
  fillin/type = line,
  fillin/no-answer-type=none,
  solution/show-solution=show-stay,
  solution/label-indentation=false,
  page/foot-content=试卷第 ; 页（共 ; 页）
}

\newcommand{\pp}{(\quad)}
\newcommand{\blankline}{\rule[-1pt]{1.5cm}{0.4pt}}

\DeclareMathOperator{\Cov}{Cov}
\DeclareMathOperator{\grad}{grad}
\DeclareMathOperator{\rot}{rot}
\DeclareMathOperator{\divop}{div}


\newcommand{\qrcode}{
  \begin{tikzpicture}
    \node[rectangle,
          draw=blue,            % 固定颜色
          dashed,
          line width=1pt,
          rounded corners=5pt,
          inner sep=10pt,
          fill=blue!20,         % 固定背景色
          minimum width=4cm,    % 固定宽度
          minimum height=2cm]   % 固定高度
    {试卷条形码};           % 固定内容
  \end{tikzpicture}
}

\graphicspath{
  {./}        % 当前目录
  {../}       % 上一层
  {../../}    % 上两层
  {../../../} % 上三层
  {../../../../} % 上四层（通常足够）
}

\everymath{\displaystyle}

\title{{title}}

% \secret

\subject{计算机专业基础}

\begin{document}
\secret

\maketitle

\vspace{-10pt}
\begin{center}
\Large (科目代码：408)
\end{center}

\begin{notice}[label=\makebox[\textwidth][c]{\heiti\textnormal{考生注意事项}},top-sep=20pt]
  \item 答题前，考生须在试题册指定位置上填写考生姓名和考生编号；在答题卡指定位置上填写报考单位、考生姓名和考生编号，并涂写考生编号信息点。
  \item 考生须把试题册上的“试卷条形码”粘贴条取下，粘贴在答题卡的“试卷条形码粘贴位置”框中。不按规定粘贴条形码而影响评卷结果的，责任由考生自负。
  \item 选择题的答案必须涂写在答题卡相应题号的选项上，非选择题的答案必须书写在答题卡指定位置的边框区域内。超出答题区域书写的答案无效；在草稿纸、试题册上答题无效。
  \item 填（书）写部分必须使用黑色字迹签字笔或者钢笔书写，字迹工整、笔记清楚；涂写部分必须使用2B铅笔填涂。
  \item 考试结束，将答题卡和试题册按规定交回。
  \item 本次考试时长为3小时。
\end{notice}

\vspace{50pt}

\begin{center}

\qrcode

\vspace{20pt}

（以下信息考生必须认真填写）
\vspace{10pt}

\begin{tblr}{
width = 0.6\textwidth,
hlines,
vlines,
colspec = {Q[l, wd=1.6cm] *{15}{X[c]}},
cell{2}{2} = {r=1,c=15}{c}
}
考生编号 & & & & & & & & & & & & & & & \\
考生姓名 & & & & & & & & & & & & & & & \\
\end{tblr}
\end{center}

\newpage
{content}

\end{document}'''

exam_template_tex = ''

if is_c:
    exam_template_tex = exam_c_template_tex
else:
    exam_template_tex = exam_math_template_tex

# 获取CPU核心数
def get_cpu_count():
    """获取CPU核心数，考虑超线程"""
    try:
        # 物理核心数
        physical_cores = os.cpu_count() or 1
        
        # 如果支持，获取逻辑核心数（考虑超线程）
        if hasattr(os, 'sched_getaffinity'):
            logical_cores = len(os.sched_getaffinity(0))
        else:
            logical_cores = multiprocessing.cpu_count()
        
        # 返回逻辑核心数，但至少为2
        return max(logical_cores, 2)
    except:
        return 4  # 默认值

# 智能计算并发数
def calculate_concurrency(cpu_count):
    """
    智能计算并发数
    考虑到LaTeX编译是I/O和CPU混合型任务
    """
    if cpu_count <= 4:
        # 4核以下：全部使用
        projects_conc = max(cpu_count * 2, 2)
        tasks_conc = 1  # 每个项目pad和exam并发
    elif cpu_count <= 8:
        # 4-8核：留一个核心给系统
        projects_conc = cpu_count - 1
        tasks_conc = 2
    else:
        # 8核以上：留2个核心给系统，项目并发数=cpu_count-2
        projects_conc = cpu_count - 2
        tasks_conc = min(2, cpu_count // 4)  # 大核心系统可以增加任务并发
    
    return projects_conc, tasks_conc

# 创建线程锁确保输出不乱序
print_lock = threading.Lock()

def thread_safe_print(*args, **kwargs):
    """线程安全的打印函数"""
    with print_lock:
        print(*args, **kwargs)

def compile_sub_pad(entry, name, task_id):
    """编译pad版本的LaTeX文档"""
    thread_safe_print(f"[任务{task_id}] 🚀 开始编译PAD: {name}")
    
    # 生成LaTeX模板内容（保持不变）
    template_tex = pad_template_tex
    out_tex = template_tex.replace("{title}", name)

    # 写入文件
    current_dir = Path.cwd()
    filepath = current_dir.joinpath(entry, 'pad.tex')
    with open(filepath, "w", encoding='utf-8') as f:
        f.write(out_tex)
    
    thread_safe_print(f"[任务{task_id}] 📄 生成PAD文件: {filepath}")
    
    # 构建编译命令
    cmd = [
        'latexmk',
        '-xelatex',
        f'-jobname={name}_pad',
        '-cd',
        str(filepath)
    ]
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        stdout, stderr = process.communicate()
        elapsed_time = time.time() - start_time
        
        if process.returncode == 0:
            thread_safe_print(f"[任务{task_id}] ✅ PAD编译成功！耗时: {elapsed_time:.1f}秒")
            return True, f"pad_{task_id}"
        else:
            thread_safe_print(f"[任务{task_id}] ❌ PAD编译失败！耗时: {elapsed_time:.1f}秒")
            if stderr:
                with print_lock:
                    print(f"[任务{task_id}] 错误信息:")
                    print(stderr[:500])
            return False, f"pad_{task_id}"
            
    except Exception as e:
        thread_safe_print(f"[任务{task_id}] 💥 PAD编译异常: {str(e)}")
        return False, f"pad_{task_id}"

def compile_sub_exam(entry, name, task_id):
    """编译exam版本的LaTeX文档"""
    thread_safe_print(f"[任务{task_id}] 🚀 开始编译EXAM: {name}")
    
    current_dir = Path.cwd()
    input_path = current_dir.joinpath(entry, 'main.tex')
    output_path = current_dir.joinpath(entry, 'exam.tex')
    
    try:
        with open(input_path, "r", encoding='utf-8') as f:
            _input_tex = f.read().replace(r'\newpage', '').replace(r'\vfill', '')
            input_tex = re.sub(r'VerbatimInput.*(codes.+)', r'VerbatimInput{\1', _input_tex)

        out_tex = exam_template_tex.replace('{title}', name).replace('{content}', input_tex)
        
        with open(output_path, "w", encoding='utf-8') as f_out:
            f_out.write(out_tex)
        
        thread_safe_print(f"[任务{task_id}] 📄 生成EXAM文件: {output_path}")
        
    except Exception as e:
        thread_safe_print(f"[任务{task_id}] ❌ 读取/写入文件失败: {str(e)}")
        return False, f"exam_{task_id}"
    
    cmd = [
        'latexmk',
        '-xelatex',
        f'-jobname={name}_exam',
        '-cd',
        str(output_path)
    ]
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        stdout, stderr = process.communicate()
        elapsed_time = time.time() - start_time
        
        if process.returncode == 0:
            thread_safe_print(f"[任务{task_id}] ✅ EXAM编译成功！耗时: {elapsed_time:.1f}秒")
            return True, f"exam_{task_id}"
        else:
            thread_safe_print(f"[任务{task_id}] ❌ EXAM编译失败！耗时: {elapsed_time:.1f}秒")
            if stderr:
                with print_lock:
                    print(f"[任务{task_id}] 错误信息:")
                    print(stderr[:500])
            return False, f"exam_{task_id}"
            
    except Exception as e:
        thread_safe_print(f"[任务{task_id}] 💥 EXAM编译异常: {str(e)}")
        return False, f"exam_{task_id}"

def compile_sub_project(item, task_id, max_tasks_per_project):
    """并发编译单个项目的pad和exam版本"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_tasks_per_project) as executor:
        futures = []
        
        if not is_c:
            pad_future = executor.submit(compile_sub_pad, item['entry'], item['name'], f"{task_id}_pad")
            futures.append(pad_future)
        
        exam_future = executor.submit(compile_sub_exam, item['entry'], item['name'], f"{task_id}_exam")
        futures.append(exam_future)
        
        for future in as_completed(futures):
            success, task_type = future.result()
            results.append((success, task_type))
    
    all_success = all(success for success, _ in results)
    return all_success, task_id, item['name']

def get_list():
    """获取项目列表"""
    l = []
    current_dir = Path.cwd()
    contents_path = current_dir.joinpath('contents')
    
    if not contents_path.exists():
        thread_safe_print("⚠️  找不到contents目录")
        return l
    
    for item in contents_path.rglob('*'):
        if item.is_dir():
            input_tex_path = item.joinpath('main.tex')
            if input_tex_path.is_file():
                try:
                    with open(input_tex_path, "r", encoding='utf-8') as f:
                        first_line = f.readline()
                        title = first_line.replace('%', '').strip()
                        if title:
                            l.append({
                                'name': title,
                                'entry': str(item.relative_to(current_dir))
                            })
                            thread_safe_print(f"📁 找到项目: {title}")
                except Exception as e:
                    thread_safe_print(f"⚠️  读取{input_tex_path}失败: {str(e)}")
    
    thread_safe_print(f"📊 共找到 {len(l)} 个项目")
    return l

def main():
    """主函数"""
    # 自动检测CPU核心数
    cpu_count = get_cpu_count()
    thread_safe_print(f"🔍 检测到CPU核心数: {cpu_count}")
    
    # 智能计算并发数
    max_projects, max_tasks_per_project = calculate_concurrency(cpu_count)
    
    thread_safe_print(f"⚙️  并发配置:")
    thread_safe_print(f"  • CPU核心数: {cpu_count}")
    thread_safe_print(f"  • 项目并发数: {max_projects}")
    thread_safe_print(f"  • 任务并发数: {max_tasks_per_project}")
    thread_safe_print(f"  • 子项目模式: {is_sub}")
    thread_safe_print(f"  • 计算机模式: {is_c}")

    
    if not is_sub:
        thread_safe_print("当前为非子项目模式，退出")
        return
    
    projects = get_list()
    
    if not projects:
        thread_safe_print("❌ 未找到任何项目，退出")
        return
    
    thread_safe_print(f"🚀 开始并发编译 {len(projects)} 个项目...")
    overall_start_time = time.time()
    
    # 动态调整并发数：如果项目很少，减少并发数
    if len(projects) < max_projects:
        actual_concurrency = min(len(projects), max_projects)
        thread_safe_print(f"📉 项目数较少({len(projects)})，将并发数调整为: {actual_concurrency}")
        max_projects = actual_concurrency
    
    with ThreadPoolExecutor(max_workers=max_projects) as project_executor:
        futures = []
        
        for i, project in enumerate(projects):
            future = project_executor.submit(
                compile_sub_project, 
                project, 
                i, 
                max_tasks_per_project
            )
            futures.append(future)
        
        results = []
        successful_projects = []
        failed_projects = []
        
        for i, future in enumerate(as_completed(futures)):
            try:
                all_success, task_id, project_name = future.result()
                if all_success:
                    thread_safe_print(f"🎉 项目 {project_name} 全部编译成功！")
                    successful_projects.append(project_name)
                else:
                    thread_safe_print(f"⚠️  项目 {project_name} 部分或全部编译失败")
                    failed_projects.append(project_name)
                results.append((all_success, project_name))
            except Exception as e:
                thread_safe_print(f"💥 项目{i}执行异常: {str(e)}")
                failed_projects.append(f"项目{i}")
    
    # 输出统计信息
    overall_elapsed = time.time() - overall_start_time
    thread_safe_print("\n" + "="*60)
    thread_safe_print("📊 编译完成统计")
    thread_safe_print("="*60)
    thread_safe_print(f"总耗时: {overall_elapsed:.1f}秒")
    thread_safe_print(f"总项目数: {len(projects)}")
    thread_safe_print(f"✅ 成功项目: {len(successful_projects)}")
    
    if successful_projects:
        thread_safe_print("  成功列表:")
        for proj in successful_projects:
            thread_safe_print(f"    • {proj}")
    
    thread_safe_print(f"❌ 失败项目: {len(failed_projects)}")
    if failed_projects:
        thread_safe_print("  失败列表:")
        for proj in failed_projects:
            thread_safe_print(f"    • {proj}")
    
    thread_safe_print("="*60)
    
    # 性能分析
    if len(successful_projects) > 0:
        sequential_estimate = overall_elapsed * max_projects
        speedup = sequential_estimate / overall_elapsed if overall_elapsed > 0 else 0
        thread_safe_print(f"🚀 并发加速比: 约{speedup:.1f}x")
    
    if len(failed_projects) == 0:
        thread_safe_print("🎊 所有项目编译成功！")
    else:
        thread_safe_print(f"⚠️  有 {len(failed_projects)} 个项目编译失败")
        sys.exit(1)

if __name__ == "__main__":
    main()