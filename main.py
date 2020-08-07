#!/usr/bin/env python
import sys, os
import matplotlib.pyplot as plt

plt.rcdefaults()
import numpy as np
import matplotlib.lines as mlines
import math
import matplotlib.patches as mpatches
from collections import defaultdict

N = 6


class Wall(mlines.Line2D, tuple):
    def __new__(tuple,a,b,N=N):
        return super(Wall,tuple).__new__(tuple,(a,b))

    def __init__(self, a, b, N=N):
        self.N = N
        # tuple.__init__(self, (a, b))
        ra, ca = self.derive_rc(a)
        rb, cb = self.derive_rc(b)
        try:
            assert ra == rb or ca == cb
            assert ra != rb or ca != cb
        except AssertionError:
            sys.stderr.write("Not valid wall. Error.")
            sys.exit()
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        # print(ra,rb,ca,cb)
        if ra == rb:  # horizonal
            # print(True)
            if ca > cb:
                ca, cb = cb, ca
            y1 = ca + 0.5
            y2 = ca + 0.5
            x1 = ra - 0.5
            x2 = ra + 0.5
        elif ca == cb:  # vertical
            if ra > rb:
                ra, rb = rb, ra
            x1 = ra + 0.5
            x2 = ra + 0.5
            y1 = ca - 0.5
            y2 = ca + 0.5
        # print(x1,y1,x2,y2)
        mlines.Line2D.__init__(
            self, (x1, x2), (y1, y2), lw=7, alpha=1.0, color="black", gid=None
        )

    def derive_rc(self, n):
        return (n % self.N, n // self.N)

    def derive_n(self, a):
        c, r = a
        return r * self.N + c


class Walls(list):
    def __init__(self, income):
        tmp = list()
        if os.path.isfile(str(income)):
            for line in open(income):
                a = int(line.split()[0])
                b = int(line.split()[1])
                tmp2 = Wall(a, b)
                tmp.append(Wall(a, b))
        else:
            for (a, b) in income:
                tmp.append(Wall(a, b))
        super().__init__(tmp)


class Walker(mpatches.Wedge):
    def __init__(self, loc=(-1, 0), color="red", **kwargs):
        super().__init__(loc, 0.3, 45, 314, color=color, **kwargs)
        self.loc = loc
        self.status = "free"


class Stone(mpatches.Circle):
    def __init__(self, loc=(-1, 0), color="black", **kwargs):
        super().__init__(loc, 0.2, color=color, **kwargs)
        self.loc = loc
        self.status = "wild"


class Goal(mpatches.Circle):
    def __init__(self, loc=(-1, 0), color="pink", **kwargs):
        super().__init__(loc, 0.4, color=color, **kwargs)
        self.loc = loc
        self.status = "new"


class Target(mpatches.RegularPolygon):
    def __init__(self, loc=(-1, 0), color="green", **kwargs):
        super().__init__(loc, 5, 0.3, color=color, **kwargs)
        self.loc = loc
        self.status = "new"


class Map:
    def __init__(self, N=N):
        self.graph = defaultdict(list)
        self.N = N
        for i in range(N * N):
            r, c = self.derive_rc(i)
            up = (r - 1, c)
            down = (r + 1, c)
            left = (r, c - 1)
            right = (r, c + 1)
            for r, c in (up, down, left, right):
                if r < 0 or r >= N or c < 0 or c >= N:
                    continue
                else:
                    self.addEdge(i, self.derive_n((r, c)))
        # self.make_distance_matrix()

    def derive_rc(self, n):
        return (n % self.N, n // self.N)

    def derive_n(self, a):
        c, r = a
        return r * self.N + c

    def addEdge(self, u, v):
        if v not in self.graph[u]:
            self.graph[u].append(v)
        if u not in self.graph[v]:
            self.graph[v].append(u)

    def delEdge(self, u, v):
        if v in self.graph[u]:
            self.graph[u].remove(v)
        if u in self.graph[v]:
            self.graph[v].remove(u)

    def make_distance_matrix(self):
        self.dist = defaultdict(list)
        for i in range(self.N * self.N):
            visited = self.BFS(i)
            self.dist[i] = visited

    def find_shortest_path(self, a, b):
        path = [
            a,
        ]
        self._find_nearest_to_next(a, b, path)
        return path

    def _find_nearest_to_next(self, a, b, path):
        aim_dist = self.dist[a][b]
        for current_index, i in enumerate(self.dist[a]):
            if i == 1 and self.dist[current_index][b] == aim_dist - 1:
                path.append(current_index)
                self._find_nearest_to_next(current_index, b, path)
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

    def set_up_walls(self, ws):
        for w in ws:
            self.delEdge(w[0], w[1])
        self.walls = ws

    def generate_condition(self, nsample=None):
        if nsample == None:
            nsample = self.N
        N = self.N
        start = 0
        goal = N * N - 1
        all_point = list(range(N * N))
        all_point.remove(start)
        all_point.remove(goal)
        import random as rd

        all_sample = rd.sample(all_point, 2 * nsample)
        all_target_index = rd.sample(all_sample, nsample)
        all_stone_index = [x for x in all_sample if x not in all_target_index]
        all_target = [Target(self.derive_rc(x)) for x in all_target_index]
        all_stone = [Stone(self.derive_rc(x)) for x in all_stone_index]
        self.all_target = all_target
        self.all_stone = all_stone
        self.walker = Walker((0, 0))
        self.goal = Goal((N - 1, N - 1))
        self.walker_index = 0
        self.goal_index = N * N - 1
        self.all_target_index = all_target_index
        self.all_stone_index = all_stone_index
        return all_target, all_stone

    def generate_fig(self, output="output.png"):
        fig, ax = plt.subplots()
        board_lines = self.make_board(self.N)
        self.draw_lines(board_lines, ax)
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        for stone in self.all_stone:
            ax.add_patch(stone)
        for target in self.all_target:
            ax.add_patch(target)
        ax.add_patch(self.walker)
        ax.add_patch(self.goal)
        for w in self.walls:
            ax.add_line(w)

        plt.axis("equal")
        plt.axis("off")
        plt.savefig(output)
        plt.close()

    def make_board(self, N=None):
        if N == None:
            N = self.N
        l = list()
        for i in range(0, N + 1):
            for j in range(0, N + 1):
                l.append([x - 0.5 for x in (i, i, 0, N)])
                l.append([x - 0.5 for x in (0, N, i, i)])
        return l

    def draw_lines(self, lines, ax, color="grey", lw=3, alpha=0.2, gid=None):
        for l in lines:
            x = l[0:2]
            y = l[2:4]
            line = mlines.Line2D(x, y, lw=lw, alpha=alpha, color=color, gid=gid)
            ax.add_line(line)
            for i in range(self.N * self.N):
                ax.annotate(
                    "%d" % i,
                    self.derive_rc(i),
                    color="grey",
                    weight="bold",
                    fontsize="xx-large",
                    ha="center",
                    va="center",
                    fontweight="light",
                    zorder=0,
                )

    def find_solution(self):
        best_path = None
        best_s = self.N ** 4
        for (path, s) in self.sample_all_possible_solution():
            if s < best_s:
                best_path = path
                best_s = s
        self.best_path = best_path
        self.best_s = best_s

    def sample_all_possible_solution(self):
        from copy import deepcopy as dc

        target_index = dc(self.all_target_index)
        stone_index = dc(self.all_stone_index)
        for list_target in Map.permute(target_index, 0, len(target_index) - 1):
            for list_stone in Map.permute(stone_index, 0, len(stone_index) - 1):
                path = list()
                path.append(self.walker_index)
                for i in range(len(list_target)):
                    path.append(list_stone[i])
                    path.append(list_target[i])
                path.append(self.goal_index)
                s = 0
                for i in range(len(path) - 1):
                    s += self.dist[path[i]][path[i + 1]]
                yield (path, s)

    @staticmethod
    def permute(
        a, l, r
    ):  # https://www.geeksforgeeks.org/write-a-c-program-to-print-all-permutations-of-a-given-string/
        if l == r:
            yield a
        else:
            for i in range(l, r + 1):
                a[l], a[i] = a[i], a[l]
                yield from Map.permute(a, l + 1, r)
                a[l], a[i] = a[i], a[l]


def test():
    if not os.path.isdir("data"):
        os.mkdir("data")
    fig, ax = plt.subplots()
    board_lines = make_board()
    draw_lines(board_lines, ax)
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)

    walker = Walker()
    stone = Stone()
    target = Target()
    ax.add_patch(walker)
    ax.add_patch(stone)
    ax.add_patch(target)

    plt.axis("equal")
    plt.axis("off")
    plt.savefig("test.png")
    plt.close()


a = Map()
a.set_up_walls(Walls("walls"))
a.generate_condition(nsample=6)
a.make_distance_matrix()
a.find_solution()
print(a.best_path)
print(a.best_s)
a.generate_fig()

sys.exit()
