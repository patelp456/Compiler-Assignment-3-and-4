#!/usr/bin/env python
import ply.yacc as yacc, sys
import subprocess
import Symbol_Table as SymbolTable
import ThreeAddrCode as ThreeAddrCode
import pprint
from lexer import tokens

###########################
ST = SymbolTable.SymbTbl()
TAC = ThreeAddrCode.threeAddressCode(ST)
###########################

#------------------------------------------------------------------------------------
# The grammer rules start here.

def p_CompilationUnit(p):
	''' CompilationUnit : ProgramFile '''
	ST.Printsymbtbl()
	pprint.pprint(TAC.code)

def p_OP_DIM(p):
	''' OP_DIM : LSQPAREN RSQPAREN '''

def p_TypeSpecifier(p):
	''' TypeSpecifier : TypeName
	| TypeName Dims '''

	if(len(p) == 2) :
		p[0] = p[1]

def p_TypeName(p):
	''' TypeName : PrimitiveType
	| QualifiedName '''

	p[0] = p[1]

def p_ClassNameList(p):
	''' ClassNameList : QualifiedName
        | ClassNameList COMMA QualifiedName '''

def p_PrimitiveType(p):
	''' PrimitiveType : BOOLEAN
	| CHAR
	| BYTE
	| SHORT
	| INT
	| LONG
	| FLOAT
	| DOUBLE
	| VOID '''

	p[0] = p[1]

def p_SemiColons(p):
	''' SemiColons : SEMICOLON
        | SemiColons SEMICOLON '''



def p_ProgramFile(p):
	''' ProgramFile : PackageStatement ImportStatements TypeDeclarations
	| PackageStatement                  TypeDeclarations
	|                  ImportStatements TypeDeclarations
	|                                   TypeDeclarations '''

def p_PackageStatement(p):
	''' PackageStatement : PACKAGE QualifiedName SemiColons '''

def p_TypeDeclarations(p):
	''' TypeDeclarations : TypeDeclarationOptSemi
	| TypeDeclarations TypeDeclarationOptSemi '''

def p_TypeDeclarationOptSemi(p):
	''' TypeDeclarationOptSemi : TypeDeclaration
        | TypeDeclaration SemiColons '''

def p_ImportStatements(p):
	''' ImportStatements : ImportStatement
	| ImportStatements ImportStatement '''

def p_ImportStatement(p):
	''' ImportStatement : IMPORT QualifiedName SemiColons
	| IMPORT QualifiedName DOT MULT SemiColons '''

def p_QualifiedName(p):
	''' QualifiedName : IDENTIFIER
	| QualifiedName DOT IDENTIFIER '''

	p[0] = {}
	if(len(p) == 2) :
		p[0]['Name'] = p[1]
		# p[0]['Type'] = "int"
		# print str(p[1])
		# print "Hello"
		#pprint.pprint(ST.scopelist[-1]['identifiers'][p[1]])
		# pprint.pprint(ST.scopelist)
		# p[0]['Type'] = "int "
	else :
		p[0]['Name'] = p[1]['Name'] + '.' + p[3]

def p_TypeDeclaration(p):
	''' TypeDeclaration : ClassHeader LCURPAREN FieldDeclarations RCURPAREN
	| ClassHeader LCURPAREN RCURPAREN '''

def p_ClassHeader(p):
	''' ClassHeader : Modifiers ClassWord IDENTIFIER
	|           ClassWord IDENTIFIER '''

	if(len(p) == 4):
		p[0] = {'Modifiers' : p[1], 'ClassName' : p[3]}
	else :
		p[0] = {'Modifiers' : [], 'ClassName' : p[2]}

	ST.Add_scope(p[0]['ClassName'], 'Class')

def p_Modifiers(p):
	''' Modifiers : Modifier
	| Modifiers Modifier '''

	if(len(p) == 2) :
		p[0] = p[1]
	else :
		p[0] = p[1]
		p[0].append(p[2]);

def p_Modifier(p):
	''' Modifier : PUBLIC
	| PRIVATE
	| STATIC
	'''
	p[0] = list(p[1])

def p_ClassWord(p):
	''' ClassWord : CLASS '''

