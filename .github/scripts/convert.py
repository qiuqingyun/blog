import os, re, sys, traceback, subprocess

rootpath = os.getcwd()
input_path = os.path.join(rootpath, "Paper_translation")
output_path = os.path.join(rootpath, "source", "_posts", "translations")

# 创建输出文件夹
if not os.path.exists(output_path):
    os.makedirs(output_path)
# 读取文件列表
documents = []
if os.path.isdir(input_path):
    contents = os.listdir(input_path)
    for content in contents:
        content_path = os.path.join(input_path, content)
        if os.path.isfile(content_path):
            filename, suffix = os.path.splitext(content)
            if suffix == ".md":
                documents.append(content)

# 处理文件
index = 1
size = str(len(documents))
for document_name in documents:
    document_path = os.path.join(input_path, document_name)
    document_write_path = os.path.join(output_path, document_name)
    print(f"[{str(index)}/{size}] {document_name}")
    index += 1
    try:
        global f_in, f_out
        # 从文件名中提取论文英文名作为标题，提取发表时间和作者作为标签
        result = re.match(r"([0-9]{4})_(.*)\[ ((?:.(?!\[))*) \].md", document_name)
        year = result[1].strip()
        title = result[2].strip()
        authors = result[3].strip().split(",")
        # 从git中提取文章创建时间和最后一次更新时间
        # 创建时间
        date_str = subprocess.getoutput(
            rf'git  -C "{input_path}" log --diff-filter=A --follow --format="%as" -1 -- "{document_path}"'
        ).strip()
        # 最后一次更新时间
        updated_str = subprocess.getoutput(
            rf'git  -C "{input_path}" log -1 --format="%as" -- "{document_path}"'
        ).strip()
        print(f"date   : {date_str}\nupdated: {updated_str}")

        with open(document_path, "r") as f_in, open(document_write_path, "w") as f_out:
            # 提取标题
            content = f_in.read()
            title_one = re.match(r"^# (.*)$", content, flags=re.MULTILINE)[1].strip()
            # 分析二级标题
            title_two_iter = re.finditer(r"^## (.*)$", content, flags=re.MULTILINE)
            blocks = {}
            block_titles = []
            start_pos = None
            block_title = None
            for iter in title_two_iter:
                if start_pos is not None:
                    blocks[block_title] = [start_pos, iter.start()]
                    block_titles.append(block_title)
                start_pos = iter.end()
                block_title = iter.group(1)
            blocks[block_title] = [start_pos, None]
            block_titles.append(block_title)
            # 提取摘要
            abstract_word = block_titles[0]
            abstract = (
                content[blocks[abstract_word][0] : blocks[abstract_word][1]]
                .strip()
                .replace("\n\n", "")
            )
            # 提取关键字，将其作为标签
            keywords_word = "关键字"
            if keywords_word in blocks:
                keywords = content[
                    blocks[keywords_word][0] : blocks[keywords_word][1]
                ].strip()
            else:
                keywords = []

            # 写入新文件

            # 写入Front-matter
            f_out.write(
                f"---\n"
                f"title: >\n"
                f"\t{title}\n"
                f"date: {date_str}\n"
                f"updated: {updated_str}\n"
                f"categories: 论文翻译\n"
                f"tags: \n"
                f"- {year}\n"
            )
            for author in authors:
                f_out.write(f"- 作者_{author}\n")
            for keyword in keywords:
                f_out.write(f"- {keyword}\n")
            f_out.write(f"---\n\n")
            # 写入中文名与摘要
            f_out.write(
                f"## {title_one}\n\n"
                f"{content[blocks[abstract_word][0] : blocks[abstract_word][1]].strip()}\n\n"
                f"<!--more-->\n\n"
            )
            # 写入正文
            if len(block_titles) > 1:
                f_out.write(
                    f"## {block_titles[1]}\n\n"
                    f"{content[blocks[block_titles[1]][0] : None].strip()}"
                )
            print("Succeed\n")
    except Exception as e:
        print("Failed\n")
        traceback.print_exc()
        os.remove(document_write_path)
print("Conversion completed")
