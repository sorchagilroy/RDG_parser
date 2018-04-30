from dictionaries_unor import dictionaries
from collections import Counter, defaultdict
import itertools
import networkx as nx
import networkx.algorithms.isomorphism as iso

class rule_generator():
	def __init__(self,nodes,edges,src,tar,label,tent_label,ext):
		self.nodes = nodes
		self.edges = edges
		self.src = src
		self.tar = tar
		self.label = label
		self.tent_label = tent_label
		self.ext = ext
	
		dics = dictionaries(nodes,edges,src,tar,label,tent_label,ext)
		self.multi_sub_nodes, self.multi_sub_edges, self.multi_sub_src, self.multi_sub_tar, self.multi_sub_label, self.multi_sub_tent_label = dics.multi_subs()
		self.reentrant = dics.reentrancy()
		self.sub_nodes, self.sub_edges, self.sub_src, self.sub_tar, self.sub_label, self.sub_tent_label= dics.subs()
		self.leaves = dics.leaves()

	def dfs(self,graph,node,visited):
		if node not in visited:
			visited.append(node)
			for n in graph[node]:
				self.dfs(graph,n,visited)
		return visited

	def reorder(self,v,index):
		graph = {}
		for e in self.multi_sub_edges[v][index]:
			graph[self.multi_sub_src[v][index][e]] = self.multi_sub_tar[v][index][e]
		for n in self.multi_sub_nodes[v][index]:
			if n not in graph:
				graph[n] = []
		return self.dfs(graph,v,[])
	
	def make_rule(self,e,v,index,children):
		T = set([v]).union(self.multi_sub_tar[v][index][e])
		exts = set([v])
		for l in self.leaves:
			if l in self.reentrant[v][index] and l in self.multi_sub_nodes[v][index]:
				if self.reentrant[v][index][l] == True:
					T.add(l)
					exts.add(l)
			for c in self.multi_sub_tar[v][index][e]:
				for ind in self.reentrant[c]:
					if l in self.reentrant[c][ind]:
						if self.reentrant[c][ind][l]:
							T.add(l)
		for n in self.multi_sub_nodes[v][index]:
			if n in self.ext:
				exts.add(n)
				T.add(n)
		rule_nodes = {}
#map from nodes going in the rule to nodes in the graph
		rule_nodes[0] = v
		count = 1
		for t in T:
			if t != v:
				rule_nodes[count] = t
				count += 1
		rule_edges = set(['e1'])
		rule_src = {}
		rule_tar = {}
		rule_label = {}
		rule_tent_label = {}
		rule_tent_label['e1'] = {}
		rule_label['e1'] = self.multi_sub_label[v][index][e]
		rule_src['e1'] = 0
		rule_tar['e1'] = set()
		rule_tent_label['e1'][0] = 'src'
		edge_adds = 2
		count = 0
		nodes_used = set([0])
		for n in self.multi_sub_tar[v][index][e]:
			for i in rule_nodes:
				if rule_nodes[i] == n:
					ind = i
			if n not in self.leaves:
				edge = 'e' + str(edge_adds)
#				rule_tar['e1'].add(max(nodes_used)+1)
				rule_tar['e1'].add(ind)
#				rule_tent_label['e1'][max(nodes_used)+1] = self.multi_sub_tent_label[v][index][e][n]
#				rule_src[edge] = max(nodes_used)+1
				rule_tent_label['e1'][ind] = self.multi_sub_tent_label[v][index][e][n]
				rule_src[edge] = ind
				nodes_used = nodes_used.union(rule_tar['e1'])
				rule_edges.add(edge)
				rule_tar[edge] = set()
				rule_tent_label[edge] = {}
				edge_adds += 1
				for np in rule_nodes:
					if rule_nodes[np] in self.sub_nodes[n] and np != rule_src[edge]:
						rule_tar[edge].add(np)
						rule_tent_label[edge][np] = 0#self.multi_sub_tent_label[v][index][e][n]
