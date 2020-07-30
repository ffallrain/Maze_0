#!/usr/bin/env python
import sys,os
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import matplotlib.lines as mlines
import math
import matplotlib.patches as mpatches
from collections import defaultdict

N = 6
def make_board():
    l = list()
    for i in range(0,N+1):
        for j in range(0,N+1):
            l.append([x-0.5 for x in (i,i,0,N)])
            l.append([x-0.5 for x in (0,N,i,i)])
    return l

def make_blank_board_line_ids():
    ids = { 'h':list(),'v':list() }
    for x in range(N):
        for y in range(N+1):
            ids['h'].append( (x,y) )
    for x in range(N+1):
        for y in range(N):
            ids['v'].append( (x,y) )
    return ids

def draw_lines(lines,ax,color='grey',lw=5,alpha=0.3,gid=None):
    for l in lines:
        x = l[0:2]
        y = l[2:4]
        line = mlines.Line2D(x , y, lw=lw, alpha=alpha,color=color,gid=gid)
        ax.add_line(line)

class Walker(mpatches.Wedge):
    def __init__(self,loc=(-1,0),color = 'red',**kwargs):
        super().__init__((1,1),0.3,45,314,color = color, **kwargs)
class Stone(mpatches.Circle):
    def __init__(self,loc=(-1,0),color = 'black', **kwargs):
        super().__init__((2,2),0.2,color = color , **kwargs)
class Target(mpatches.RegularPolygon):
    def __init__(self,loc=(-1,0),color = 'green', **kwargs):
        super().__init__((3,2),5,0.3,color = color , **kwargs)

class Map:
    def __init__(self,N=N):
        self.graph = defaultdict(list)
        self.N = N
        for i in range(N*N):
            r,c = self.derive_rc(i)
            up = (r-1,c)
            down = (r+1,c)
            left = (r,c-1)
            right = (r,c+1)
            for r,c in (up,down,left,right):
                if r<0 or r>=N or c<0 or c>=N:
                    continue
                else:
                    self.addEdge(i,self.derive_n((r,c)))
        # self.make_distance_matrix()
    
    def derive_rc(self,n):
        return( n//self.N, n%self.N )
    def derive_n(self, a ):
        r,c = a
        return r * self.N + c 

    def addEdge(self,u,v):
        if v not in self.graph[u]:
            self.graph[u].append(v)
        if u not in self.graph[v]:
            self.graph[v].append(u)
    def delEdge(self,u,v):
        if v in self.graph[u]:
            self.graph[u].remove(v)
        if u in self.graph[v]:
            self.graph[v].remove(u)

    def make_distance_matrix(self):
        self.dist = defaultdict(list)
        for i in range(self.N*self.N):
            visited = self.BFS(i)
            self.dist[i] = visited

    def find_shortest_path(self,a,b):
        path = [a,]
        self._find_nearest_to_next(a,b,path)
        return path
        
    def _find_nearest_to_next(self,a,b,path):
        aim_dist = self.dist[a][b]
        for current_index,i in enumerate( self.dist[a]):
            if i == 1 and self.dist[current_index][b] == aim_dist - 1:
                path.append(current_index)
                self._find_nearest_to_next(current_index,b,path)
                break
        return

    def BFS(self, s):
        visited = [-1] * (len(self.graph))
        queue = []
        queue.append(s)
        visited[s] = 0
        while queue:
            s = queue.pop(0)
            for i in self.graph[s]:
                if visited[i] == -1:
                    queue.append(i)
                    visited[i] = visited[s] + 1
        return visited

def test():
    if not os.path.isdir("data"):
        os.mkdir("data")
    fig,ax = plt.subplots()
    board_lines = make_board()
    draw_lines(board_lines,ax)
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)

    walker = Walker()
    stone = Stone()
    target = Target()
    ax.add_patch(walker)
    ax.add_patch(stone)
    ax.add_patch(target)

    plt.axis('equal')
    plt.axis('off')
    plt.savefig("test.png")
    plt.close()

a = Map()
a.delEdge(0,N)
a.make_distance_matrix()

path = a.find_shortest_path(0,18)
print(path)
sys.exit()

    
