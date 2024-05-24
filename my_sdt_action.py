# 记录id
import builtins


class Top:
    def __init__(self):
        self.id_dict = {}

    def get_addr(self, lexeme) -> str:
        """
        获取id的地址
        :param lexeme: id的名字lexeme
        :return: id的地址addr
        """
        if self.id_dict.get(lexeme) is None:
            _error_list.append('Error: use of undeclared id ' + lexeme)
            # 错误处理：未声明的id，默认声明一个类型为int的id
            self.put(lexeme, Symbol.Type.Type_('int'))
            return lexeme
        return self.id_dict.get(lexeme)[0]

    def get_type(self, lexeme) -> "Symbol.Type.Type_":
        """
        获取id的类型
        :param lexeme: id的名字lexeme
        :return: id的类型type
        """
        if self.id_dict.get(lexeme) is None:
            _error_list.append('Error: use of undeclared id ' + lexeme)
            # 错误处理：未声明的id，默认声明一个类型为int的id
            self.put(lexeme, Symbol.Type.Type_('int'))
            return Symbol.Type.Type_('int')
        return self.id_dict.get(lexeme)[1]

    def put(self, lexeme, type):
        if self.id_dict.get(lexeme) is not None:
            _error_list.append('Error: ' + lexeme + ' has been redefined')
            # 错误处理：重复声明的id，不再重复声明
            pass
        self.id_dict[lexeme] = (lexeme, type)


class Symbol:
    class _symbol:
        def __init__(self):
            pass

    class Program(_symbol):
        pass

    class Decls(_symbol):
        pass

    class Decl(Decls):
        pass

    class Stmts(_symbol):
        def __init__(self, nextlist: list[builtins.int] | None = None, breaklist: list[builtins.int] | None = None,
                     continuelist: list[builtins.int] | None = None):
            super().__init__()
            self.nextlist = nextlist
            self.breaklist = breaklist
            self.continuelist = continuelist

    class Stmt(Stmts):
        pass

    class Stmt_Open(Stmt):
        pass

    class Block(Stmt):
        pass

    class Stmt_Closed(Stmt):
        pass

    class M(_symbol):
        def __init__(self, instr: builtins.int | None = None):
            super().__init__()
            self.instr = instr

    class N(_symbol):
        def __init__(self, nextlist: list[builtins.int] | None = None):
            super().__init__()
            self.nextlist = nextlist

    class Bool(_symbol):
        def __init__(self, truelist: list[builtins.int] | None = None, falselist: list[builtins.int] | None = None):
            super().__init__()
            self.truelist = truelist
            self.falselist = falselist

    class Bool_Join(Bool):
        pass

    class Bool_Unary(Bool):
        pass

    class Rel(_symbol):
        def __init__(self, op: str | None = None):
            super().__init__()
            self.op = op

    class L(_symbol):
        pass

    class K(_symbol):
        pass

    class Expr(_symbol):
        def __init__(self, type: "Symbol.Type.Type_|None" = None, addr: str | None = None):
            super().__init__()
            self.type = type
            self.addr = addr

    class Expr_Assign(Expr):
        pass

    class Expr_Arith(Expr):
        pass

    class Expr_Term(Expr):
        pass

    class Expr_Unary(Expr):
        pass

    class Loc(_symbol):
        def __init__(self, array_addr: str | None = None, type: "Symbol.Type.Type_|None" = None,
                     offset_addr: str | None = None):
            super().__init__()
            assert isinstance(array_addr, str) or array_addr is None
            assert isinstance(type, Symbol.Type.Type_) or type is None
            assert isinstance(offset_addr, str) or offset_addr is None
            self.array_addr = array_addr
            self.type = type
            self.offset_addr = offset_addr

    class Type(_symbol):
        class Type_:
            def __init__(self, type: str, elem_type: "Symbol.Type.Type_|None" = None,
                         width: builtins.int | None = None):
                """
                Type.type，保存实际类型，元素类型(如果是数组），元素宽度
                :param type: 类型的字符串：int/long/float/double/array
                :param elem_type: 子元素的类型
                :param width: 类型的宽度，下标访问时使用（按字节移动下标）
                """
                self.type = type
                self.elem_type = elem_type
                self.width = width

            def __eq__(self, other):
                if other is None:
                    return False
                if self.type in ["int", "long", "float", "double"]:
                    return self.type == other
                else:  # self.type==array
                    return self.type == other.type and self.elem_type == other.elem_type

            def __str__(self):
                return self.type

        class Array_(Type_):
            def __init__(self, _num: builtins.int, elem_type: "Symbol.Type.Type_|None",
                         width: builtins.int | None = None):
                super().__init__("array", elem_type, width)
                self._num = _num

            def __eq__(self, other):
                if other is None:
                    return False
                return self.type == other.type and self.elem_type == other.elem_type and self._num == other._num

        def __init__(self, type: Type_ | None = None, width: builtins.int | None = None):
            super().__init__()
            self.type = type
            self.width = width

    class Basic(_symbol):
        def __init__(self, type: "Symbol.Type.Type_|None" = None, width: builtins.int | None = None):
            super().__init__()
            self.type = type
            self.width = width

    class num(_symbol):
        def __init__(self, lexval, lextype: "Symbol.Type.Type_|None" = None):
            super().__init__()
            self.lexval = lexval
            self.lextype = lextype

    class id(_symbol):
        def __init__(self, lexeme):
            super().__init__()
            self.lexeme = lexeme