#					if rule_nodes[np] in self.sub_nodes[n] and rule_nodes[np] == n:
#						rule_src[edge] = np
				nodes_used = nodes_used.union(rule_tar[edge])
				rule_label[edge] = 'NT'#children[n]
			else:
				if children[n] == False:
#					rule_tar['e1'].add(max(nodes_used)+1)
					rule_tar['e1'].add(ind)
#					rule_tent_label['e1'][max(nodes_used)+1] = self.multi_sub_tent_label[v][index][e][n]
					rule_tent_label['e1'][ind] = self.multi_sub_tent_label[v][index][e][n]
					nodes_used = nodes_used.union(rule_tar['e1'])
				else:
					for np in rule_nodes:
						if rule_nodes[np] == n:
							rule_tar['e1'].add(np)
							rule_tent_label['e1'][np] = self.multi_sub_tent_label[v][index][e][n]
					nodes_used = nodes_used.union(rule_tar['e1'])
			count += 1
		rule_ext = set()
		for i in rule_nodes:
			if rule_nodes[i] in exts:
				rule_ext.add(i)
		return [set(rule_nodes.keys()),rule_edges,rule_src,rule_tar,rule_label,rule_tent_label,rule_ext]


#This function takes in an existing fragment and a new candidate one and checks if they match. A pair match if they are isomorphic ignoring edge and node labels but taking tentacle labels into account."""

	def match(self,RULE,R,is_frag):
		[c_rule_nodes,c_rule_edges,c_rule_src,c_rule_tar,c_rule_label,c_rule_tent_label,c_rule_ext] = RULE #c rule for candidate rule
		[rule_nodes,rule_edges,rule_src,rule_tar,rule_label,rule_tent_label,rule_ext] = R
		tent_to_num = {}
		count = 0
		#to move things quicker, first just compare sizes of sets - if these don't match it's definitely not isomorphic.
		if len(c_rule_nodes) != len(rule_nodes):
			return False
		if len(c_rule_edges) != len(rule_edges):
			return False
		if len(c_rule_ext) != len(rule_ext):
			return False
		#can't see how to use networkx to take edge labels into account so converting to numerical values first
		for e in c_rule_edges:
			for v in c_rule_tar[e]:
				t = c_rule_tent_label[e][v]
				if t not in tent_to_num:
					tent_to_num[t] = count
					count +=1
		for e in rule_edges:
			for v in rule_tar[e]:
				t = rule_tent_label[e][v]
				if t not in tent_to_num:
					tent_to_num[t] = count
					count +=1
		#the terminals are the only ones with important tent labels, make rule sets all nonterminal tent labels to 0 to all be the same. In the ordered case, we would want these to be numbered.
		G1 = nx.DiGraph()
		G2 = nx.DiGraph()
		#giving external nodes weight 1 and the rest weight 0 so that we can distinguish them
		for c in c_rule_nodes:
			if c in c_rule_ext:
				G1.add_node(c,weight=1)
			else:
				G1.add_node(c,weight=0)
		for r in rule_nodes:
			if r in rule_ext:
				G2.add_node(r,weight=1)
			else:
				G2.add_node(r,weight=0)
		for e in c_rule_edges:
			for t in c_rule_tar[e]:
				G1.add_edge(c_rule_src[e],t, weight = tent_to_num[c_rule_tent_label[e][t]])
		for e in rule_edges:
			for t in rule_tar[e]:
				G2.add_edge(rule_src[e],t, weight=tent_to_num[rule_tent_label[e][t]])
		em = iso.numerical_edge_match('weight',1)
		nm = iso.numerical_node_match('weight',1)
		if nx.is_isomorphic(G1,G2,edge_match=em,node_match=nm):
#			print 'match found'
#			print 'candidate: ',RULE
#			print 'fragment: ',R
			return True
		else:
			return False	
