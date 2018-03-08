#!/usr/bin/python

from collections import defaultdict
import optparse
from dictionaries import dictionaries
from rule_generator import rule_generator
import sys

optparser = optparse.OptionParser()
optparser.add_option("-n",'--number',dest='lang_id', default='1',help='Which language you want as input.')
(opts,_) = optparser.parse_args()


nodes = {}
edges = {}
src = {}
tar = {}
label = {}
lhs = {}
ext = {}
RDG = []



#f = open('language%s.txt'%opts.lang_id)
f = open('bolt_dag.txt')
for line in f:
	if '#' in line:
		pass
	else:
		if 'nodes =' in line:
			nodes = eval(line.split('=')[1])
		if 'edges =' in line:
			edges = eval(line.split('=')[1])
		if 'src =' in line:
			src = eval(line.split('=')[1])
		if 'tar =' in line: 
			tar = eval(line.split('=')[1])
		if 'label =' in line and 'tent label =' not in line:
			label = eval(line.split('=')[1])
		if 'lhs =' in line:
			lhs = eval(line.split('=')[1])
		if 'ext = ' in line:
			ext = eval(line.split('=')[1])
		if 'RDG' in line:
			RDG = eval(line.split('=')[1]) 
		if 'lang' in line:
			lang = eval(line.split('=')[1])		

non_terms = []
rules = []
clone_rules = set()
lhs = {}
num_to_rule = {}
fragments = []
def parses_to(node,index,NT_counter,rule_counter,dics):
#	print 'node: ',node
	v = node
	returns = []
	multi_sub_nodes,_,_,multi_sub_tar,_ = dics.multi_subs()
	if dics.out_degree(v) > 1 and index == -1:
		X = []
		for i in multi_sub_nodes[v].keys():
			p,NT_counter,rule_counter = parses_to(v,i,NT_counter,rule_counter,dics)
			X.append(set(p))
		NTs = set.intersection(*X)
		returns = []
		for nt in NTs:
#			if has_clone_rule(nt) == True:
#				returns.append(nt)
			returns.append(nt)
			clone_rules.add(nt)
#		for nt in set(NTs):
#			tree[node].append(nt)
	else:
		if index == -1:
			index = 0
		e = dics.edge_below(v,index)
		children = []
		for n in multi_sub_tar[v][index][e]:
			if n in dics.leaves():
				if n in dics.ext:
					children.append(True)
				else:
					tars = []
					for ep in multi_sub_tar[v][index]:
						if ep != e:
							tars = tars + multi_sub_tar[v][index][ep]
					if n in tars:
						children.append(True)
					else:
						children.append(False)	
	#				children.append(reentrant[v][index][n])
			else:
				p,NT_counter,rule_counter = parses_to(n,-1,NT_counter,rule_counter,dics)#[0]
#				print 'node: ',node
#				print 'p: ',p
				children.append(p[0])#only keeps one nonterminal for now - change
		r_g = rule_generator(dics.nodes, dics.edges, dics.src, dics.tar, dics.label, dics.ext)
		RULE = r_g.make_rule(e,v,index,children)
#		print 'node: ',node
#		print 'rule: ',RULE
		count = 0
		for n in num_to_rule:
			if r_g.match(RULE,num_to_rule[n],False):
				returns.append(lhs[n])
				count += 1
				tree[node].append(n)
		if count == 0:					
			lhs[rule_counter] = "X"+str(NT_counter)
			num_to_rule[rule_counter] = RULE
			rule_counter += 1
			NT_counter += 1
			rules.append(RULE)
			returns.append(lhs[rule_counter-1])
			tree[node].append(rule_counter-1)
		f_count = 0
		for f in fragments:
			if r_g.match(RULE,f,True):
				f_count +=1
		if f_count == 0:
			fragments.append(RULE)
#		for R in RDG:
#			if match(RULE,R):
#				returns.append(lhs[R])
	return returns,NT_counter,rule_counter

def is_connected(G):
	graph = defaultdict(list)
        for e in edges[G]:                                                                                                                                                                        
                graph[src[G][e]] = graph[src[G][e]] + tar[G][e]
        for n in nodes[G]:                                                                                                                                                                        
                if n not in graph:                                                                                                                                                                                 
                        graph[n] = []       
	rg = rule_generator(nodes[G],edges[G],src[G],tar[G],label[G],ext[G])                                                                                                                                                                       
        visited =  rg.dfs(graph,0,[])
	if set(visited) == set(nodes[G]):
		return True
	else:
#		print 'visited: ',visited
#		print 'nodes[G]: ',nodes[G]
		return False
non_cons = 0
tot = 0
#currently just outputs a grammar for each. Happens to have some same rules but only because it finds things in the same order (this won't happen in general)
for G in lang:
	if True:#G != 'G369' and G != 'G664' and G != 'G1132' and G != 'G1133':#removing 369 as has a cycle with the root (fix this), probably same issue for 664
		tot += 1
		sys.stderr.write('%s\n'%G)
#		print 'G: ',G
#		print 'nodes: ',nodes[G]
#		print 'edges: ',edges[G]
#		print 'src: ',src[G]
#		print 'tar: ',tar[G]
#		print 'label: ',label[G]
#		print 'ext: ',ext[G]
		tree = defaultdict(list)
		if is_connected(G) == False:
#			print 'Graph is not connected.'
			non_cons += 1
		else:
			dics = dictionaries(nodes[G],edges[G],src[G],tar[G],label[G],ext[G])
			returns,NT_counter,rule_counter = parses_to(0,-1,0,0,dics)
			for n in num_to_rule:
#				print '\nn: ',n
#				print 'lhs: ',lhs[n]
#				print 'rhs: ',num_to_rule[n]
				if lhs[n] in clone_rules:
					pass
#					print 'Clone rule of rank %s for nonterminal %s'%(len(num_to_rule[n][5]),lhs[n]) 
		#	print 'clone rules: ',clone_rules
#			print 'start NT: ',returns
#			print 'tree: ',tree
#fragments = []
#for rule in rules:
#	count = 0
#	g = nodes.keys()[0]
#	rg = rule_generator(nodes[g],edges[g],src[g],tar[g],label[g],ext[g])
#	for f in fragments:
#		if rg.match(rule,f,True):
#			count +=1 
#	if count == 0:
#		fragments.append(rule)
print '\n\n'
print 'Building blocks: '
for f in fragments:
	print f
for n in num_to_rule:
	if lhs[n] in clone_rules:
		print 'Clone rule of rank %s allowed' %(len(num_to_rule[n][5]))
print 'Total number of graphs: ',tot
print 'Number of graphs not connected: ',non_cons
