from dictionaries import dictionaries

class rule_generator():
	def __init__(self,nodes,edges,src,tar,label,ext):
		self.nodes = nodes
		self.edges = edges
		self.src = src
		self.tar = tar
		self.label = label
		self.ext = ext
	
		dics = dictionaries(nodes,edges,src,tar,label,ext)
		self.multi_sub_nodes, self.multi_sub_edges, self.multi_sub_src, self.multi_sub_tar, self.multi_sub_label = dics.multi_subs()
		self.reentrant = dics.reentrancy()
		self.sub_nodes, self.sub_edges, self.sub_src, self.sub_tar, self.sub_label = dics.subs()
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
		T = [v] + self.multi_sub_tar[v][index][e]
		exts = [v]
		for l in self.leaves:
			if l in self.reentrant[v][index] and l in self.multi_sub_nodes[v][index]:
				if self.reentrant[v][index][l] == True:
					T.append(l)
					exts.append(l)
			for c in self.multi_sub_tar[v][index][e]:
				for ind in self.reentrant[c]:
					if l in self.reentrant[c][ind]:
						if self.reentrant[c][ind][l]:
							T.append(l)
		for n in self.multi_sub_nodes[v][index]:
			if n in self.ext:
				exts.append(n)
				T.append(n)
		trav = self.reorder(v,index)
		Tp = []
		for t in trav:
			if t in T:
				Tp.append(t)
		T = Tp
		rule_nodes = range(len(T))
		rule_edges = ['e1']
		rule_src = {}
		rule_tar = {}
		rule_label = {}
		rule_label['e1'] = self.multi_sub_label[v][index][e]
		rule_src['e1'] = 0
		rule_tar['e1'] = []
		edge_adds = 2
		count = 0
		nodes_used = [0]
		for n in self.multi_sub_tar[v][index][e]:
			if n not in self.leaves:
				edge = 'e' + str(edge_adds)
				rule_tar['e1'].append(max(nodes_used)+1)
				rule_src[edge] = max(nodes_used)+1
				nodes_used = nodes_used + rule_tar['e1']
				rule_edges.append(edge)
				rule_tar[edge] = []
				edge_adds += 1
				for np in rule_nodes:
					if T[np] in self.sub_nodes[n] and np != rule_src[edge]:
						rule_tar[edge].append(np)
					if T[np] in self.sub_nodes[n] and T[np] == n:
						rule_src[edge] = np
				nodes_used = nodes_used + rule_tar[edge]
				rule_label[edge] = children[count]
			else:
				if children[count] == False:
					rule_tar['e1'].append(max(nodes_used)+1)
					nodes_used = nodes_used + rule_tar['e1']
				else:
					for np in rule_nodes:
						if T[np] == n:
							rule_tar['e1'].append(np)
					nodes_used = nodes_used + rule_tar['e1']
			count += 1
		rule_ext = []
		for i in range(len(T)):
			if T[i] in exts:
				rule_ext.append(i)
		return [rule_nodes,rule_edges,rule_src,rule_tar,rule_label,rule_ext]


	def match(self,RULE,R,is_frag):
		[c_rule_nodes,c_rule_edges,c_rule_src,c_rule_tar,c_rule_label,c_rule_ext] = RULE
		[rule_nodes,rule_edges,rule_src,rule_tar,rule_label,rule_ext] = R
		if c_rule_nodes != rule_nodes:
			return False
		if c_rule_edges != rule_edges:
			return False
		for e in c_rule_edges:
			if c_rule_src[e] != rule_src[e]:
				return False
			if c_rule_tar[e] != rule_tar[e]:
				return False
			if c_rule_label[e] != rule_label[e]:
				if is_frag == False:
					return False
				else:
					if rule_label[e].islower():
						return False
		if c_rule_ext != rule_ext:
			return False
		return True
