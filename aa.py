import sys,os
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import matplotlib.lines as mlines
import math
import matplotlib.patches as mpatches

N = 6
# add a line
def make_board():
    l = list()
    for i in range(0,N):
        for j in range(0,N):
            l.append([x-0.5 for x in (i,i,0,N-1)])
            l.append([x-0.5 for x in (0,N-1,i,i)])
    return l

def make_blank_board_line_ids():
    ids = { 'h':list(),'v':list() }
    for x in range(N-1):
        for y in range(N):
            ids['h'].append( (x,y) )
    for x in range(N):
        for y in range(N-1):
            ids['v'].append( (x,y) )
    return ids

# draw lines
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

if True:  # test
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

sys.exit()


    
# draw piece
def draw_piece(lines,ax,color='g',lw=15,alpha=0.7,gid="P"):
    draw_lines(lines,ax,color,lw,alpha,gid=gid)
    pass

# generate piece all possible locations
def generate_all_loc():
    loc = list()
    for i in range(-1,5):
        for j in range(-1,5):
            for k in range(8):
                loc.append((i,j,k))
    loc = np.array(loc)
    return loc

# generate logical all possible locations
def generate_logic_all_loc(piece,board=None,all_loc = None):
    if all_loc is None:
        all_loc = generate_all_loc()
    keep_loc = list()
    for loc in all_loc:
        ids = derive_piece_line_ids(piece,loc)
        if check_lines_in_board(ids,board=board):
            keep_loc.append(loc)
    return keep_loc

# derive piece line_ids :
def derive_piece_line_ids(piece,loc):
    piece = np.array(piece)
    ids = { 'h':list(),'v':list() }
    # Treat mirror
    if loc[2] in (4,5,6,7):
        for i in range(len(piece)):
            piece[i][0] = 0 - piece[i][0]
    # Rotate
    new_piece = list()
    A = math.pi * 0.5 * (loc[2]%4)
    cosA = math.cos(A)
    sinA = math.sin(A)
    for tmp in piece :
        x,y = tmp
        nx = round(x * cosA - y * sinA)
        ny = round(x * sinA + y * cosA)
        new_piece.append( (nx,ny) )
    for tmp in new_piece:
        if tmp[0]%2==0 and tmp[1]%2==1: # horizonal 
            x = tmp[0]/2. + loc[0]
            y = (tmp[1]+1)/2. + loc[1]
            ids['h'].append( (x,y) )
        elif tmp[0]%2==1 and tmp[1]%2==0: # vertical 
            x = (tmp[0]+1)/2. + loc[0]
            y = tmp[1]/2. + loc[1]
            ids['v'].append( (x,y) )
        else:
            print("Error")
            raise Exception
    return ids

# derive piece lines:
def derive_piece_lines( ids ):
    all_lines = list()
    if check_lines_in_board(ids):
        pass
    else:
        pass
        # return False
    for a in ids['v'] : # vertical
        x,y = a
        x0 = x
        x1 = x
        y0 = y
        y1 = y+1
        all_lines.append( (x0,x1,y0,y1) )
    for a in ids['h'] : # horizonal
        x,y = a
        x0 = x
        x1 = x + 1
        y0 = y
        y1 = y
        all_lines.append( (x0,x1,y0,y1) )
    return all_lines

# derive piece lines interface:
def compute_piece_lines( piece, loc ):
    ids = derive_piece_line_ids(piece,loc)
    lines = derive_piece_lines(ids)
    return lines

def check_lines_in_board( ids,board = {'h':list(),'v':list()} ):
    in_board = True
    for a in ids['v'] : # vertical
        x,y=a
        if 0<=x<5 and 0<=y<4:
            pass
        else:
            in_board = False
    for a in ids['h'] : # horizonal
        x,y=a
        if 0<=x<4 and 0<=y<5:
            pass
        else:
            in_board = False
    if True: # board != None:
        for a in ids['v']:
            if a in board['v']:
                in_board = False
        for a in ids['h']:
            if a in board['h']:
                in_board = False
    return in_board

def make_graphic( piece_loc, found_count):
    if not os.path.isdir("data"):
        os.mkdir("data")
    fig,ax = plt.subplots()
    board_lines = make_board()
    draw_lines(board_lines,ax)
    for name,loc in piece_loc.items():
        print(name,loc)
        color = piece_colors[name]
        piece = all_pieces[name]
        piece_lines = compute_piece_lines( piece, loc )
        print(piece_lines)
        draw_piece(piece_lines,ax,color=color)
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.axis('equal')
    plt.axis('off')
    plt.savefig("data/%d.png"%(found_count,))
    plt.close()

def check_solution( piece_loc ):
    all_cross_points = set()
    for name in ['l','u','t','j']:
        cross_point = np.array(piece_cross_point[name])
        loc = piece_loc[name]
        # Flip
        if loc[2] in (4,5,6,7):
            for i in range(len(cross_point)):
                cross_point[i][0] = 0 - cross_point[i][0]
        # Rotate
        new_cross_point = list()
        A = math.pi * 0.5 * (loc[2]%4)
        cosA = math.cos(A)
        sinA = math.sin(A)
        for tmp in cross_point :
            x,y = tmp
            nx = x * cosA - y * sinA
            ny = x * sinA + y * cosA
            new_cross_point.append( (nx,ny) )
        for x,y in new_cross_point:
            if (x+loc[0],y+loc[1]) in all_cross_points:
                return False
            else:
                all_cross_points.add( (x+loc[0],y+loc[1]) )
    print(all_cross_points)
    return True