def p_FieldDeclarations(p):
	''' FieldDeclarations : FieldDeclarationOptSemi
		| FieldDeclarations FieldDeclarationOptSemi '''    

	p[0] = p[1]

def p_FieldDeclarationOptSemi(p):
	''' FieldDeclarationOptSemi : FieldDeclaration
        | FieldDeclaration SemiColons '''
	p[0] = p[1]

def p_FieldDeclaration(p):
	''' FieldDeclaration : FieldVariableDeclaration SEMICOLON
	| MethodDeclaration
	| ConstructorDeclaration
	| StaticInitializer
        | NonStaticInitializer
        | TypeDeclaration '''

	p[0] = p[1]

def p_FieldVariableDeclaration(p):
	''' FieldVariableDeclaration : Modifiers TypeSpecifier VariableDeclarators
	|           TypeSpecifier VariableDeclarators '''

def p_VariableDeclarators(p):
	''' VariableDeclarators : VariableDeclarator
	| VariableDeclarators COMMA VariableDeclarator '''

	p[0] = {}
	p[0]['Type'] = p[-1]
	if len(p) == 2 :
		p[0]['Names'] = list(p[1]['Name'])
	else:
		p[0]['Names'] = p[1]['Names']
		p[0]['Names'].append(p[3]['Name'])

def p_VariableDeclarator(p):
	''' VariableDeclarator : DeclaratorName
	| DeclaratorName EQUAL VariableInitializer '''

	p[0] = {}
	p[0]['Name'] = p[1]

	if(p[-1] == ",") :
		p[0]['Type'] = p[-2]['Type']
	else :
		p[0]['Type'] = p[-1]

	if(len(p) == 4):
		if(p[0]['Type'] == p[3]['Type']) :
			TAC.emit(p[0]['Name'],p[3]['Name'],'','=')
		else:
			print "Error in VariableDeclarator"

def p_VariableInitializer(p):
	''' VariableInitializer : Expression '''
	p[0] = p[1]


def p_MethodDeclaration(p):
	''' MethodDeclaration : Modifiers TypeSpecifier MethodDeclarator MethodBody
	|           TypeSpecifier MethodDeclarator MethodBody '''

	if(len(p) == 5):
		p[0] = {'Modifiers' : p[1], 'Type' : p[2], 'Name' : p[3]['Name'], 'ParamList' : p[3]['List']}

def p_MethodDeclarator(p):
	''' MethodDeclarator : DeclaratorName LROUNPAREN ParameterList RROUNPAREN
	| DeclaratorName LROUNPAREN RROUNPAREN '''

	if(len(p) == 5) :
		p[0] = {'Name' : p[1], 'List' : p[3]}
	else :
		p[0] = {'Name' : p[1], 'List' : []}

	ST.Add_scope(p[0]['Name'], 'Function')
	TAC.genNewTacFunc(p[0]['Name'])

def p_ParameterList(p):
	''' ParameterList : Parameter
	| ParameterList COMMA Parameter '''

	if(len(p) == 2) :
		p[0] = p[1]
	else :
		p[0] = p[1]
		p[0].append(p[3])
	
def p_Parameter(p):
	''' Parameter : TypeSpecifier DeclaratorName '''
	p[0] = [{'Type' : p[1], 'Name' : p[2]}]

def p_DeclaratorName(p):
	''' DeclaratorName : IDENTIFIER
        | DeclaratorName OP_DIM '''

	p[0] = p[1]

def p_MethodBody(p):
	''' MethodBody : Block
	| SEMICOLON '''

	p[0] = p[1]

def p_ConstructorDeclaration(p):
	''' ConstructorDeclaration : Modifiers ConstructorDeclarator        Block
	|           ConstructorDeclarator        Block '''

def p_ConstructorDeclarator(p):
	''' ConstructorDeclarator : IDENTIFIER LROUNPAREN ParameterList RROUNPAREN
	| IDENTIFIER LROUNPAREN RROUNPAREN '''

def p_StaticInitializer(p):
	''' StaticInitializer : STATIC Block '''

def p_NonStaticInitializer(p):
	''' NonStaticInitializer : Block '''

