# 词法分析器
from __future__ import annotations  # 为兼容低版本python（不支持函数类别定义），导入__future__模块

from colorama import Fore, Style  # 导入可视化相关的库(用于改变输出字体的颜色)


# 定义Token类
class Token:
    """定义Token类：包含三个信息，词法的类型，词法类型对应的颜色，词法错误的提示"""
    type_to_name = {
        'whitespace': '空白符',
        'command': '预处理命令',
        'string': '字符串',
        'char': '字符',
        'identifier': '标识符',
        'keyword': '关键字',
        'int_dec': '十进制整数',
        'int_oct': '八进制整数',
        'int_bin': '二进制整数',
        'int_hex': '十六进制整数',
        'float': '浮点数',
        'operator': '运算符',
        'comment': '注释',
        'error': '错误',
    }
    type_to_color = {
        'whitespace': Fore.WHITE,  # 白色
        'command': Fore.CYAN,  # 青色
        'string': Fore.GREEN,  # 绿色
        'char': Fore.GREEN,  # 绿色
        'identifier': Style.RESET_ALL,  # 默认色
        'keyword': '\033[38;2;255;140;0m',  # 橘色
        'int_dec': Fore.BLUE,  # 蓝色
        'int_oct': Fore.BLUE,  # 蓝色
        'int_bin': Fore.BLUE,  # 蓝色
        'int_hex': Fore.BLUE,  # 蓝色
        'float': Fore.BLUE,  # 蓝色
        'operator': Fore.MAGENTA,  # 紫色
        'comment': Fore.LIGHTBLACK_EX,  # 灰色
        'error': Fore.RED,  # 红色
    }

    def __init__(self, _type, value, hint=""):
        self.type = _type
        self.value = value
        self.hint = hint

    def __str__(self):
        if self.type == 'whitespace':
            return f""
        if self.hint:
            return f"<{self.type}, {self.value}, {self.hint}>\n"
        else:
            return f"<{self.type}, {self.value}>\n"


# 定义字符集(借鉴正则表达式的字符集)
class SignSet:
    """定义SignSet字符集：借鉴正则表达式的字符集表示方法，定义了\s\w\d等字符集"""

    # \d类
    sign_set_d = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    # \w类
    sign_set_w = {
                     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                     'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                     'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                     'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                     '_'
                 } | sign_set_d
    # \s类
    sign_set_s = {' ', '\t', '\n'}
    # \W类(键盘顺序)
    sign_set_W = ({'`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+',
                   '[', ']', '{', '}', '\\', '|', ';', ':', "'", '"', ',', '<', '.', '>', '/', '?'}
                  | sign_set_s) \
                 - {'`', '@', '$', }  # FIXME 有些符号C语言没有，故删除
    # .类
    sign_set_dot = (sign_set_w | sign_set_W) - {'\n'}
    sign_set_all = sign_set_dot | {'\n'}
    # 关键字
    keyword_set = [
        'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern',
        'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
        'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while']


# 定义循环匹配函数（适用于DFA无法解决的情况(比如需要判断是否行首)
def loop_match(_j, sign_set, _code) -> int:
    """循环匹配字符串，让j停在最后一个匹配的字符上，或者遇到整个字符串结尾"""
    while _j < len(_code) and _code[_j] in sign_set:
        _j += 1
    _j -= 1
    return _j