if True:
    piece_h = ( (0,1) ,(1,0), (-1,0),(-1,2) )
    piece_x = ( (0,1) ,(2,1), (1,0), (1,2)  )
    piece_w = ( (-1,2),(1,0), (0,1), (2,-1) )
    piece_u = ( (-1,0),(0,-1),(2,-1),(3,0)  )
    piece_s = ( (-1,2),(0,1), (0,-1),(1,0)  )
    piece_l = ( (-1,0),(-1,2),(-1,4),(0,-1) )
    piece_j = ( (-1,0),(-1,2),(1,0), (0,-1) )
    piece_n = ( (-1,0),(-1,2),(0,1), (0,-1) )
    piece_t = ( (-1,0),(-1,2),(-1,4),(0,1)  )
    piece_y = ( (-1,2),(1,0), (0,1), (2,1)  )
    cross_points_l = ( (-0.5,0.5), (-0.5,1.5) )
    cross_points_j = ( (-0.5,0.5), )
    cross_points_u = ( (0.5,-0.5), )
    cross_points_t = ( (-0.5,1.5), )
    piece_cross_point = { "l" : cross_points_l, "l" : cross_points_l,
                          "j" : cross_points_u, "j" : cross_points_j,
                          "t" : cross_points_t, "t" : cross_points_t,
                          "u" : cross_points_u, "u" : cross_points_u,
    }

    all_pieces = { 'h': piece_h ,
                   'x': piece_x ,
                   'w': piece_w ,
                   'u': piece_u ,
                   's': piece_s ,
                   'l': piece_l ,
                   'j': piece_j ,
                   'n': piece_n ,
                   't': piece_t ,
                   'y': piece_y ,
    }
    piece_colors ={'h': "dimgray" ,
                   'x': "green" ,
                   'w': "magenta" ,
                   'u': "black" ,
                   's': "red" ,
                   'l': "blue" ,
                   'j': "purple" ,
                   'n': "orange" ,
                   't': "brown" ,
                   'y': "yellow" ,
    }

    def _generate_legal_loc_for_piece( piece ):
        all_loc = list()
        keep_uniq = list()
        for i in range(-1,5):
            for j in range(-1,5):
                for k in range(8):
                    loc = (i,j,k)
                    ids = derive_piece_line_ids(piece,loc)
                    if check_lines_in_board(ids):
                        a = list(ids['h'])
                        b = list(ids['v'])
                        a.sort()
                        b.sort()
                        uniq = a+b
                        if uniq not in keep_uniq:
                            keep_uniq.append(uniq)
                            all_loc.append(loc)
        return all_loc
    piece_locs = dict()
    for name,piece in all_pieces.items():
        piece_locs[name] = _generate_legal_loc_for_piece(piece)

piece_list = list(all_pieces.keys())
current_board = list()

def place_piece(board,piece,loc):
    ids = derive_piece_line_ids(piece,loc)
    for a in ids['h']: # horizonal  
        board['h'].append(a)
    for a in ids['v']: # vertical
        board['v'].append(a)
    # print(">>>>> Placed piece")
    # print(">>>>> Current board: %s"%board)

def remove_piece(board,piece,loc):
    ids = derive_piece_line_ids(piece,loc)
    for a in ids['h']: # horizonal  
        board['h'].remove(a)
    for a in ids['v']: # vertical
        board['v'].remove(a)

global_piece_loc = dict()
for name in piece_list:
    global_piece_loc[name] = None


count = 0
found_count = 0
def place_next( current_board, current_index ):
    global found_count
    global count
    global global_piece_loc

    count += 1
    if count %1000 == 0:
        print (">>>>> Trying %d times"%count)
    if current_index == 10:
        if check_solution(global_piece_loc):
            make_graphic(global_piece_loc,found_count)
            found_count += 1
            print(">>>>> Bravo !")
            ofp = open("solutions.data",'a')
            ofp.write("%s\n"%str(global_piece_loc))
            ofp.close()
            return False
        else:
            return False

    name = piece_list[current_index]
    current_piece = all_pieces[name]
    if name == 'h':
        tmp_all_loc = generate_logic_all_loc( current_piece, board=current_board, all_loc = piece_locs[name])
        current_all_loc = list()
        for loc in tmp_all_loc:
            if loc[2] < 4 :
                if loc[0] == 0 and loc[1] == 0:
                    current_all_loc.append(loc)
                if loc[0] == 0 and loc[1] == 1:
                    current_all_loc.append(loc)
                if loc[0] == 1 and loc[1] == 1:
                    current_all_loc.append(loc)
    else:
        current_all_loc = generate_logic_all_loc( current_piece, board=current_board, all_loc = piece_locs[name])

    for current_loc in current_all_loc:
        # print(">>>>> Placing %s ."%name)
        global_piece_loc[name] = current_loc
        place_piece( current_board, current_piece, current_loc )
        result = place_next( current_board, current_index+1 )
        if result:
            ids = derive_piece_line_ids(current_piece,current_loc)
            print(">>>>> Current piece: %s, loc: %s"%(name,ids))
            return True
        global_piece_loc[name] = None
        remove_piece( current_board, current_piece,current_loc )
    return False

blank_board = { 'h':list(),'v':list() }
place_next(blank_board,0 )

# piece_loc = { 
#     "h" :(0, 0, 0),
#     "x" :(0, 2, 0),
#     "w" :(0, 1, 0),
#     "u" :(0, 3, 6),
#     "s" :(3, 0, 5),
#     "l" :(2, 3, 2),
#     "j" :(3, 1, 5),
#     "n" :(3, 3, 2),
#     "t" :(2, 0, 1),
#     "y" :(1, 2, 3),
#     }
# # 
# print(check_solution( piece_loc ))
# make_graphic( piece_loc, 1 )
