class dictionaries():
	def __init__(self,nodes,edges,src,tar,label,ext):
		self.nodes = nodes
		self.edges = edges
		self.src = src
		self.tar = tar
		self.label = label
		self.ext = ext
	
	def sub_dag(self,n):
		sub_nodes = [n]
		for e in self.edges:
			if self.src[e] in sub_nodes:
				sub_nodes = sub_nodes + self.tar[e]
		sub_nodes = set(sub_nodes)
		sub_edges = []
		for e in self.edges:
			if self.src[e] in sub_nodes:
				if set(self.tar[e]).issubset(sub_nodes):
					sub_edges.append(e)
		return [sub_nodes,sub_edges]

	def out_degree(self, v):
		out = 0
		for e in self.edges:
			if self.src[e] == v:
				out +=1
		return out
	
	def subgraphs_below(self,v):
		if self.out_degree(v) <= 1:
			return [self.sub_dag(v)]
		[sub_nodes,sub_edges] = self.sub_dag(v)
		subgraphs = []
		for e in sub_edges:
			if self.src[e] == v:
				n_subs = set([v])
				e_subs = set([e])
				for n in self.tar[e]:
					n_subs = n_subs.union(set(self.sub_dag(n)[0]))
					e_subs = e_subs.union(set(self.sub_dag(n)[1]))
				subgraphs.append([n_subs,e_subs])
		return subgraphs

	def edge_below(self,v,index):
		_,multi_sub_edges,multi_sub_src,_,_ = self.multi_subs()
		for e in multi_sub_edges[v][index]:
			if multi_sub_src[v][index][e] == v:
				return e

	def subs(self):
		sub_nodes = {}
		sub_edges = {}
		sub_src = {}
		sub_tar = {}
		sub_label = {}
		for n in self.nodes:
			sub_nodes[n] = self.sub_dag(n)[0]
			sub_edges[n] = self.sub_dag(n)[1]
			sub_src[n] = {}
			sub_tar[n] = {}
			sub_label[n] = {}
			for e in self.edges:
				if e in sub_edges[n]:
					sub_src[n][e] = self.src[e]
					sub_tar[n][e] = self.tar[e]
					sub_label[n][e] = self.label[e]
		return sub_nodes,sub_edges,sub_src,sub_tar,sub_label

	def multi_subs(self):
		multi_sub_nodes = {}
		multi_sub_edges = {}
		multi_sub_src = {}
		multi_sub_tar = {}
		multi_sub_label = {}
		for n in self.nodes:
			multi_sub_nodes[n] = {}
			multi_sub_edges[n] = {}
			multi_sub_src[n] = {}
			multi_sub_tar[n] = {}
			multi_sub_label[n] = {}
			if self.out_degree(n) > 1:
				graphs = self.subgraphs_below(n)
				for i in range(len(graphs)):
					multi_sub_nodes[n][i] = graphs[i][0]
					multi_sub_edges[n][i] = graphs[i][1]
					multi_sub_src[n][i] = {}
					multi_sub_tar[n][i] = {}
					multi_sub_label[n][i] = {}
					for e in self.edges:
						if e in multi_sub_edges[n][i]:
							multi_sub_src[n][i][e] = self.src[e]
							multi_sub_tar[n][i][e] = self.tar[e]
							multi_sub_label[n][i][e] = self.label[e]
			else:
				graph = self.sub_dag(n)
				_,_,sub_src,sub_tar,sub_label = self.subs()
				multi_sub_nodes[n][0] = graph[0]
				multi_sub_edges[n][0] = graph[1]
				multi_sub_src[n][0] = sub_src[n]
				multi_sub_tar[n][0] = sub_tar[n]
				multi_sub_label[n][0] = sub_label[n]
		return multi_sub_nodes, multi_sub_edges,multi_sub_src, multi_sub_tar,multi_sub_label

	def reentrancy(self):
		reentrant = {}
		multi_sub_nodes, multi_sub_edges,_,_,_ = self.multi_subs()
		for n in self.nodes:
			reentrant[n] = {}
			for i in multi_sub_nodes[n]:
				reentrant[n][i] = {}
				for v in multi_sub_nodes[n][i]:
					tars = []
					for e in self.edges:
						if e not in multi_sub_edges[n][i]:
							tars = tars + self.tar[e]
					if len(multi_sub_nodes[n][i]) == 1:
						reentrant[n][i][v] = False
					elif tars.count(v) > 0:
						reentrant[n][i][v] = True
					else:
						reentrant[n][i][v] = False
		return reentrant

	def leaves(self):
		return [n for n in self.nodes if n not in self.src.values()]
	
	def roots(self):
		return [n for n in self.nodes if n not in self.tar.values()]

