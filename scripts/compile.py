from pathlib import Path
import subprocess
import sys
import argparse

def compile_pad(entry, name):


    template_tex = r'''\documentclass[oneside]{book}

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

\setstretch{1.5}

\everymath{\displaystyle}

\pagestyle{fancy}
\fancyhf{}  % 清除所有页眉页脚
\renewcommand{\headrulewidth}{0pt}  % 去掉页眉横线
\fancyhead[R]{\rightmark}   % 页眉居右显示章和节
\fancyfoot[C]{\thepage}

\newcommand{\pp}{(\quad)}
\newcommand{\blankline}{\rule[-1pt]{1.5cm}{0.4pt}}

\let\oldvfill\vfill  % 保存原来的\vfill命令
\renewcommand{\vfill}{\newpage}

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
    out_tex = template_tex.replace("{title}", name)

    current_dir = Path.cwd()
    filepath = current_dir.joinpath(entry, 'pad.tex')
    with open(filepath, "w") as f:
        f.write(out_tex)
    
    print(str(filepath))
    cmd = [
        'latexmk',
        '-xelatex',
        f'-jobname={name}_pad',
        '-cd',
        str(filepath)
    ]
    result = subprocess.run(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    if result.returncode == 0:
        print("✅ 编译成功！")
        return True
    else:
        print("❌ 编译失败:")
        return False

def compile_exam(entry, name):

    template = r'''\let\stop\empty
\documentclass{exam-zh}

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

    current_dir = Path.cwd()
    input_path = current_dir.joinpath(entry, 'main.tex')
    output_path = current_dir.joinpath(entry, 'exam.tex')
    with open(input_path, "r") as f:
        input_tex = f.read().replace(r'\newpage', '').replace(r'\vfill', '')

        out_tex = template.replace('{title}', name).replace('{content}', input_tex)
        with open(output_path, "w") as f_out:
            f_out.write(out_tex)
    
        
    cmd = [
        'latexmk',
        '-xelatex',
        f'-jobname={name}_exam',
        '-cd',
        str(output_path)
    ]
    result = subprocess.run(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    if result.returncode == 0:
        print("✅ 编译成功！")
        return True
    else:
        print("❌ 编译失败:")
        return False

def get_list():
    l = []
    current_dir = Path.cwd()
    contents_path = current_dir.joinpath('contents')
    for item in contents_path.rglob('*'):
        if item.is_dir():
            
            input_tex_path = item.joinpath('main.tex')
            if input_tex_path.is_file():
                with open(input_tex_path, "r") as f:
                    first_line = f.readline()
                    title = first_line.replace('%', '').strip()
                    l.append({
                        'name': title,
                        'entry': str(item.relative_to(current_dir))
                    })

    return l

def main():

    l = get_list()
    parser = argparse.ArgumentParser(description='Compile LaTeX projects')
    parser.add_argument('--sub', type=str, default='false', 
                       help='Whether this is a sub project (true/false)')
    
    args = parser.parse_args()
    
    # 将字符串转换为布尔值
    is_sub = args.sub.lower() == 'true'
    
    print(f"Is sub project: {is_sub}")
    
    if is_sub:

        for item in l:
            current_dir = Path.cwd()
            input_path = current_dir.joinpath(item['entry'])
            if input_path.is_dir():
                compile_pad(item['entry'], item['name'])
                compile_exam(item['entry'], item['name'])

main()