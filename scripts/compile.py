from pathlib import Path
import subprocess
import sys

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

\title{26李林880题}
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


    current_dir = Path.cwd()
    filepath = current_dir.joinpath(entry, 'pad.tex')
    with open(filepath, "w") as f:
        f.write(template_tex)
    

    cmd = [
        'latexmk',
        '-xelatex',
        f'-jobname=${name}_pad',
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
    
def main():

    l = [
        {
            'name': '24合工大超越卷1',
            'entry': 'contents/24hegongdachaoyuejuan/juan1'
        },
        {
            'name': '24合工大超越卷2',
            'entry': 'contents/24hegongdachaoyuejuan/juan2'
        },
    ]

    for item in l:
        compile_pad(item['entry'], item['name'])

main()