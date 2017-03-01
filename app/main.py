import bottle
import os
import random

board_width = 0
board_height = 0
turn = 0
snakes = []
food = []
snakeLocs = []

"""
------------------
--- MAIN LOGIC ---
------------------
"""
class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    # Returns the distance between itself and another point
    # Uses x distance + y distance, not actual (diagonal) distance, because snakes only move N/S/E/W   
    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)
    # Finding direction to go to get to self from other - up,down,left,right correspond to 0,1,2,3
    # Works like final - initial with vectors - e.g. (1,0) - (0,0) = 3 -> move right
    def __sub__(self, other):
        # if other is to the left of self, the displacement is to the right
        if self.x - other.x == 1:
            return 3
        # if other is to the right of self, the displacement is to the left 
        if self.x - other.x == -1:
            return 2
        # down is positive y, up is negative y.
        if self.y - other.y == 1:
            return 1
        if self.y - other.y == -1:
            return 0
        else:
            return NotImplemented
    def __str__(self):
        return "({},{})".format(self.x,self.y)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __hash__(self):
        return self.x * board_height + self.y
        
class Node:
    def __init__(self, point, value):
        self.value = value
        self.point = point
        self.parent = None
        self.G = 0
        self.H = 0

    def moveCost(self, other):
        if self.value == '%':
            return 1
        elif self.value == '!':
            return -1
        else:
            return 0

    def heuristic(self, other):
        return self.point.distance(other.point)
    
    def __sub__(self, other):
        return self.point - other.point
    def __str__(self):
        return "{}:{}".format(self.point,self.value)
    def __eq__(self, other):
        return self.point == other.point
    def __hash__(self):
        return self.point.x * board_height + self.point.y

def valueOf(point):
    value = '.'
    if (point.x < 0 or point.y < 0 or point.x >= board_width or point.y >= board_height):
        value = '%'
    elif any(point == s for s in snakeLocs):
        value = '%'
    elif any(point == f for f in food):
        value = '!'
    return value
        

def children(node):
    x,y = node.point.x,node.point.y
    children = []
    points = [Point(x-1, y), Point(x+1, y), Point(x, y-1), Point(x, y+1)]
    for p in points:
        if valueOf(p) != '%':
            children.append(Node(p, valueOf(p)))
    return children

def AStar(head, goalNode):
    openSet = set()
    closedSet = set()
    current = head
    openSet.add(head)
    while openSet:
        current = min(openSet, key=lambda o:o.G + o.H)
        
        if current == goalNode:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(current)
            return path[::-1]
        
        openSet.remove(current)
        closedSet.add(current)
        
        for node in children(current):
            if node in closedSet:
                continue
            
            if node in openSet:
                newG = current.G + current.moveCost(node)
                if node.G > newG:
                    node.G = newG
                    node.parent = current
            else:
                node.G = current.G + current.moveCost(node)
                node.H = node.heuristic(goalNode)
                node.parent = current
                openSet.add(node)
    
    print("Path not found. Uh oh.")
  
def chooseGoalNode(head):
    #TODO: Fix this up to actually decide where it's best to go to.
    rand = Node(Point(random.randint(0,board_width-1), random.randint(0,board_height-1)), '!')
    rand = Node(food[0], '!')
    return rand
    
def moveToGoalNode(head, goalNode):
    bestMoves = AStar(head, goalNode)
    return bestMoves[1]

# Returns an int between 0 and 3, inclusive
def choose(head):
    goalNode = chooseGoalNode(head)
    print("Goal node: ",str(goalNode))
    nextMove = moveToGoalNode(head, goalNode)
    print("Next move: ",str(nextMove))
    return nextMove - head
    
"""
------------------------
--- DEALING WITH I/O ---
------------------------
"""
@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    global board_width,board_height
    board_width = data['width']
    board_height = data['height']
    
    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#FFFFFF',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'battlesnake-python'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    game_id = data['game_id']
    our_snake = data['you']     # UUID to be searched for in snakes[]
    global board_width,board_height,turn,food,snakes,snakeLocs
    board_width = data['width']
    board_height = data['height']
    turn = data['turn'] # current game turn
    foodlist = data['food']
    snakes = data['snakes']
    
    for f in foodlist:
        food.append(Point(f[0],f[1]))
    
    for s in snakes:
        for c in s['coords']:
            snakeLocs.append(Point(c[0],c[1]))
        
    #print(data)
    print(our_snake)
    print(str(food))
    print(snakes['id'==our_snake]['taunt'])
    print "snake locations: [%s]" % ", ".join(map(str, snakeLocs))
    
    headp = Point(snakes['id'==our_snake]['coords'][0][0], snakes['id'==our_snake]['coords'][0][1])
    head = Node(headp, '%')
    direction = choose(head)
    directions = ['up', 'down', 'left', 'right']

    return {
        'move': directions[direction],
        'taunt': 'battlesnake-python?'
    }

# Jamie: No idea what this comment means or how the function works, but it's best not to break it.
# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