# 定义DFA类，以及内部的符号集解析函数、自动匹配函数
class DFA:
    """DFA确定有限自动机类"""

    def __init__(self, *, edges: list, start: int, end: dict):
        """输入 边(起点, 转移条件, 终点)、初态(状态编号)和终态(状态编号, 类型信息)，转为内部的数据结构(邻接表)"""
        assert isinstance(edges, list)
        for i in range(len(edges)):
            edge = edges[i]
            assert isinstance(edge, tuple)
            assert len(edge) == 3
            edge = list(edge)
            assert isinstance(edge[0], int)
            assert isinstance(edge[1], set) or isinstance(edge[1], str)
            if isinstance(edge[1], set):
                for char in edge[1]:
                    assert isinstance(char, str)
            elif isinstance(edge[1], str):
                edge[1] = self.parse_single_regexp(edge[1])
            assert isinstance(edge[1], set)
            assert isinstance(edge[2], int)
            edges[i] = tuple(edge)
        self.start = start
        self.end = end
        self.graph = {}
        for edge in edges:
            if edge[0] not in self.graph:
                self.graph[edge[0]] = {}
            for char in edge[1]:
                self.graph[edge[0]][char] = edge[2]

    # 解析单元素正则表达式(即解析字符集)
    @staticmethod
    def parse_single_regexp(s: str) -> set:
        """解析单元素正则表达式，返回字符集"""
        if s[0] == '[' and s[-1] == ']':
            s = s[1:-1]
        else:
            assert len(s) == 1 or (s[0] == '\\' and len(s) == 2)
        sign_set = []
        i, j = -1, -1
        exclusion_model = False
        if s[0] == '^':
            exclusion_model = True
            s = s[1:]
        while j < len(s) - 1:
            j += 1
            i = j
            if s[j] == '\\':
                assert j < len(s) - 1
                j += 1
                if s[j] == 'd':
                    sign_set += SignSet.sign_set_d
                    continue
                if s[j] == 'w':
                    sign_set += SignSet.sign_set_w
                    continue
                if s[j] == 's':
                    sign_set += SignSet.sign_set_s
                    continue
                if s[j] == 'W':
                    sign_set += SignSet.sign_set_W
                    continue
                if s[j] == 'n':
                    sign_set.append('\n')
                    continue
                if s[j] == 't':
                    sign_set.append('\t')
                    continue
                if s[j] in SignSet.sign_set_W - SignSet.sign_set_s:
                    sign_set.append(s[j])
                    continue
                raise Exception(f'unknown escape character: {s[j]}')
            if s[j] == '.':
                sign_set += SignSet.sign_set_dot
                continue
            if s[j] in SignSet.sign_set_w:
                if j < len(s) - 1 and s[j + 1] == '-':
                    assert j < len(s) - 2
                    assert s[j + 2] in SignSet.sign_set_w
                    # ascii码顺序
                    sign_set += [chr(i) for i in range(ord(s[j]), ord(s[j + 2]) + 1)]
                    j += 2
                else:
                    sign_set.append(s[j])
                continue
            raise Exception(f'unknown character: {s[j]}')
        if exclusion_model:
            return SignSet.sign_set_all - set(sign_set)
        else:
            return set(sign_set)

    # 自动匹配函数
    def match(self, _code: str, _i: int, _j: int) -> (Token, int):
        """匹配字符串，返回Token实例和最后一个匹配的字符的下标"""
        state = self.start
        # _j表示需要判断的字符的下标
        while _j < len(_code) and state in self.graph:  # 没有后节点就停止（表示进入下一个token识别）
            # 判断是否有下一步
            if _code[_j] not in self.graph[state]:  # 通过char不能找到后继节点，停止
                break
            else:
                state = self.graph[state][_code[_j]]  # 状态走一步
                _j += 1  # 指针后移，判断下一个字符
        _j -= 1
        if state in self.end:
            return Token(
                self.end[state].split('@')[0],
                _code[_i:_j + 1],
                self.end[state].split('@')[1] if '@' in self.end[state] else ''
            ), _j
        raise Exception('匹配失败')  # FIXME 之后可以改成警告