# 记录最终的三元式
_result_code = []
# 记录下一个指令的位置
nextinstr = 0
# 记录变量
_temp_var_list = {
    'int': [],
    'long': [],
    'float': [],
    'double': [],
}
# 记录id
top = Top()
# 记录错误
_error_list = []


def backpatch(lst, instr):
    for i in lst:
        assert "goto" in _result_code[i]
        # 将goto以及后面的全部内容替换为goto instr
        _result_code[i] = _result_code[i].split("goto")[0] + "goto " + str(instr)


def merge(lst1, lst2) -> list[builtins.int]:
    return lst1 + lst2


def makelist(instr):
    return [instr]


def gen(*symbols):
    global nextinstr
    # 转为字符串
    symbols = [str(symbol) for symbol in symbols]
    instr = ' '.join(symbols)
    _result_code.append(instr)
    nextinstr += 1
    return nextinstr - 1


def newTemp(type: str | Symbol.Type.Type_) -> str:
    """
    生成临时变量，返回临时变量的addr
    :param type: 临时变量的类型
    :return: 临时变量的addr
    """
    if isinstance(type, str):
        _temp_var_list[type].append(type[0] + str(len(_temp_var_list[type])))
        return _temp_var_list[type][-1]
    elif isinstance(type, Symbol.Type.Type_):
        _temp_var_list[type.type].append(type.type[0] + str(len(_temp_var_list[type.type])))
        return _temp_var_list[type.type][-1]
    else:
        raise TypeError('type must be str or Symbol.Type.Type_')



# Type.type = array(num.lexval, Type1.type)
def array(num: int, type: Symbol.Type.Type_) -> Symbol.Type.Array_:
    return Symbol.Type.Array_(num, type, num * type.width)


def error(msg):
    _error_list.append('Error: ' + msg)


def resultAccuracy(type1: Symbol.Type.Type_, type2: Symbol.Type.Type_) -> Symbol.Type.Type_:
    type_priority = {'double': 3, 'float': 2, 'long': 2, 'int': 1}
    if type1.type == 'array' or type2.type == 'array':
        error('array type cannot be operated')
        return Symbol.Type.Type_('double')
    if type_priority[type1.type] > type_priority[type2.type]:
        return type1
    elif type_priority[type1.type] < type_priority[type2.type]:
        return type2
    else:
        if type1.type == type2.type:
            return type1
        else:  # long float
            return Symbol.Type.Type_('double')


# FIXME test declare