def p_Block(p):
	''' Block : LCURPAREN LocalVariableDeclarationsAndStatements RCURPAREN
	| LCURPAREN RCURPAREN '''

	if(len(p) == 4) :
		p[0] = p[2]
	else :
		p[0] = {}

def p_LocalVariableDeclarationsAndStatements(p):
	''' LocalVariableDeclarationsAndStatements : LocalVariableDeclarationOrStatement
	| LocalVariableDeclarationsAndStatements LocalVariableDeclarationOrStatement '''

	if(len(p) == 3) :
		p[0] = p[1]
		p[0]['loopEndList'] = TAC.merge(p[1].get('loopEndList', []), p[2].get('loopEndList', []))
		p[0]['loopBeginList'] = TAC.merge(p[1].get('loopBeginList', []), p[2].get('loopBeginList', []))
	else :
		p[0] = p[1]



def p_LocalVariableDeclarationOrStatement(p):
	''' LocalVariableDeclarationOrStatement : LocalVariableDeclarationStatement
	| Statement '''

	p[0] = p[1]

def p_LocalVariableDeclarationStatement(p):
	''' LocalVariableDeclarationStatement : TypeSpecifier VariableDeclarators SEMICOLON '''

	p[0] = {'Type' : p[1], 'Names' : p[2]['Names']}
	for identifer in p[2]['Names']:
		if ST.Exists_curr_scope(identifer) == False:
			ST.Add_identifier(identifer, p[1])
		else :
			print "Error in Variable Declarator"

def p_Statement(p):
	''' Statement : EmptyStatement Mark_quad
	| LabelStatement Mark_quad
	| ExpressionStatement SEMICOLON Mark_quad
	| JumpStatement Mark_quad
	| Block Mark_quad'''

	p[0] = {}
	Next = p[1].get('nextlist', [])
	p[0]['nextlist'] = Next
	# if(len(p) == 3):
	# 	TAC.backPatch(Next,p[2]['quad'])
	# else :
	# 	TAC.backPatch(Next,p[3]['quad'])

	# p[0] = p[1]
	p[0]['loopEndList'] = p[1].get('loopEndList',[]);
	p[0]['loopBeginList'] = p[1].get('loopBeginList',[]);

def p_Statement_1(p):
	''' Statement :  IterationStatement Mark_quad
					| SelectionStatement Mark_quad '''
	p[0] = {}
	Next = p[1].get('nextlist', [])
	p[0]['nextlist'] = Next
	if(len(p) == 3):
		TAC.backPatch(Next,p[2]['quad'])
	else :
		TAC.backPatch(Next,p[3]['quad'])
	#print Next
	# print "Hello"
	# p[0] = p[1]
	p[0]['loopEndList'] = p[1].get('loopEndList',[]);
	p[0]['loopBeginList'] = p[1].get('loopBeginList',[]);

def p_Mark_quad(p):
	''' Mark_quad : '''
	p[0] = {'quad' : TAC.getNextInstr()}

def p_EmptyStatement(p):
	''' EmptyStatement : SEMICOLON '''

def p_LabelStatement(p):
	''' LabelStatement : IDENTIFIER COLON
        | CASE ConstantExpression COLON
	| DEFAULT COLON '''

def p_ExpressionStatement(p):
	''' ExpressionStatement : Expression '''
	p[0] = p[1]

def p_SelectionStatement(p):
	''' SelectionStatement : If_1 LROUNPAREN Expression RROUNPAREN Mark_if Statement '''
	
	p[0] = {}

	p[0]['nextlist'] = p[5].get('falselist',[])
	p[0]['loopEndList'] = p[6].get('loopEndList', [])
	p[0]['loopBeginList'] = p[6].get('loopBeginList',[])

def p_SelectionStatement_2(p):
	''' SelectionStatement : If_1 LROUNPAREN Expression RROUNPAREN Mark_if Statement ELSE Mark_else Statement '''
	p[0] = {}

