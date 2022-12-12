import os, re, sys, traceback

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
    print("[" + str(index) + "/" + size + "] " + document_name, end="")
    index += 1
    try:
        global f_in, f_out
        document_path = os.path.join(input_path, document_name)
        document_write_path = os.path.join(output_path, document_name)
        # 从文件名中提取论文英文名作为标题，提取发表时间和作者作为标签
        result = re.match(r"([0-9]{4})_(.*)\[ ((?:.(?!\[))*) \].md", document_name)
        year = result[1].strip()
        title = result[2].strip()
        authors = result[3].strip().split(",")
        with open(document_path, "r") as f_in, open(document_write_path, "w") as f_out:
            # 提取标题
            content = f_in.read()
            title_one = re.match(r"^# (.*)$", content, flags=re.MULTILINE)[1].strip()
            # 分析二级标题
            title_two_iter = re.finditer(r"^## (.*)$", content, flags=re.MULTILINE)
            blocks = {}
            start_pos = None
            block_title = None
            for iter in title_two_iter:
                if start_pos is not None:
                    blocks[block_title] = [start_pos, iter.start()]
                start_pos = iter.end()
                block_title = iter.group(1)
            blocks[block_title] = [start_pos, None]
            # 提取摘要
            abstract_word = "摘要"
            abstract = (
                content[blocks[abstract_word][0] : blocks[abstract_word][1]]
                .strip()
                .replace("\n\n", "")
            )
            # 提取关键字，将其作为标签
            keywords_word = "关键字"
            keywords_flag = False
            if keywords_word in blocks:
                keywords_flag = True
                keywords = content[
                    blocks[keywords_word][0] : blocks[keywords_word][1]
                ].strip()
            else:
                keywords = []
            # 写入新文件
            f_out.write(
                "---\ntitle: >\n\t"
                + title
                + "\ndescription: >\n\t"
                + abstract
                + "\ncategories: 论文翻译"
                + "\ntags:"
                + "\n- "
                + year
            )
            for author in authors:
                f_out.write("\n- Author_" + author)
            for keyword in keywords:
                f_out.write("\n- " + keyword)
            f_out.write("\n---\n")
            f_out.write("## 摘要\n" + content[blocks[abstract_word][0] : None].strip())
            print(" Succeed")
    except Exception as e:
        print(" Failed")
        traceback.print_exc()
print("Conversion completed")
