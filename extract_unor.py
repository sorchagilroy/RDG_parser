#!/usr/bin/python

from collections import defaultdict
import optparse
from dictionaries_unor import dictionaries
from rule_generator_unor import rule_generator
import sys

optparser = optparse.OptionParser()
optparser.add_option("-n",'--number',dest='lang_id', default='1',help='Which language you want as input.')
(opts,_) = optparser.parse_args()

#out = open('output_all/all_trees.txt',"w+")

nodes = {}
edges = {}
src = {}
tar = {}
label = {}
tent_label = {}
lhs = {}
ext = {}
RDG = []

#specify the input file- assumed to be in a format that the below can handle.
f = open('data/amr2_tester.txt')
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
		if 'tent label =' in line:
			tent_label = eval(line.split('=')[1])
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
fragments = defaultdict(list)
frag_terms = defaultdict(list)
frag_used = defaultdict(list)
def parses_to(G,node,index,NT_counter,rule_counter,dics,tree):
	sys.stderr.write('%s\n'%node)
	v = node
	returns = []
	multi_sub_nodes,_,_,multi_sub_tar,_,_ = dics.multi_subs()
	if dics.out_degree(v) > 1 and index == -1:
		X = []
		for i in multi_sub_nodes[v].keys():
			p,NT_counter,rule_counter = parses_to(G,v,i,NT_counter,rule_counter,dics,tree)
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
		children = {}
		for n in multi_sub_tar[v][index][e]:
			if n in dics.leaves():
				if n in dics.ext:
					children[n] = True
				else:
					tars = []
					for ep in multi_sub_tar[v][index]:
						if ep != e:
							tars = tars + list(multi_sub_tar[v][index][ep])
					if n in tars:
						children[n] = True
					else:
						children[n] = False
			else:
				p,NT_counter,rule_counter,tree = parses_to(G,n,-1,NT_counter,rule_counter,dics,tree)#[0]
				children[n] = p[0]
		r_g = rule_generator(dics.nodes, dics.edges, dics.src, dics.tar, dics.label, dics.tent_label, dics.ext)
		RULE = r_g.make_rule(e,v,index,children)
#below is commented out for now but was used as the parser rather than extractor. Need to use the tree maker from this
#		count = 0
#		for n in num_to_rule:
#			if r_g.match(RULE,num_to_rule[n],False):
#				returns.append(lhs[n])
#				count += 1
#				tree[node].append(n)
#		if count == 0:					
#			lhs[rule_counter] = "X"+str(NT_counter)
#			num_to_rule[rule_counter] = RULE
#			rule_counter += 1
#			NT_counter += 1
#			rules.append(RULE)
#			returns.append(lhs[rule_counter-1])
#			tree[node].append(rule_counter-1)
		f_count = 0
#the below sorting makes sure we look at the most used fragments first
		fs = sorted(fragments, key = lambda k: len(frag_used[k]))
		for f in fs:
			if f_count ==0:
				if r_g.match(RULE,fragments[f],True):
					f_count +=1
					returns.append(f)
					[ns,es,srcs,trs,labs,tntlabs,exts]=RULE
					frag_terms[f].append(labs['e1'])
					frag_used[f].append(G)
					tree[node].append(f)
		if f_count == 0:
			fragments[len(fragments)] = RULE
			[ns,es,srcs,trs,labs,tntlabs,exts] = RULE
			frag_terms[len(fragments)-1].append(labs['e1'])
			frag_used[len(fragments)-1].append(G)
			tree[node].append(len(fragments)-1)
#instead of just NT- could have NTi for rank i?
			returns.append('NT')#if you want all the NTs to look the same
			#returns.append('X'+str(len(fragments))) # if you want the NTs to be different
#		for R in RDG:
#			if match(RULE,R):
#				returns.append(lhs[R])
	return returns,NT_counter,rule_counter,tree