# else :
	TAC.backPatch(p[5]['falselist'], p[8]['quad'])
	p[0]['nextlist'] = p[8]['nextlist']
	p[0]['loopEndList'] = p[6].get('loopEndList', [])
	p[0]['loopBeginList'] = p[6].get('loopBeginList',[])
  #   else:
		# TAC.backPatch(p[5]['falseList'], p[8]['quad'])
		# p[0]['nextList'] = p[8]['nextList']
		# p[0]['loopEndList'] = p[6].get('loopEndList', [])
		# p[0]['loopBeginList'] = p[6].get('loopBeginList',[])
	# | SWITCH LROUNPAREN Expression RROUNPAREN Block '''
	
def p_If_1(p):
	''' If : IF'''
	ST.Add_scope("if", "if");

def p_Mark_if(p):
	''' Mark_if : '''
	p[0] = {}
	p[0]['falselist'] = [TAC.getNextInstr()]
	# print p[0]['falselist']
	
	TAC.emit(p[-2]['Name'],'',-1,'COND_GOTO')

def p_Mark_else(p):
	''' Mark_else : '''
	p[0] = {}
	p[0]['nextlist'] = [TAC.getNextInstr()]
	
	TAC.emit('','',-1,'GOTO')
	p[0]['quad'] = TAC.getNextInstr()

def p_IterationStatement_while(p):
	''' IterationStatement : WHILE Mark_quad LROUNPAREN Expression RROUNPAREN Mark_while Statement '''

	p[0] = {}
	p[0]['nextlist'] = []

	TAC.backPatch(p[7]['loopBeginList'], p[2]['quad'])
	p[0]['nextlist'] = TAC.merge(p[7].get('loopEndList',[]), p[7].get('nextlist',[]))
	p[0]['nextlist'] = TAC.merge(p[6].get('falselist',[]), p[7].get('loopEndList',[]))



	TAC.emit ('','',p[2]['quad'], 'GOTO')

def p_Mark_while(p):
	''' Mark_while : '''

	p[0] = {}
	p[0]['falselist'] = [TAC.getNextInstr()]
	TAC.emit(p[-2]['Name'],'',-1,'COND_GOTO')

def p_IterationStatement_dowhile(p):
	''' IterationStatement : Do Mark_quad Statement WHILE LROUNPAREN Expression Mark_dowhile RROUNPAREN SEMICOLON '''


	p[0] = {}
	p[0]['nextlist'] = []

	TAC.backPatch(p[3]['loopBeginList'], p[2]['quad'])
	# p[0]['nextlist'] = TAC.merge(p[7].get('loopEndList',[]), p[7].get('nextlist',[]))
	p[0]['nextlist'] = TAC.merge(p[2].get('falselist',[]), p[3].get('loopEndList',[]))
	TAC.emit (p[6]['Name'],'',p[2]['quad'], 'COND_GOTO_TR')


def p_Do(p):
	''' Do : DO '''
	p[0] = {}

def p_Mark_dowhile(p):
	''' Mark_dowhile : '''

	p[0] = {}
	p[0]['falselist'] = [TAC.getNextInstr()]
	# TAC.emit('','',-1,'COND_GOTO')

def p_IterationStatement_for(p):
	''' IterationStatement : FOR LROUNPAREN ForInit ForExpr Mark_quad ForIncr RROUNPAREN Mark_quad Statement '''
	p[0] = {}
	p[0]['nextlist'] = []

	TAC.backPatch(p[9]['loopBeginList'], p[5]['quad'])
	TAC.backPatch(p[4]['truelist'], p[8]['quad'])
	p[0]['nextlist'] = TAC.merge(p[4].get('falselist',[]), p[9].get('loopEndList',[]))
	TAC.emit (p[5]['quad'],'','', 'GOTO')


def p_IterationStatement_for_2(p):
	''' IterationStatement : FOR LROUNPAREN ForInit ForExpr         RROUNPAREN Statement '''

def p_ForInit(p):
	''' ForInit : ExpressionStatements SEMICOLON 
	| LocalVariableDeclarationStatement 
	| SEMICOLON '''

def p_ForExpr(p):
	''' ForExpr : Mark_quad Expression SEMICOLON
	| Mark_quad SEMICOLON '''
	if(len(p) == 4) :
		p[0] = p[2]
		p[0]['falselist'] = [TAC.getNextInstr()]
		TAC.emit(p[2]['Name'], '', -1, 'COND_GOTO')
		p[0]['truelist'] = [TAC.getNextInstr()]
		p[0]['quad'] = p[1]['quad']