# 定义词法分析函数
def parse(code: str) -> list:
    """定义词法分析函数parse()：在该函数内进行词法分析，先根据词素的大类进行分支语句，然后实例化对应类别的DFA，然后用DFA类内部的匹配函数匹配(或直接用循环匹配函数匹配)"""
    token_list = []
    # i为token的起始位置, j为token的结束位置（token=code[i:j+1]）
    line_head = True  # 用于判断是否是行首（不考虑空白符）
    i, j = -1, -1

    while j < len(code) - 1:
        i = j + 1
        j = i
        # whitespace
        if code[j] in SignSet.sign_set_s:
            j = loop_match(j, SignSet.sign_set_s, code)
            if '\n' in code[i:j + 1]:
                line_head = True
            token_list.append(Token('whitespace', code[i:j + 1]))
            continue
        # command
        if code[j] == '#':
            j = loop_match(j, SignSet.sign_set_dot, code)
            if line_head:
                token_list.append(Token('command', code[i:j + 1]))
            else:
                token_list.append(Token('error', code[i:j + 1], 'command必须在行首'))
            line_head = False
            continue
        # string
        if code[j] == '"':
            j += 1
            fa = DFA(
                edges=[
                    (1, r'[^\"\\\n]', 1),
                    (1, r'\"', 2),
                    (1, r"\\", 3),
                    (3, r".", 1),
                ],
                start=1,
                end={
                    1: 'error@双引号不成对',
                    2: 'string',
                    3: 'error@转义符无内容'
                }
            )
            token, j = fa.match(code, i, j)
            token_list.append(token)
            line_head = False
            continue
        # char
        if code[j] == "'":
            j += 1
            fa = DFA(
                edges=[
                    (1, r"[^\'\\\n]", 2),
                    (1, r"\\", 3),
                    (3, r".", 2),
                    (2, r"\'", 4),
                ],
                start=1,
                end={
                    1: 'error@单引号不成对',
                    2: 'error@单引号不成对',
                    4: 'char',
                    3: 'error@转义符无内容'
                }
            )
            token, j = fa.match(code, i, j)
            token_list.append(token)
            line_head = False
            continue
        # identifier|keyword
        if code[j] in SignSet.sign_set_w - SignSet.sign_set_d:
            j += 1
            fa = DFA(
                edges=[
                    (1, SignSet.sign_set_w, 1),
                ],
                start=1,
                end={
                    1: 'identifier'
                }
            )
            token, j = fa.match(code, i, j)
            # 判断是否是关键字
            if token.value in SignSet.keyword_set:
                token.type = 'keyword'
            token_list.append(token)
            line_head = False
            continue
        # number
        if code[j] in SignSet.sign_set_d | {'.'}:
            fa = DFA(
                edges=[
                    (0, r'0', 1),
                    (0, r'[1-9]', 2),
                    (0, r'\.', 3),
                    (1, r'[0-7]', 4),
                    (1, r'[89]', 5),
                    (1, r'[bB]', 6),
                    (1, r'[xX]', 9),
                    (1, r'[ac-wyzAC-WYZ_]', 12),
                    (1, r'\.', 13),
                    (2, r'\d', 2),
                    (2, r'[a-df-zA-DF-Z_]', 12),
                    (2, r'[eE]', 14),
                    (2, r'\.', 13),
                    (3, r'\d', 13),
                    (4, r'[0-7]', 4),
                    (4, r'[89a-zA-Z_\.]', 5),
                    (5, r'[\w\.]', 5),
                    (6, r'[01]', 7),
                    (6, r'[2-9a-zA-Z_\.]', 8),
                    (7, r'[01]', 7),
                    (7, r'[2-9a-zA-Z_\.]', 8),
                    (8, r'[\w\.]', 8),
                    (9, r'[\da-fA-F]', 10),
                    (9, r'[g-zG-Z_\.]', 11),
                    (10, r'[\da-fA-F]', 10),
                    (10, r'[g-zG-Z_\.]', 11),
                    (11, r'[\w\.]', 11),
                    (12, r'\w', 12),
                    (13, r'\d', 13),
                    (13, r'[eE]', 14),
                    (13, r'[a-df-zA-DF-Z_\.]', 17),
                    (14, r'[a-zA-Z_\.]', 17),
                    (14, r'[\+\-]', 15),
                    (14, r'\d', 16),
                    (15, r'[A-Za-z_\.]', 17),
                    (15, r'\d', 16),
                    (16, r'\d', 16),
                    (16, r'[a-zA-Z_\.]', 17),
                    (17, r'[\w\.]', 17)
                ],
                start=0,
                end={
                    1: 'int_dec',
                    2: 'int_dec',
                    3: 'operator',
                    4: 'int_oct',
                    5: 'error@错误的八进制数',
                    6: 'error@缺少数值的二进制数',
                    7: 'int_bin',
                    8: 'error@错误的二进制数',
                    9: 'error@缺少数值的十六进制数',
                    10: 'int_hex',
                    11: 'error@错误的十六进制数',
                    12: 'error@数字开头的标识符',
                    13: 'float',
                    14: 'error@科学计数法缺少指数',
                    15: 'error@科学计数法缺少指数值',
                    16: 'float',
                    17: 'error@带有非法字符的小数'
                }
            )
            token, j = fa.match(code, i, j)
            token_list.append(token)
            line_head = False
            continue
        # operator
        if code[j] in SignSet.sign_set_W - {'.', '/'} - SignSet.sign_set_s:
            fa = DFA(
                edges=[
                    (0, r'[\?\:\,\;\(\)\[\]\{\}\~]', 9),
                    (0, r'\+', 1),
                    (0, r'\-', 2),
                    (0, r'[\*\%\!\^\=]', 3),
                    (0, r'\<', 4),
                    (0, r'\>', 5),
                    (0, r'\&', 7),
                    (0, r'\|', 8),
                    (0, r'\\', 10),
                    (1, r'[\+\=]', 9),
                    (2, r'[\-\=\>]', 9),
                    (3, r'\=', 9),
                    (4, r'\=', 9),
                    (4, r'\<', 6),
                    (5, r'\=', 9),
                    (5, r'\>', 6),
                    (6, r'\=', 9),
                    (7, r'[\&\=]', 9),
                    (8, r'[\|\=]', 9),
                ],
                start=0,
                end={
                    1: 'operator',
                    2: 'operator',
                    3: 'operator',
                    4: 'operator',
                    5: 'operator',
                    6: 'operator',
                    7: 'operator',
                    8: 'operator',
                    9: 'operator',
                    10: 'error@不在字符串中的转义字符',
                }
            )
            token, j = fa.match(code, i, j)
            token_list.append(token)
            line_head = False
            continue
        # comment
        if code[j] == '/':
            j += 1
            fa = DFA(
                edges=[
                    (1, r'\/', 2),
                    (1, r'\*', 3),
                    (2, r'.', 2),
                    (3, r'[^\*]', 3),
                    (3, r'\*', 4),
                    (4, r'[^\/]', 3),
                    (4, r'\/', 5),
                ],
                start=1,
                end={
                    1: 'operator',
                    2: 'comment',
                    3: 'error@未成对的/*',
                    4: 'error@未成对的/*',
                    5: 'comment'
                }
            )
            token, j = fa.match(code, i, j)
            token_list.append(token)
            line_head = False
            continue
        # error
        if code[j] in SignSet.sign_set_all:
            raise Exception(f'可能出现但未考虑到的字符: {code[j]}')
        else:
            token_list.append(Token('error', code[j], '不应出现的字符(如中文等)'))

    return token_list


