import os
import re

path = os.getcwd() + "/"
input_path = path + "Paper_translation/"
output_path = path + "source/_posts/translations/"
# 创建输出文件夹
if not os.path.exists(output_path):
    os.makedirs(output_path)
# 读取文件列表
files = []
if os.path.isdir(input_path):
    files_list = os.listdir(input_path)
    for file in files_list:
        if not os.path.isdir(file):
            filename, suffix = os.path.splitext(file)
            if suffix == ".md":
                files.append(file)
# 处理文件
index = 1
size = len(files)
for file in files:
    print("[" + str(index) + "/" + str(size) + "] " + file, end="")
    index += 1
    try:
        global f_in, f_out
        file_path = input_path + file
        file_new_path = output_path + file
        with open(file_path, "r") as f_in, open(file_new_path, "w") as f_out:
            # 提取标题
            content = f_in.read()
            title = re.sub(
                r"# ", "", re.findall(r"^# .*$", content, flags=re.MULTILINE)[0]
            ).strip()
            # 提取描述
            tags = re.findall(r"^## .*$", content, flags=re.MULTILINE)
            description = re.findall(
                r"" + tags[0] + ".*" + tags[1], content, flags=re.DOTALL
            )[0]
            description = re.sub(
                r"\n\n",
                "",
                re.sub(
                    r"" + tags[1],
                    "",
                    re.sub(r"" + tags[0], "", description).strip(),
                ).strip(),
            )
            if len(description) > 300:
                description = description[0:300] + "…"
            # 写入新文件
            f_out.write(
                "---\ntitle: "
                + title
                + "\ndescription: "
                + description
                + "\n---\n"
                + content
            )
            print(" Succeed")
    except:
        print(" Failed")
print("Conversion completed")