def is_connected(G):
	graph = defaultdict(set)
        for e in edges[G]:
                graph[src[G][e]] = graph[src[G][e]].union(tar[G][e])
        for n in nodes[G]:
                if n not in graph: 
                        graph[n] = set()
	rg = rule_generator(nodes[G],edges[G],src[G],tar[G],label[G],tent_label[G],ext[G])                                                                                                                                                                       
        visited =  rg.dfs(graph,0,[])
	if set(visited) == set(nodes[G]):
		return True
	else:
		return False
non_cons = 0
tot = 0
count = 0
for G in lang:
	count += 1
	if True:#G not in ots:#True:#change this if you want to look at a specific example
		tot += 1
		sys.stderr.write('%s\n'%G)
#		out.write('G: %s\n'%G)
#		print 'G: ',G
#		print 'nodes = ',nodes[G]
#		print 'edges = ',edges[G]
#		print 'src = ',src[G]
#		print 'tar = ',tar[G]
#		print 'label = ',label[G]
#		print 'tent label = ',tent_label[G]
#		print 'ext = ',ext[G]
#		print 'lang = [\'%s\']'%G
		tree = defaultdict(list)
		if is_connected(G) == False:
#			print 'Graph is not connected.'
			non_cons += 1
		else:
			dics = dictionaries(nodes[G],edges[G],src[G],tar[G],label[G],tent_label[G],ext[G])
			returns,NT_counter,rule_counter,tree_frags = parses_to(G,0,-1,0,0,dics,tree)
			tree_struct = {}
			tree_term = {}
			tree_tents = {}
			for e in edges[G]:
				if len(set(tar[G][e]).intersection(set(src[G].values()))) != 0:
					tree_struct[src[G][e]] = []
					tree_tents[src[G][e]] = {}
					for n in tar[G][e]:
						if n in src[G].values():
							tree_struct[src[G][e]].append(n)
							tree_tents[src[G][e]][n] = tent_label[G][e][n]
				tree_term[src[G][e]] = label[G][e]
#			out.write('tree structure: %s'%tree_struct)
#			out.write('tree terminals: %s'%tree_term)
#			out.write('tree fragments: %s'%tree_frags)
#			out.write('tree tents: %s\n'%tree_tents)
			print 'tree structure: ',tree_struct
			print 'tree terminals: ',tree_term
			print 'tree fragments: ',tree_frags
			print 'tree_tents: ',tree_tents
			if count%1000 == 0:
#				out.write('After %s graphs\n'%count)
				print 'After %s graphs'%count
				for f in fragments:
#					out.write('%s'%f)
					print f
#					out.write('\n')
#					out.write('%s'%fragments[f])
					print fragments[f]
#					out.write('\nPossible terminals: %s'%frag_terms[f])
					print 'Possible terminals: ',frag_terms[f]
#					out.write('Used in graphs: %s\n'%frag_used[f])
					print 'Used in graphs: ',frag_used[f]
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
#out.write('\n\n')
#out.write('Building blocks: \n')
print '\n\n'
print 'Building blocks: '
count = 1
for f in fragments:
#	out.write('%s'%f)
#	out.write('\n')
#	out.write('%s'%fragments[f])
#	out.write('\n')
#	count +=1
#	out.write('Possible terminals: %s'%frag_terms[f])
#	out.write('Used in graphs: %s\n'%frag_used[f])
	print f
	print fragments[f]
	count += 1
	print 'Possible terminals: ',frag_terms[f]
	print 'Used in graphs: ',frag_used[f]
for n in num_to_rule:
	if lhs[n] in clone_rules:
#		out.write('Clone rule of rank %s allowed\n'%(len(num_to_rule[n][5])))
		print 'Clone rule of rank %s allowed \n'%len(num_to_rule[n][5])
#out.write('Total number of graphs: %s\n'%tot)
print 'Total number of graphs: %s\n'%tot
#out.write('Number of graphs not connected: %s\n'%non_cons)
print 'Number of graphs not connected: %s\n'%non_cons
