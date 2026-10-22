import math
import json

print("="*60)
print("【一、格式化输出：f-string（推荐）】")
print("=" * 60)
name = "xx"
score = 92.3456
# 基础用法
print(f"姓名：{name}，分数：{score:.3f}")
# 进阶用法
print(f"分数：{score=}")
# 宽度对齐
print(f"|{name:10}|{score:10.2f}|")
print(f"|{score:<10.2f}|") # 左对齐
print(f"|{score:>10.2f}|") # 右对齐（默认）
print(f"|{score:^10.2f}|") # 居中


#str和repr的区别
s = "hello\nworld"
print("\nstr() 给人看：")
print(str(s))
print("\nrepr() 给解释器看，调试用：")
print(repr(s))

print("\n" + "=" * 60)
print("【二、str.format() 格式化】")
print("=" * 60)
print("{0} 的圆周率大概是 {1:.4f}".format("圆周率", math.pi))
print("{name} 今年 {age} 岁".format(name="小红", age=18))

# 对齐方法 rjust / ljust / center / zfill
num = "78"
print(num.rjust(6))   # 右对齐，左边补空格
print(num.ljust(6))   # 左对齐，右边补空格
print(num.center(6))  # 居中
print(num.zfill(6))   # 左边补0

print("\n" + "=" * 60)
print("【三、文件读写 with open （重点！自动关闭文件）】")
print("=" * 60)
# 1. 写入 'w' 模式，覆盖原有内容
with open("test_txt.txt", "w", encoding="utf-8") as f:
    f.write("第一行文字\n")
    f.write("第二行文字\n")
# 2. 追加 'a' 模式，在末尾加内容，不覆盖
with open("test_txt.txt", "a", encoding="utf-8") as f:
    f.write("这一行是追加进去的\n")

with open("test_txt.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

print("---- 逐行读取 for line in f ----")
with open("test_txt.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line, end="")

# 5. readline() 读一行
print("---- readline() 示例 ----")
with open("test_txt.txt", "r", encoding="utf-8") as f:
    line1 = f.readline()
    print(line1, end="")
# 6. readlines() 全部读到列表
with open("test_txt.txt", "r", encoding="utf-8") as f:
    line_list = f.readlines()
print("\nreadlines 返回列表：", line_list)

#json.dump 写入文件
print("\n" + "=" * 60)
print("【四、json 保存/读取字典、列表结构化数据】")
print("=" * 60)
data = {
    "name": "阿强",
    "hobby": ["看书", "打球"],
    "age": 22
}
with open("test_json.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)  # 写入json文件，indent=4表示缩进4个空格


with open("test_json.json", "r", encoding="utf-8") as f:
    data_loaded = json.load(f)  # 读取json文件4
print("读取的json数据：", data_loaded)
print("读取的json数据类型：", type(data_loaded))  # <class 'dict'>