def p_ForIncr(p):
	''' ForIncr : ExpressionStatements  '''

	p[0] = {}
	TAC.emit(p[-2]['quad'],'','','GOTO')

def p_ExpressionStatements(p):
	''' ExpressionStatements : ExpressionStatement
	| ExpressionStatements COMMA ExpressionStatement '''

def p_JumpStatement(p):
	''' JumpStatement : BREAK            SEMICOLON
	| CONTINUE            SEMICOLON
	| RETURN Expression SEMICOLON
	| RETURN            SEMICOLON '''


###############
###############

def p_PrimaryExpression(p):
	''' PrimaryExpression : QualifiedName '''
	p[0] = p[1]
	# print p[1]['Name']
	# print ST.Get_attr(p[1]['Name'],'Type')
	if(ST.Get_attr(p[1]['Name'],'Type') != None) :
		p[0]['Type'] = ST.Get_attr(p[1]['Name'],'Type')

def p_PrimaryExpression_nn(p):
	''' PrimaryExpression : NotJustName '''

	p[0] = p[1]


def p_NotJustName(p):
	''' NotJustName : SpecialName
	| NewAllocationExpression
	| ComplexPrimary '''
	p[0] = p[1]

def p_ComplexPrimary(p):
	''' ComplexPrimary : LROUNPAREN Expression RROUNPAREN
	| ComplexPrimaryNoParenthesis '''
	if(len(p) == 2):
		p[0] = p[1]
	else :
		p[0] = p[2]

def p_ComplexPrimaryNoParenthesis_int(p):
	''' ComplexPrimaryNoParenthesis : INT_CONST '''
	p[0] = {}
	p[0]['Type'] = "int"
	p[0]['Name'] = ST.Gen_Temp()
	TAC.emit(p[0]['Name'],p[1],'','=')


def p_ComplexPrimaryNoParenthesis_temp(p):
	''' ComplexPrimaryNoParenthesis : FLOAT_CONST '''
	p[0] = {}
	p[0]['Type'] = "float"
	p[0]['Name'] = ST.Gen_Temp()
	TAC.emit(p[0]['Name'],p[1],'','=')

def p_ComplexPrimaryNoParenthesis_string(p):
	''' ComplexPrimaryNoParenthesis : STRING '''
	p[0] = {}
	p[0]['Type'] = "string"
	p[0]['Name'] = ST.Gen_Temp()
	ST.Add_string(p[0]['Name'],p[1])


def p_ComplexPrimaryNoParenthesis_char(p):
	''' ComplexPrimaryNoParenthesis : CHAR_CONST '''


def p_ComplexPrimaryNoParenthesis_bool(p):
	''' ComplexPrimaryNoParenthesis : BOOLEAN_CONST '''
	p[0] = {}
	p[0]['Type'] = "bool"
	p[0]['Name'] = ST.Gen_Temp()
	TAC.emit(p[0]['Name'],p[1],'','=')
	# ST.Add_string(p[0]['Name'],p[1])
	# p[0]['truelist'] = [TAC.getNextInstr()]
	# print p[0]['Name']


def p_ComplexPrimaryNoParenthesis_rem(p):
	''' ComplexPrimaryNoParenthesis : ArrayAccess
	| FieldAccess '''

	p[0] = p[1]

def p_ComplexPrimaryNoParenthesis_met(p): 
	''' ComplexPrimaryNoParenthesis : MethodCall '''
	p[0] = p[1]

def p_ArrayAccess(p):
	''' ArrayAccess : QualifiedName LSQPAREN Expression RSQPAREN
	| ComplexPrimary LSQPAREN Expression RSQPAREN '''

def p_FieldAccess(p):
	''' FieldAccess : NotJustName DOT IDENTIFIER
	| RealPostfixExpression DOT IDENTIFIER
        | QualifiedName DOT THIS
        | QualifiedName DOT CLASS
        | PrimitiveType DOT CLASS '''

