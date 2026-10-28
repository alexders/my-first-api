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

if True:
   print("这是一个测试")

try:
    a = 10 / 0
except ZeroDivisionError:
    print("错误：不能除以0！")


# nonlocal 嵌套函数，修改外层函数变量
def outer():
    num = 10
    def inner():
        nonlocal num
        num = 20
    inner()
    print(num)
outer()

y = 100
def test_local():
    y = 200
    print("局部y：", y)
test_local()
print("全局y：", y)
print()

print("===== 9.3 初探类 =====")
class Dog:
    # 类变量：所有实例共享
    species = "狗"

    def __init__(self, name):
        # 实例变量：每个实例独立
        self.name = name

    def bark(self):
        print(self.name, "汪汪")

# 实例化
d1 = Dog("旺财")
d2 = Dog("大黄")
d1.bark()
d2.bark()
print(d1.name, d2.name)
print(Dog.species, d1.species)

# ===================== 9.4 补充知识点：__class__、动态添加属性 =====================
print("===== 9.4 补充说明 =====")
print(d1.__class__)

# //d1.age = 3  # 动态添加属性,编译器会提醒,但是不会运行失败
# print(d1.age)

# ===================== 9.5 继承、isinstance、issubclass、多重继承、MRO =====================
print("===== 9.5 继承 =====")
class Animal:
    def say(self):
        print("动物叫")

class Cat(Animal):
    def say(self):
        print("喵喵")

c = Cat()
c.say() # 重写方法

# 调用父类原始写法
class Cat2(Animal):
    def say(self):
        Animal.say(self)
        print("喵喵喵")
c2 = Cat2()
c2.say()

# 判断类型
print(isinstance(c, Cat))
print(isinstance(c, Animal))
print(issubclass(Cat, Animal))

# 多重继承
class A:
    def hello(self):
        print("A")
class B:
    def hello(self):
        print("B")
class C(A,B):
    pass
cc = C()
cc.hello() # 看MRO顺序，优先A
print(C.__mro__) # 打印MRO查找顺序
print()

print("===== 9.7 杂项 =====")
from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
p = Point(10,20)
print(p)

m = d1.bark
print(m.__self__)
print(m.__func__)
print()

class Count:
    def __init__(self, end):
        self.n = 0
        self.end = end
    def __iter__(self):
        return self
    def __next__(self):
        if self.n < self.end:
            val = self.n
            self.n += 1
            return val
        else:
            raise StopIteration

c = Count(3)
it = iter(c)
print(next(it)) # 0
print(next(it)) # 1
print(next(it)) # 2
# ===================== 9.9 生成器 yield =====================
print("===== 9.9 生成器 =====")
def gen(end):
    n = 0
    while n < end:
        yield n
        n += 1

g = gen(3)
print(next(g))
print(next(g))
print(next(g))

for x in gen(3):
    print("for循环：", x)
print()

# ===================== 9.10 生成器表达式 (expr for ...) =====================
print("===== 9.10 生成器表达式 =====")
lst_comp = [x*x for x in range(5)] # 列表推导，全部放内存
gen_comp = (x*x for x in range(5)) # 生成器表达式，惰性
print(lst_comp)
print(sum(x for x in range(10))) # 作为函数参数可以省略括号 0 1 2 3 4 5 6 7 8 9 

import glob
print(glob.glob("*.py")) # 当前目录下所有py文件


# 文件 demo.py
import sys
print(sys.argv)