class SDT_right(list):
    def __init__(self, rights: list[str], a: str):
        """
        定义一个产生式右部类
        :param rights: 产生式右部
        :param a: 语义动作，a是一个字符串，直接exec执行，注意命名空间
        """
        # 这里删掉序号防止报错
        super().__init__([right.replace("1", "").replace("2", "").replace("3", "") for right in rights])
        self.rights = rights
        self.a = a


sdt_grammar = {
    "S'": [
        SDT_right(
            ["Program"],
            # language=Python
            """
            pass
            """
        )
    ],
    "Program": [
        SDT_right(
            ["Basic", "id", "(", ")", "Block"],
            # language=Python
            """
            backpatch(Block.nextlist, nextinstr)
            if Block.breaklist: error('break statement not in loop')
            if Block.continuelist: error('continue statement not in loop')
            gen('return')
            """
        )
    ],
    "Block": [
        SDT_right(
            ["{", "Decls", "Stmts", "}"],
            # language=Python
            """
            Block.nextlist = Stmts.nextlist
            Block.breaklist = Stmts.breaklist
            Block.continuelist = Stmts.continuelist
            """
        )
    ],
    "Decls": [
        SDT_right(
            ["Decls1", "Decl"],
            # language=Python
            """
            pass
            """
        ),
        SDT_right(
            [],
            # language=Python
            """
            pass
            """
        )
    ],
    "Decl": [
        SDT_right(
            ["Type", "id", ";"],
            # language=Python
            """
            top.put(id.lexeme, Type.type)
            """
        )
    ],
    "Type": [
        SDT_right(
            ["Type1", "[", "num", "]"],
            # language=Python
            """
            Type.type = array(num.lexval, Type1.type)
            Type.width = num.lexval * Type1.width
            """
        ),
        SDT_right(
            ["Basic"],
            # language=Python
            """
            Type.type = Basic.type
            Type.width = Basic.width
            """
        )
    ],
    "Basic": [
        SDT_right(
            ["float"],
            # language=Python
            """
            Basic.type = float
            Basic.width = 8
            """
        ),
        SDT_right(
            ["int"],
            # language=Python
            """
            Basic.type = int
            Basic.width = 4
            """
        ),
        SDT_right(
            ["long"],
            # language=Python
            """
            Basic.type = long
            Basic.width = 8
            """
        ),
        SDT_right(
            ["double"],
            # language=Python
            """
            Basic.type = double
            Basic.width = 16
            """
        )
    ],
    "Stmts": [
        SDT_right(
            ["Stmts1", "M", "Stmt"],
            # language=Python
            """
            backpatch(Stmts1.nextlist, M.instr)
            Stmts.nextlist = Stmt.nextlist
            Stmts.breaklist = merge(Stmts1.breaklist, Stmt.breaklist)
            Stmts.continuelist = merge(Stmts1.continuelist, Stmt.continuelist)
            """
        ),
        SDT_right(
            [],
            # language=Python
            """
            Stmts.nextlist = []
            Stmts.breaklist = []
            Stmts.continuelist = []
            """
        )
    ],
    "Stmt": [
        SDT_right(
            ["Stmt_Open"],
            # language=Python
            """
            Stmt.nextlist = Stmt_Open.nextlist
            Stmt.breaklist = Stmt_Open.breaklist
            Stmt.continuelist = Stmt_Open.continuelist
            """
        ),
        SDT_right(
            ["Stmt_Closed"],
            # language=Python
            """
            Stmt.nextlist = Stmt_Closed.nextlist
            Stmt.breaklist = Stmt_Closed.breaklist
            Stmt.continuelist = Stmt_Closed.continuelist
            """
        )
    ],
    "Stmt_Open": [
        SDT_right(
            ["if", "(", "Bool", ")", "M", "Stmt1"],
            # language=Python
            """
            backpatch(Bool.truelist, M.instr)
            Stmt_Open.nextlist = merge(Bool.falselist, Stmt1.nextlist)
            Stmt_Open.breaklist = Stmt1.breaklist
            Stmt_Open.continuelist = Stmt1.continuelist
            """
        ),
        SDT_right(
            ["if", "(", "Bool", ")", "M1", "Stmt_Closed1", "N", "else", "M2", "Stmt_Open2"],
            # language=Python
            """
            backpatch(Bool.truelist, M1.instr)
            backpatch(Bool.falselist, M2.instr)
            temp = merge(Stmt_Closed1.nextlist, N.nextlist)
            Stmt_Open.nextlist = merge(temp, Stmt_Open2.nextlist)
            Stmt_Open.breaklist = merge(Stmt_Closed1.breaklist, Stmt_Open2.breaklist)
            Stmt_Open.continuelist = merge(Stmt_Closed1.continuelist, Stmt_Open2.continuelist)
            """
        ),
        SDT_right(
            ["while", "M1", "(", "Bool", ")", "M2", "Stmt_Open1"],
            # language=Python
            """
            backpatch(Stmt_Open1.nextlist, M1.instr)
            backpatch(Bool.truelist, M2.instr)
            backpatch(Stmt_Open1.continuelist, M1.instr)
            Stmt_Open.nextlist = merge(Bool.falselist, Stmt_Open1.breaklist)
            Stmt_Open.breaklist = []
            Stmt_Open.continuelist = []
            gen('goto', M1.instr)
            """
        ),
        SDT_right(
            ["for", "(", "Expr1", ";", "M1", "Bool", ";", "M2", "Expr2", "N", ")", "M3", "Stmt_Open3"],
            # language=Python
            """
            backpatch(Bool.truelist, M3.instr)
            backpatch(N.nextlist, M1.instr)
            backpatch(Stmt_Open3.nextlist, M2.instr)
            backpatch(Stmt_Open3.continuelist, M2.instr)
            gen('goto', M2.instr)
            Stmt_Open.nextlist = merge(Bool.falselist, Stmt_Open3.breaklist)
            Stmt_Open.breaklist = []
            Stmt_Open.continuelist = []
            """
        ),
    ],
    "Stmt_Closed": [
        SDT_right(
            ["if", "(", "Bool", ")", "M1", "Stmt_Closed1", "N", "else", "M2", "Stmt_Closed2"],
            # language=Python
            """
            backpatch(Bool.truelist, M1.instr)
            backpatch(Bool.falselist, M2.instr)
            temp = merge(Stmt_Closed1.nextlist, N.nextlist)
            Stmt_Closed.nextlist = merge(temp, Stmt_Closed2.nextlist)
            Stmt_Closed.breaklist = merge(Stmt_Closed1.breaklist, Stmt_Closed2.breaklist)
            Stmt_Closed.continuelist = merge(Stmt_Closed1.continuelist, Stmt_Closed2.continuelist)
            """
        ),
        SDT_right(
            ["while", "M1", "(", "Bool", ")", "M2", "Stmt_Closed1"],
            # language=Python
            """
            backpatch(Stmt_Closed1.nextlist, M1.instr)
            backpatch(Bool.truelist, M2.instr)
            backpatch(Stmt_Closed1.continuelist, M1.instr)
            Stmt_Closed.nextlist = merge(Bool.falselist, Stmt_Closed1.breaklist)
            Stmt_Closed.breaklist = []
            Stmt_Closed.continuelist = []
            gen('goto', M1.instr)
            """
        ),
        SDT_right(
            ["do", "M1", "Stmt1", "while", "M2", "(", "Bool", ")", ";"],
            # language=Python
            """
            backpatch(Bool.truelist, M1.instr)
            backpatch(Stmt1.nextlist, M2.instr)
            backpatch(Stmt1.continuelist, M1.instr)
            Stmt_Closed.nextlist = merge(Bool.falselist, Stmt1.breaklist)
            Stmt_Closed.breaklist = []
            Stmt_Closed.continuelist = []
            gen('goto', M1.instr)
            """
        ),
        SDT_right(
            ["for", "(", "Expr1", ";", "M1", "Bool", ";", "M2", "Expr2", "N", ")", "M3", "Stmt_Closed3"],
            # language=Python
            """
            backpatch(Bool.truelist, M3.instr)
            backpatch(N.nextlist, M1.instr)
            backpatch(Stmt_Closed3.nextlist, M2.instr)
            backpatch(Stmt_Closed3.continuelist, M2.instr)
            gen('goto', M2.instr)
            Stmt_Closed.nextlist = merge(Bool.falselist, Stmt_Closed3.breaklist)
            Stmt_Closed.breaklist = []
            Stmt_Closed.continuelist = []
            """
        ),
        SDT_right(
            ["break", ";"],
            # language=Python
            """
            Stmt_Closed.nextlist = []
            Stmt_Closed.breaklist = makelist(nextinstr)
            Stmt_Closed.continuelist = []
            gen('goto_____')
            """
        ),
        SDT_right(
            ["continue", ";"],
            # language=Python
            """
            Stmt_Closed.nextlist = []
            Stmt_Closed.breaklist = []
            Stmt_Closed.continuelist = makelist(nextinstr)
            gen('goto_____')
            """
        ),
        SDT_right(
            ["Expr", ";"],
            # language=Python
            """
            Stmt_Closed.nextlist = []
            Stmt_Closed.breaklist = []
            Stmt_Closed.continuelist = []
            """
        ),
        SDT_right(
            ["Block"],
            # language=Python
            """
            Stmt_Closed.nextlist = Block.nextlist
            Stmt_Closed.breaklist = Block.breaklist
            Stmt_Closed.continuelist = Block.continuelist
            """
        ),
    ],
    "M": [
        SDT_right(
            [],
            # language=Python
            """
            M.instr = nextinstr
            """
        )
    ],
    "N": [
        SDT_right(
            [],
            # language=Python
            """
            N.nextlist = makelist(nextinstr)
            gen('goto_____')
            """
        )
    ],
    "Bool": [
        SDT_right(
            ["Bool1", "||", "L", "Bool_Join2"],
            # language=Python
            """
            backpatch(Bool1.falselist, L.instr)
            Bool.truelist = merge(Bool1.truelist, Bool_Join2.truelist)
            Bool.falselist = Bool_Join2.falselist
            """
        ),
        SDT_right(
            ["Bool_Join1"],
            # language=Python
            """
            Bool.truelist = Bool_Join1.truelist
            Bool.falselist = Bool_Join1.falselist
            """
        )
    ],
    "Bool_Join": [
        SDT_right(
            ["Bool_Join1", "&&", "K", "Bool_Unary2"],
            # language=Python
            """
            backpatch(Bool_Join1.truelist, K.instr)
            Bool_Join.truelist = Bool_Unary2.truelist
            Bool_Join.falselist = merge(Bool_Join1.falselist, Bool_Unary2.falselist)
            """
        ),
        SDT_right(
            ["Bool_Unary1"],
            # language=Python
            """
            Bool_Join.truelist = Bool_Unary1.truelist
            Bool_Join.falselist = Bool_Unary1.falselist
            """
        )
    ],
    "Bool_Unary": [
        SDT_right(
            ["Expr1", "Rel", "Expr2"],
            # language=Python
            """
            Bool_Unary.truelist = makelist(nextinstr)
            Bool_Unary.falselist = makelist(nextinstr+1)
            gen('if', Expr1.addr, Rel.op, Expr2.addr, 'goto  ___')
            gen('goto _____')
            """
        ),
        SDT_right(
            ["true"],
            # language=Python
            """
            Bool_Unary.truelist = makelist(nextinstr)
            Bool_Unary.falselist = []
            gen('goto_____')
            """
        ),
        SDT_right(
            ["false"],
            # language=Python
            """
            Bool_Unary.falselist = makelist(nextinstr)
            Bool_Unary.truelist = []
            gen('goto_____')
            """
        ),
        SDT_right(
            ["!", "Bool_Unary1"],
            # language=Python
            """
            Bool_Unary.truelist = Bool_Unary1.falselist
            Bool_Unary.falselist = Bool_Unary1.truelist
            """
        ),
        SDT_right(
            ["(", "Bool", ")"],
            # language=Python
            """
            Bool_Unary.truelist = Bool.truelist
            Bool_Unary.falselist = Bool.falselist
            """
        )
    ],
    "L": [
        SDT_right(
            [],
            # language=Python
            """
            L.instr = nextinstr
            """
        )
    ],
    "K": [
        SDT_right(
            [],
            # language=Python
            """
            K.instr = nextinstr
            """
        )
    ],
    "Rel": [
        SDT_right(
            ["<"],
            # language=Python
            """
            Rel.op='<'
            """
        ),
        SDT_right(
            [">"],
            # language=Python
            """
            Rel.op='>'
            """
        ),
        SDT_right(
            ["=="],
            # language=Python
            """
            Rel.op='=='
            """
        ),
        SDT_right(
            ["!="],
            # language=Python
            """
            Rel.op='!='
            """
        ),
        SDT_right(
            ["<="],
            # language=Python
            """
            Rel.op='<='
            """
        ),
        SDT_right(
            [">="],
            # language=Python
            """
            Rel.op='>='
            """
        )
    ],
    "Expr": [
        SDT_right(
            ["Expr_Assign1"],
            # language=Python
            """
            Expr.addr = Expr_Assign1.addr
            Expr.type = Expr_Assign1.type
            """
        )
    ],
    "Expr_Assign": [
        SDT_right(
            ["Loc", "=", "Expr1"],
            # language=Python
            """
            if Expr1.type != Loc.type:
                gen(Loc.array_addr, '[', Loc.offset_addr, ']', '=', Loc.type, Expr1.addr)
            else:
                gen(Loc.array_addr, '[', Loc.offset_addr, ']', '=', Expr1.addr)
            Expr_Assign.addr = newTemp(Loc.type)
            Expr_Assign.type = Loc.type
            gen(Expr_Assign.addr, '=', Loc.array_addr, '[', Loc.offset_addr, ']')
            """
        ),
        SDT_right(
            ["id", "=", "Expr1"],
            # language=Python
            """
            if Expr1.type != top.get_type(id.lexeme):
                gen(top.get_addr(id.lexeme), '=', top.get_type(id.lexeme), Expr1.addr)
            else:
                gen(top.get_addr(id.lexeme), '=', Expr1.addr)
            Expr_Assign.addr = newTemp(top.get_type(id.lexeme))
            Expr_Assign.type = top.get_type(id.lexeme)
            gen(Expr_Assign.addr, '=', top.get_addr(id.lexeme))
            """
        ),
        SDT_right(
            ["Expr_Arith1"],
            # language=Python
            """
            Expr_Assign.addr = Expr_Arith1.addr
            Expr_Assign.type = Expr_Arith1.type
            """
        )
    ],
    "Expr_Arith": [
        SDT_right(
            ["Expr_Arith1", "+", "Expr_Term2"],
            # language=Python
            """
            Expr_Arith.type = resultAccuracy(Expr_Arith1.type, Expr_Term2.type)
            Expr_Arith.addr = newTemp(Expr_Arith.type)
            operand1 = Expr_Arith1.addr
            if Expr_Arith1.type != Expr_Arith.type:
                operand1 = newTemp(Expr_Arith.type)
                gen(operand1, '=', Expr_Arith1.type, Expr_Arith1.addr)
            operand2 = Expr_Term2.addr
            if Expr_Term2.type != Expr_Arith.type:
                operand2 = newTemp(Expr_Arith.type)
                gen(operand2, '=', Expr_Arith.type, Expr_Term2.addr)
            gen(Expr_Arith.addr, '=', operand1, '+', operand2)
            """
        ),
        SDT_right(
            ["Expr_Arith1", "-", "Expr_Term2"],
            # language=Python
            """
            Expr_Arith.type = resultAccuracy(Expr_Arith1.type, Expr_Term2.type)
            Expr_Arith.addr = newTemp(Expr_Arith.type)
            operand1 = Expr_Arith1.addr
            if Expr_Arith1.type != Expr_Arith.type:
                operand1 = newTemp(Expr_Arith.type)
                gen(operand1, '=', Expr_Arith1.type, Expr_Arith1.addr)
            operand2 = Expr_Term2.addr
            if Expr_Term2.type != Expr_Arith.type:
                operand2 = newTemp(Expr_Arith.type)
                gen(operand2, '=', Expr_Arith.type, Expr_Term2.addr)
            gen(Expr_Arith.addr, '=', operand1, '-', operand2)
            """
        ),
        SDT_right(
            ["Expr_Term1"],
            # language=Python
            """
            Expr_Arith.addr = Expr_Term1.addr
            Expr_Arith.type = Expr_Term1.type
            """
        )
    ],
    "Expr_Term": [
        SDT_right(
            ["Expr_Term1", "*", "Expr_Unary2"],
            # language=Python
            """
            Expr_Term.type = resultAccuracy(Expr_Term1.type, Expr_Unary2.type)
            Expr_Term.addr = newTemp(Expr_Term.type)
            operand1 = Expr_Term1.addr
            if Expr_Term1.type != Expr_Term.type:
                operand1 = newTemp(Expr_Term.type)
                gen(operand1, '=', Expr_Term1.type, Expr_Term1.addr)
            operand2 = Expr_Unary2.addr
            if Expr_Unary2.type != Expr_Term.type:
                operand2 = newTemp(Expr_Term.type)
                gen(operand2, '=', Expr_Term.type, Expr_Unary2.addr)
            gen(Expr_Term.addr, '=', operand1, '*', operand2)
            """
        ),
        SDT_right(
            ["Expr_Term1", "/", "Expr_Unary2"],
            # language=Python
            """
            Expr_Term.type = resultAccuracy(Expr_Term1.type, Expr_Unary2.type)
            Expr_Term.addr = newTemp(Expr_Term.type)
            operand1 = Expr_Term1.addr
            if Expr_Term1.type != Expr_Term.type:
                operand1 = newTemp(Expr_Term.type)
                gen(operand1, '=', Expr_Term1.type, Expr_Term1.addr)
            operand2 = Expr_Unary2.addr
            if Expr_Unary2.type != Expr_Term.type:
                operand2 = newTemp(Expr_Term.type)
                gen(operand2, '=', Expr_Term.type, Expr_Unary2.addr)
            gen(Expr_Term.addr, '=', operand1, '/', operand2)
            """
        ),
        SDT_right(
            ["Expr_Unary1"],
            # language=Python
            """
            Expr_Term.addr = Expr_Unary1.addr
            Expr_Term.type = Expr_Unary1.type
            """
        )
    ],
    "Expr_Unary": [
        SDT_right(
            ["-", "Expr_Unary1"],
            # language=Python
            """
            Expr_Unary.addr = newTemp(Expr_Unary1.type)
            Expr_Unary.type = Expr_Unary1.type
            gen(Expr_Unary.addr, '=', '-', Expr_Unary1.addr)
            """
        ),
        SDT_right(
            ["+", "Expr_Unary1"],
            # language=Python
            """
            Expr_Unary.addr = newTemp(Expr_Unary1.type)
            Expr_Unary.type = Expr_Unary1.type
            gen(Expr_Unary.addr, '=', '+', Expr_Unary1.addr)
            """
        ),
        SDT_right(
            ["(", "Basic", ")", "Expr_Unary1"],
            # language=Python
            """
            Expr_Unary.addr = newTemp(Basic.type)
            Expr_Unary.type = Basic.type
            gen(Expr_Unary.addr, '=', '(', Basic.type, ")", Expr_Unary1.addr)
            """
        ),
        SDT_right(
            ["(", "Expr1", ")"],
            # language=Python
            """
            Expr_Unary.addr = Expr1.addr
            Expr_Unary.type = Expr1.type
            """
        ),
        SDT_right(
            ["Loc"],
            # language=Python
            """
            Expr_Unary.addr = newTemp(Loc.type)
            Expr_Unary.type = Loc.type
            gen(Expr_Unary.addr, '=', Loc.array_addr, '[', Loc.offset_addr, ']')
            """
        ),
        SDT_right(
            ["id"],
            # language=Python
            """
            Expr_Unary.addr = top.get_addr(id.lexeme)
            Expr_Unary.type = top.get_type(id.lexeme)
            """
        ),
        SDT_right(
            ["num"],
            # language=Python
            """
            Expr_Unary.addr = num.lexval
            Expr_Unary.type = num.lextype
            """
        )
    ],
    "Loc": [
        SDT_right(
            ["Loc1", "[", "Expr", "]"],
            # language=Python
            """
            Loc.array_addr = Loc1.array_addr
            Loc.type = Loc1.type.elem_type
            t = newTemp(int)
            Loc.offset_addr = newTemp(int)
            gen(t, '=', Expr.addr, '*', Loc.type.width)
            gen(Loc.offset_addr, '=', Loc.offset_addr, '+', t)
            """
        ),
        SDT_right(
            ["id", "[", "Expr", "]"],
            # language=Python
            """
            Loc.array_addr = top.get_addr(id.lexeme)
            Loc.type = top.get_type(id.lexeme).elem_type
            if Loc.type == None:
                error(f"{id.lexeme} is not an array")
                # 错误处理：将其转为可以用的类型
                Loc.type = top.get_type(id.lexeme)
            Loc.offset_addr = newTemp(int)
            gen(Loc.offset_addr, '=', Expr.addr, '*', Loc.type.width)
            """
        )
    ],
}

# 检查SDT的语义动作是否每行都有缩进12个空格，然后删掉12个空格
for left_symbol in sdt_grammar.keys():
    for production_index in range(len(sdt_grammar[left_symbol])):
        action_lines = sdt_grammar[left_symbol][production_index].a.split('\n')
        # 第一行一定是空行，删掉
        assert action_lines[
                   0].strip() == '', f"文法中产生式{left_symbol}->{sdt_grammar[left_symbol][production_index]}中的语义动作缩进不正确"
        action_lines = action_lines[1:]
        for action_line in action_lines:
            if action_line.strip() == '':
                continue
            # 检查是否有12个空格缩进
            assert action_line.startswith(
                ' ' * 12), f"文法中产生式{left_symbol}->{sdt_grammar[left_symbol][production_index]}中的语义动作缩进不正确"
        # 删掉12个空格
        sdt_grammar[left_symbol][production_index].a = '\n'.join(
            [action_line[12:] for action_line in action_lines])