def p_MethodCall(p):
	''' MethodCall : MethodAccess LROUNPAREN ArgumentList RROUNPAREN
	| MethodAccess LROUNPAREN RROUNPAREN '''
	p[0] = {}
	p[0]['Name'] = p[1]['Name']
	if(p[0]['Name'] == 'System.out.println') :
		TAC.emit(p[3][0]['Name'],'',p[3][0]['Type'],'Print')

def p_MethodAccess(p):
	''' MethodAccess : SpecialName '''

def p_MethodAccess(p) :
	''' MethodAccess : QualifiedName '''
	p[0] = p[1]


def p_SpecialName(p):
	''' SpecialName : THIS
	| SUPER
	| NULL '''

def p_ArgumentList(p):
	''' ArgumentList : Expression
	| ArgumentList COMMA Expression '''

	if(len(p) == 2) :
		p[0] = [p[1]]
	else :
		p[0] = p[1]
		p[0].append(p[3])

def p_NewAllocationExpression(p):
	''' NewAllocationExpression : PlainNewAllocationExpression
        | QualifiedName DOT PlainNewAllocationExpression '''

def p_PlainNewAllocationExpression(p):
	''' PlainNewAllocationExpression : ArrayAllocationExpression
    	| ClassAllocationExpression
    	| ArrayAllocationExpression LCURPAREN RCURPAREN
    	| ClassAllocationExpression LCURPAREN RCURPAREN
    	| ClassAllocationExpression LCURPAREN FieldDeclarations RCURPAREN '''

def p_ClassAllocationExpression(p):
	''' ClassAllocationExpression : NEW TypeName LROUNPAREN ArgumentList RROUNPAREN
	| NEW TypeName LROUNPAREN              RROUNPAREN '''

def p_ArrayAllocationExpression(p):
	''' ArrayAllocationExpression : NEW TypeName DimExprs Dims
	| NEW TypeName DimExprs
        | NEW TypeName Dims '''

def p_DimExprs(p):
	''' DimExprs : DimExpr
	| DimExprs DimExpr '''

def p_DimExpr(p):
	''' DimExpr : LSQPAREN Expression RSQPAREN '''

def p_Dims(p):
	''' Dims : OP_DIM
	| Dims OP_DIM '''

def p_PostfixExpression(p):
	''' PostfixExpression : PrimaryExpression
	| RealPostfixExpression '''
	p[0] = p[1]

def p_RealPostfixExpression(p):
	''' RealPostfixExpression : PostfixExpression OP_INC
	| PostfixExpression OP_DEC '''

def p_UnaryExpression(p):
	''' UnaryExpression : OP_INC UnaryExpression
	| OP_DEC UnaryExpression
	| ArithmeticUnaryOperator CastExpression
	| LogicalUnaryExpression '''
	if(len(p) == 2) :
		p[0] = p[1]

def p_LogicalUnaryExpression(p):
	''' LogicalUnaryExpression : PostfixExpression
	| LogicalUnaryOperator UnaryExpression '''
	if(len(p) == 2) :
		p[0] = p[1]

def p_LogicalUnaryOperator(p):
	''' LogicalUnaryOperator : '~'
	| NOT '''

def p_ArithmeticUnaryOperator(p):
	''' ArithmeticUnaryOperator : PLUS
	| MINUS '''

def p_CastExpression(p):
	''' CastExpression : UnaryExpression '''
	# | LROUNPAREN PrimitiveTypeExpression RROUNPAREN CastExpression
	# | LROUNPAREN ClassTypeExpression RROUNPAREN CastExpression
	# | LROUNPAREN Expression RROUNPAREN LogicalUnaryExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]

def p_PrimitiveTypeExpression(p):
	''' PrimitiveTypeExpression : PrimitiveType
        | PrimitiveType Dims '''

def p_ClassTypeExpression(p):
	''' ClassTypeExpression : QualifiedName Dims '''

def p_MultiplicativeExpression(p):
	''' MultiplicativeExpression : CastExpression
	| MultiplicativeExpression MULT CastExpression
	| MultiplicativeExpression DIV CastExpression
	| MultiplicativeExpression MOD CastExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = p[3]['Type']
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_ConditionalAndExpression";
def p_AdditiveExpression(p):
	''' AdditiveExpression : MultiplicativeExpression
        | AdditiveExpression PLUS MultiplicativeExpression
	| AdditiveExpression MINUS MultiplicativeExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = p[3]['Type']
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_ConditionalAndExpression";