int = Symbol.Type.Type_('int', width=4)
long = Symbol.Type.Type_('long', width=8)
float = Symbol.Type.Type_('float', width=8)
double = Symbol.Type.Type_('double', width=16)
#
# Block = Symbol.Block()
# Stmts = Symbol.Stmts()
# Stmt, Stmt1, Stmt2 = Symbol.Stmt(), Symbol.Stmt(), Symbol.Stmt()
# Stmt_Open, Stmt_Open1, Stmt_Open2 = Symbol.Stmt_Open(), Symbol.Stmt_Open(), Symbol.Stmt_Open()
# Stmt_Closed, Stmt_Closed1, Stmt_Closed2 = Symbol.Stmt_Closed(), Symbol.Stmt_Closed(), Symbol.Stmt_Closed()
# M, M1, M2, M3 = Symbol.M(), Symbol.M(), Symbol.M(), Symbol.M()
# N = Symbol.N()
# Bool, Bool1 = Symbol.Bool(), Symbol.Bool()
# Bool_Join, Bool_Join1 = Symbol.Bool_Join(), Symbol.Bool_Join()
# Bool_Unary, Bool_Unary1 = Symbol.Bool_Unary(), Symbol.Bool_Unary()
# Rel = Symbol.Rel()
# L = Symbol.L()
# K = Symbol.K()
# Expr, Expr1, Expr2 = Symbol.Expr(), Symbol.Expr(), Symbol.Expr()
# Expr_Assign, Expr_Assign1 = Symbol.Expr_Assign(), Symbol.Expr_Assign()
# Expr_Arith, Expr_Arith1 = Symbol.Expr_Arith(), Symbol.Expr_Arith()
# Expr_Term, Expr_Term1 = Symbol.Expr_Term(), Symbol.Expr_Term()
# Expr_Unary, Expr_Unary1 = Symbol.Expr_Unary(), Symbol.Expr_Unary()
# Loc, Loc1 = Symbol.Loc(), Symbol.Loc()
# Type, Type1 = Symbol.Type(), Symbol.Type()
# Basic = Symbol.Basic()
# num = Symbol.num(1, int)
# id = Symbol.id('x')
#
# # FIXME test begin
# pass
#
# backpatch(Block.nextlist, nextinstr)
# if not Block.breaklist: error('break statement not in loop')
# if not Block.continuelist: error('continue statement not in loop')
# gen('return')
#
# Block.nextlist = Stmts.nextlist
# Block.breaklist = Stmts.breaklist
# Block.continuelist = Stmts.continuelist
#
# pass
# pass
#
# top.put(id.lexeme, Type.type)
# id.type = Type.type
#
# Type.type = array(num.lexval, Type1.type)
# Type.width = num.lexval * Type1.width
#
# Type.type = Basic.type
# Type.width = Basic.width
#
# Basic.type = float
# Basic.width = 8
#
# Basic.type = int
# Basic.width = 4
#
# Basic.type = long
# Basic.width = 8
#
# Basic.type = double
# Basic.width = 16
#
# backpatch(Stmt1.nextlist, M.instr)
# Stmts.nextlist = Stmt.nextlist
# Stmts.breaklist = merge(Stmt1.breaklist, Stmt.breaklist)
# Stmts.continuelist = merge(Stmt1.continuelist, Stmt.continuelist)
#
# Stmts.nextlist = []
# Stmts.breaklist = []
# Stmts.continuelist = []
#
# Stmt.nextlist = Stmt_Open.nextlist
# Stmt.breaklist = Stmt_Open.breaklist
# Stmt.continuelist = Stmt_Open.continuelist
#
# Stmt.nextlist = Stmt_Closed.nextlist
# Stmt.breaklist = Stmt_Closed.breaklist
# Stmt.continuelist = Stmt_Closed.continuelist
#
# backpatch(Bool.truelist, M.instr)
# Stmt_Open.nextlist = merge(Bool.falselist, Stmt.nextlist)
# Stmt_Open.breaklist = Stmt.breaklist
# Stmt_Open.continuelist = Stmt.continuelist
#
# backpatch(Bool.truelist, M1.instr)
# backpatch(Stmt_Closed.nextlist, M2.instr)
# backpatch(Stmt_Closed.continuelist, M1.instr)
# Stmt_Open.nextlist = merge(Bool.falselist, Stmt_Closed.breaklist)
# Stmt_Open.breaklist = []
# Stmt_Open.continuelist = []
# gen('goto', M1.instr)
#
# backpatch(Stmt_Open.nextlist, M1.instr)
# backpatch(Bool.truelist, M2.instr)
# backpatch(Stmt_Open.continuelist, M1.instr)
# Stmt_Open.nextlist = merge(Bool.falselist, Stmt_Open.breaklist)
# Stmt_Open.breaklist = []
# Stmt_Open.continuelist = []
# gen('goto', M1.instr)
#
# backpatch(Bool.truelist, M3.instr)
# backpatch(N.nextlist, M1.instr)
# backpatch(Stmt_Open.nextlist, M2.instr)
# backpatch(Stmt_Open.continuelist, M2.instr)
# gen('goto', M2.instr)
# Stmt_Open.nextlist = merge(Bool.falselist, Stmt_Open.breaklist)
# Stmt_Open.breaklist = []
# Stmt_Open.continuelist = []
#
# backpatch(Bool.truelist, M1.instr)
# backpatch(Bool.falselist, M2.instr)
# temp = merge(Stmt_Closed1.nextlist, N.nextlist)
# Stmt_Closed.nextlist = merge(temp, Stmt_Closed2.nextlist)
# Stmt_Closed.breaklist = merge(Stmt_Closed1.breaklist, Stmt_Closed2.breaklist)
# Stmt_Closed.continuelist = merge(Stmt_Closed1.continuelist, Stmt_Closed2.continuelist)
#
# backpatch(Stmt_Closed1.nextlist, M1.instr)
# backpatch(Bool.truelist, M2.instr)
# backpatch(Stmt_Closed1.continuelist, M1.instr)
# Stmt_Closed.nextlist = merge(Bool.falselist, Stmt_Closed1.breaklist)
# Stmt_Closed.breaklist = []
# Stmt_Closed.continuelist = []
# gen('goto', M1.instr)
#
# backpatch(Bool.truelist, M1.instr)
# backpatch(Stmt.nextlist, M2.instr)
# backpatch(Stmt.continuelist, M1.instr)
# Stmt_Closed.nextlist = merge(Bool.falselist, Stmt.breaklist)
# Stmt_Closed.breaklist = []
# Stmt_Closed.continuelist = []
# gen('goto', M1.instr)
#
# backpatch(Bool.truelist, M3.instr)
# backpatch(N.nextlist, M1.instr)
# backpatch(Stmt_Closed1.nextlist, M2.instr)
# backpatch(Stmt_Closed1.continuelist, M2.instr)
# gen('goto', M2.instr)
# Stmt_Closed.nextlist = merge(Bool.falselist, Stmt_Closed1.breaklist)
# Stmt_Closed.breaklist = []
# Stmt_Closed.continuelist = []
#
# Stmt_Closed.nextlist = []
# Stmt_Closed.breaklist = makelist(nextinstr)
# Stmt_Closed.continuelist = []
# gen('goto_____')
#
# Stmt_Closed.nextlist = []
# Stmt_Closed.breaklist = []
# Stmt_Closed.continuelist = makelist(nextinstr)
# gen('goto_____')
#
# Stmt_Closed.nextlist = []
# Stmt_Closed.breaklist = []
# Stmt_Closed.continuelist = []
#
# Stmt_Closed.nextlist = Block.nextlist
# Stmt_Closed.breaklist = Block.breaklist
# Stmt_Closed.continuelist = Block.continuelist
#
# M.instr = nextinstr
#
# N.nextlist = makelist(nextinstr)
# gen('goto_____')
#
# backpatch(Bool1.falselist, L.instr)
# Bool.truelist = merge(Bool1.truelist, Bool_Join.truelist)
# Bool.falselist = Bool_Join.falselist
#
# Bool.truelist = Bool_Join.truelist
# Bool.falselist = Bool_Join.falselist
#
# backpatch(Bool_Join1.truelist, K.instr)
# Bool.truelist = Bool_Unary.truelist
# Bool.falselist = merge(Bool_Join1.falselist, Bool_Unary.falselist)
#
# Bool_Join.truelist = Bool_Unary.truelist
# Bool_Join.falselist = Bool_Unary.falselist
#
# Bool_Unary.truelist = makelist(nextinstr)
# gen('if', Expr1.addr, Rel.op, Expr2.addr, 'goto  ___')
# Bool_Unary.falselist = makelist(nextinstr)
# gen('goto _____')
#
# Bool_Unary.truelist = makelist(nextinstr)
# Bool_Unary.falselist = []
# gen('goto_____')
#
# Bool_Unary.falselist = makelist(nextinstr)
# Bool_Unary.truelist = []
# gen('goto_____')
#
# Bool_Unary.truelist = Bool_Unary1.falselist
# Bool_Unary.falselist = Bool_Unary1.truelist
#
# Bool_Unary.truelist = Bool.truelist
# Bool_Unary.falselist = Bool.falselist
#
# L.instr = nextinstr
#
# K.instr = nextinstr
#
# Rel.op = '<'
# Rel.op = '>'
# Rel.op = '=='
# Rel.op = '!='
# Rel.op = '<='
# Rel.op = '>='
#
# Expr.addr = Expr_Assign.addr
# Expr.type = Expr_Assign.type
#
# if Expr.type != Loc.type:
#     gen(Loc.array_addr, '[', Loc.offset_addr, ']', '=', Loc.type, Expr.addr)
# else:
#     gen(Loc.array_addr, '[', Loc.offset_addr, ']', '=', Expr.addr)
# Expr_Assign.addr = newTemp(Loc.type)
# Expr_Assign.type = Loc.type
# gen(Expr_Assign.addr, '=', Loc.array_addr, '[', Loc.offset_addr, ']')
#
# if Expr.type != id.type:
#     gen(top.get(id.lexeme), '=', id.type, Expr.addr)
# else:
#     gen(top.get(id.lexeme), '=', Expr.addr)
# Expr_Assign.addr = newTemp(id.type)
# Expr_Assign.type = id.type
# gen(Expr_Assign.addr, '=', top.get(id.lexeme))
#
# Expr_Assign.addr = Expr_Arith.addr
# Expr_Assign.type = Expr_Arith.type
#
# Expr_Arith.type = resultAccuracy(Expr_Arith.type, Expr_Term.type)
# Expr_Arith.addr = newTemp(Expr_Arith.type)
# operand1 = Expr_Arith.addr
# if Expr_Arith.type != Expr_Arith.type:
#     operand1 = newTemp(Expr_Arith.type)
# gen(operand1, '=', Expr_Arith.type, Expr_Arith.addr)
# operand2 = Expr_Term.addr
# if Expr_Term.type != Expr_Arith.type:
#     operand2 = newTemp(Expr_Arith.type)
# gen(operand2, '=', Expr_Arith.type, Expr_Term.addr)
# gen(Expr_Arith.addr, '=', operand1, '+', operand2)
#
# Expr_Arith.type = resultAccuracy(Expr_Arith.type, Expr_Term.type)
# Expr_Arith.addr = newTemp(Expr_Arith.type)
# operand1 = Expr_Arith.addr
# if Expr_Arith.type != Expr_Arith.type:
#     operand1 = newTemp(Expr_Arith.type)
# gen(operand1, '=', Expr_Arith.type, Expr_Arith.addr)
# operand2 = Expr_Term.addr
# if Expr_Term.type != Expr_Arith.type:
#     operand2 = newTemp(Expr_Arith.type)
# gen(operand2, '=', Expr_Arith.type, Expr_Term.addr)
# gen(Expr_Arith.addr, '=', operand1, '-', operand2)
#
# Expr_Arith.addr = Expr_Term.addr
# Expr_Arith.type = Expr_Term.type
#
# Expr_Term.type = resultAccuracy(Expr_Term.type, Expr_Unary.type)
# Expr_Term.addr = newTemp(Expr_Term.type)
# operand1 = Expr_Term.addr
# if Expr_Term.type != Expr_Term.type:
#     operand1 = newTemp(Expr_Term.type)
# gen(operand1, '=', Expr_Term.type, Expr_Term.addr)
# operand2 = Expr_Unary.addr
# if Expr_Unary.type != Expr_Term.type:
#     operand2 = newTemp(Expr_Term.type)
# gen(operand2, '=', Expr_Term.type, Expr_Unary.addr)
# gen(Expr_Term.addr, '=', operand1, '*', operand2)
#
# Expr_Term.type = resultAccuracy(Expr_Term.type, Expr_Unary.type)
# Expr_Term.addr = newTemp(Expr_Term.type)
# operand1 = Expr_Term.addr
# if Expr_Term.type != Expr_Term.type:
#     operand1 = newTemp(Expr_Term.type)
# gen(operand1, '=', Expr_Term.type, Expr_Term.addr)
# operand2 = Expr_Unary.addr
# if Expr_Unary.type != Expr_Term.type:
#     operand2 = newTemp(Expr_Term.type)
# gen(operand2, '=', Expr_Term.type, Expr_Unary.addr)
# gen(Expr_Term.addr, '=', operand1, '/', operand2)
#
# Expr_Term.addr = Expr_Unary.addr
# Expr_Term.type = Expr_Unary.type
#
# Expr_Unary.addr = newTemp(Expr_Unary.type)
# gen(Expr_Unary.addr, '=', '-', Expr_Unary.addr)
#
# Expr_Unary.addr = newTemp(Expr_Unary.type)
# gen(Expr_Unary.addr, '=', '+', Expr_Unary.addr)
#
# Expr_Unary.addr = newTemp(Basic.type)
# Expr_Unary.type = Basic.type
# gen(Expr_Unary.addr, '=', Basic.type, Expr_Unary.addr)
#
# Expr_Unary.addr = Expr.addr
# Expr_Unary.type = Expr.type
#
# Expr_Unary.addr = newTemp(Loc.type)
# gen(Expr_Unary.addr, '=', Loc.array_addr, '[', Loc.offset_addr, ']')
#
# Expr_Unary.addr = top.get(id.lexeme)
# Expr_Unary.type = id.type
#
# Expr_Unary.addr = num.lexval
# Expr_Unary.type = num.lextype
#
# Loc.array_addr = Loc1.array_addr
# Loc.type = Loc1.type.elem_type
# t = newTemp(int)
# Loc.offset_addr = newTemp(int)
# gen(t, '=', Expr.addr, '*', Loc.type.width)
# gen(Loc.offset_addr, '=', Loc.offset_addr, '+', t)
#
# Loc.array_addr = top.get(id.lexeme)
# Loc.type = id.type.elem_type
# Loc.offset_addr = newTemp(int)
# gen(Loc.offset_addr, '=', Expr.addr, '*', Loc.type.width)