# 定义符号表输出函数
def print_token_list(token_list, path=None):
    """根据对应词素类别来输出，内部隐式使用Token的__str__()函数，可以将whitespace类型转为空字符串(不输出)，error类型可以输出错误信息"""
    # for i in token_list:
    #     print(i, end='')
    # 输出到文件
    if path:
        with open(f"{path}.out", 'w', encoding='utf-8') as f:
            for i in token_list:
                f.write(str(i))
        with open(f"{path}.sym", 'w', encoding='utf-8') as f:
            # token_list去重
            token_list = set(list([(token.type, token.value, token.hint) for token in token_list]))
            # 去除空白符类
            token_list = [i for i in token_list if i[0] != 'whitespace']
            # 排序
            token_list.sort()
            # 输出符号表
            for i in token_list:
                f.write(f"{i[0].upper()}{'@' + i[2] if i[2] != '' else ''} {i[1]}\n")


# 定义可视化函数
def show_token_list(token_list):
    """根据词素类别来可视化，将不同类别输出为不同颜色的文本"""
    # 类型颜色对照表输出
    for _type in Token.type_to_name:
        if _type == "whitespace":
            continue
        print(Token.type_to_color[_type] + Token.type_to_name[_type] + Style.RESET_ALL, end=' ')
    print()
    print()
    # token_list按照类型输出（对应颜色）
    for token in token_list:
        print(Token.type_to_color[token.type] + str(token.value) + Style.RESET_ALL, end='')


def get_token(sample_filepath: str):
    """获取token列表的函数，输入为样例文件的路径，输出为token列表"""
    # 读取代码
    with open(f'{sample_filepath}', 'r', encoding='utf-8') as f:
        code = f.read()
    # 词法分析(函数循环匹配/DFA自动匹配)
    _tokens = parse(code)
    return _tokens