def p_ShiftExpression(p):
	''' ShiftExpression : AdditiveExpression
        | ShiftExpression OP_SHL AdditiveExpression
        | ShiftExpression OP_SHR AdditiveExpression
        | ShiftExpression OP_SHRR AdditiveExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]

def p_RelationalExpression(p):
	''' RelationalExpression : ShiftExpression
        | RelationalExpression LESS ShiftExpression
	| RelationalExpression MORE ShiftExpression
	| RelationalExpression OP_LE ShiftExpression
	| RelationalExpression OP_GE ShiftExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = p[3]['Type']
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_RelationalExpression";

def p_EqualityExpression(p):
	''' EqualityExpression : RelationalExpression
        | EqualityExpression OP_EQ RelationalExpression
        | EqualityExpression OP_NE RelationalExpression '''
   	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = "bool"
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_EqualityExpression";

def p_AndExpression(p):
	''' AndExpression : EqualityExpression
	| AndExpression '&' EqualityExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = "bool"
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_AndExpression";


def p_ExclusiveOrExpression(p):
	''' ExclusiveOrExpression : AndExpression
	| ExclusiveOrExpression '^' AndExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = "bool"
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_ExclusiveOrExpression";	

def p_InclusiveOrExpression(p):
	''' InclusiveOrExpression : ExclusiveOrExpression
	| InclusiveOrExpression '|' ExclusiveOrExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = "bool"
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_InclusiveOrExpression";

def p_ConditionalAndExpression(p):
	''' ConditionalAndExpression : InclusiveOrExpression
	| ConditionalAndExpression OP_LAND InclusiveOrExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = "bool"
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_ConditionalAndExpression";

def p_ConditionalOrExpression(p):
	''' ConditionalOrExpression : ConditionalAndExpression
	| ConditionalOrExpression OP_LOR ConditionalAndExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(p[1]['Type'] == p[3]['Type']) :
			p[0]['Name'] = ST.Gen_Temp()
			p[0]['Type'] = "bool"
			TAC.emit(p[0]['Name'],p[1]['Name'],p[3]['Name'],p[2])
		else:
			print "Error in p_ConditionalOrExpression";

def p_ConditionalExpression(p):
	''' ConditionalExpression : ConditionalOrExpression
	| ConditionalOrExpression '?' Expression COLON ConditionalExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]

def p_AssignmentExpression(p):
	''' AssignmentExpression : ConditionalExpression
	| UnaryExpression AssignmentOperator AssignmentExpression '''
	p[0] = {}
	if(len(p) == 2) :
		p[0] = p[1]
	else :
		if(ST.Get_attr(p[1]['Name'],'Type') == p[3]['Type']):
			p[0]['Type'] = p[3]['Type']
			p[0]['Name'] = ST.Gen_Temp()
			TAC.emit(p[1]['Name'],p[3]['Name'],'',p[2])
		else :
			print "Error in AssignmentExpression"


def p_AssignmentOperator(p):
	''' AssignmentOperator : EQUAL
	| ASS_MUL
	| ASS_ADD
	| ASS_SUB '''

	p[0] = p[1]

def p_Expression(p):
	''' Expression : AssignmentExpression '''
	p[0] = p[1]


def p_ConstantExpression(p):
	''' ConstantExpression : ConditionalExpression '''

def p_error(p):
	print('error: {}'.format(p))
#---------------------------------------------------------------------------------------------------------

# Set up a logging object
import logging
logging.basicConfig(
	level = logging.DEBUG,
	filename = "parselog.txt",
	filemode = "w",
	format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()


#Building the parser
parser = yacc.yacc(debug=True)

if __name__ == '__main__':
   try:
		f = sys.argv[1]
		data = open(f).read()	
   except EOFError:
   		print 'Error in Parsing'
   if data:
		result = parser.parse(data,debug=log)
		# print result

#-----------------------------------------------------------------------------------------------------

# Convert the parselog to .dot file for graph generation
print("\n")
subprocess.call(['./dotgen.sh'])