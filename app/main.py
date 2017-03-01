import bottle
import os
import random

board_width = 0
board_height = 0
turn = 0
snakes = []
food = []

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
    def distance(self, point):
        return abs(self.x - point.x) + abs(self.y - point.y)
        
class Node:
    def __init__(self, point, value):
        self.value = value
        self.point = point
        self.parent = None
        self.G = 0
        self.H = 0

    def moveCost(self, other):
        if value == '%':
            return 1
        elif value == '!':
            return -1
        else:
            return 0
    
    def heuristic(self, other):
        return distance(self.point, other.point)

def getNextClosestFood(foodList):
    closestFood = foodList[0]
    return closestFood

def valueOf(point):
    if (point.x < 0 or point.y < 0 or point.x >= board_width or point.y >= board_height):
        value = '%'
    elif any(point in s for s in snakes):
        value = '%'
    elif (point in f):
        value = '!'
    else:
        value = '.'
        

def children(node):
    x,y = node.point.x,node.point.y
    children = []
    points = [Point(x-1, y), Point(x+1, y), Point(x, y-1), Point(x, y+1)]
    for p in points:
        if valueOf(p) != '%':
            children.add(Node(p, valueOf(p)))
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
                node.H = distance(node.point, goalNode)
                node.parent = current
                openset.add(node)
    
    print("Path not found. Uh oh.")
                
        
        
def chooseGoalNode(head):
    return head
    
def moveToGoalNode(head, goalNode):
    bestMoves = AStar(head, goalNode)
    return bestMoves[0]

# Returns an int between 0 and 3, inclusive
def choose(head):
    goalNode = chooseGoalNode(head)
    nextMove = moveToGoalNode(head, goalNode)
    return random.randint(0,3)
    
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
    global board_width,board_height,turn,food,snakes
    board_width = data['width']
    board_height = data['height']
    turn = data['turn'] # current game turn
    food = data['food']
    snakes = data['snakes']
    
    #print(data)
    print(our_snake)
    print(food)
    print(snakes['id'==our_snake]['taunt'])
    
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
