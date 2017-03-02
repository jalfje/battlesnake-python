import bottle
import os
import random

board_width = 0
board_height = 0
turn = 0
snakes = []
food = []
snakeLocs = []
snakeHeads = []
failureValue = -1


#------------------#
#--- MAIN LOGIC ---#
#------------------#
class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.G = 0
        self.H = 0
        self.value = self.setValue()

    def moveCost(self, other):
        if self.value == "wall":
            return 1000
        elif self.value == "snake":
            return 10
        elif self.value == "food":
            return -2
        elif self.value == "nexttohead":
            return 4
        elif self.value == "nexttosnake":
            return 2
        elif self.value == "empty":
            return 1
        else:
            print "Something went wrong - node.value of {} is not valid".format(str(self))
            return 1
    
    def setValue(self):
        if (self.x < 0 or self.y < 0 or self.x >= board_width or self.y >= board_height):
            return "wall"
        elif any(self == h for h in snakeHeads):
            return "head"
        elif any(self == s for s in snakeLocs):
            return "snake"
        elif any(self == f for f in food):
            return "food"
        else:
            # If this node is next to a snake head
            for h in snakeHeads:
                neighbors = [(h.x-1,h.y),(h.x+1,h.y),(h.x,h.y-1),(h.x,h.y+1)]
                if any(self.x == p[0] and self.y == p[1] for p in neighbors):
                    return "nexttohead"
            # If this node is next to a snake body segment
            for s in snakeLocs:
                neighbors = [(s.x-1,s.y),(s.x+1,s.y),(s.x,s.y-1),(s.x,s.y+1)]
                if any(self.x == p[0] and self.y == p[1] for p in neighbors):
                    return "nexttosnake"
        # In all other cases, return empty
        return "empty"
    
    # Returns the distance between itself and another Node - "Manhattan" distance
    # Uses x distance + y distance, not actual (diagonal) distance, because snakes only move N/S/E/W   
    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)
        
    # Finding direction to go to get to self from other - up,down,left,right correspond to 0,1,2,3
    # Works like final - initial with vectors - e.g. (1,0) - (0,0) = 3 -> move right
    def __sub__(self, other):
        # if other is to the left of self, the displacement is to the right. others are similar.
        if self.x - other.x == 1:
            return 3
        if self.x - other.x == -1:
            return 2
        if self.y - other.y == 1:
            return 1
        if self.y - other.y == -1:
            return 0
        else:
            return NotImplemented
    def __str__(self):
        return "({},{}):{}".format(self.x,self.y,self.value)
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y
    # Hash function required due to overloaded == operator, and Node's use within sets.
    # This hash function guarantees no collisions with non-equal Nodes. x * height > y for all x,y.
    def __hash__(self):
        return self.x * board_height + self.y

def children(node):
    x,y = node.x,node.y
    children = []
    nodes = [Node(x-1,y), Node(x+1,y), Node(x,y-1), Node(x,y+1)]
    for n in nodes:
        if n.value != "wall" and n.value != "snake":
            children.append(n)
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
                node.H = node.distance(goalNode)
                node.parent = current
                openSet.add(node)
    #TODO: Handle no path found (i.e. the goal is blocked off. Should try to find another node.)
    print("Path not found. Uh oh.")
    return failureValue

def chooseGoalNode(head):
    #TODO: Fix this up to actually decide where it's best to go to.
    #TODO: Determine what order to search for things, in case of multiple calls
    #goal = bestFood() else goal = center()
    goal = Node(random.randint(0,board_width-1), random.randint(0,board_height-1))
    goal = food[0]
    return goal
    
def moveToGoalNode(head, goalNode):
    astar = AStar(head, goalNode)
    # AStar may return a failureValue to indicate it can't find a path. If so, return failureValue
    # so that we can try again, with a new goal node.
    if (astar != failureValue):
        return astar[1]
    else:
        return failureValue

# Returns an int between 0 and 3, inclusive
def choose(head):
    nextMove = failureValue
    while nextMove == failureValue:
        goalNode = chooseGoalNode(head)
        print("Goal node: ",str(goalNode))
        nextMove = moveToGoalNode(head, goalNode)
        print("Next move: ",str(nextMove))
    return nextMove - head
    

#------------------------#
#--- DEALING WITH I/O ---#
#------------------------#
@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

# Handle start requests.
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
    # TODO: Do something fun to choose color.
    # TODO: Get a good head image
    # TODO: Choose a good name
    
    return {
        'color': '#FFFFFF',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'jalfje-battlepython'
    }

# Handle move requests.
@bottle.post('/move')
def move():
    data = bottle.request.json
    game_id = data['game_id']       # This should stay constant after /start call [UUID]
    our_snake = data['you']         # This should stay constant after /start call [UUID]
    global board_width,board_height,turn,food,snakes,snakeLocs,snakeHeads
    board_width = data['width']     # This should stay constant after /start call [int]
    board_height = data['height']   # This should stay constant after /start call [int]
    turn = data['turn']             # Current game turn, should increment by 1 each time. [int]
    foodlist = data['food']         
    snakes = data['snakes']         # First list in each snake's 'coords' is the head
    
    for f in foodlist:
        food.append(Node(f[0],f[1]))
    
    for s in snakes:
        # Don't add our snake's head to the list of snakeHeads, but add all snakes to snakeLocs
        if not s['id'] == our_snake:
            snakeHeads.append(Node(s['coords'][0][0],s['coords'][0][1]))
        for c in s['coords']:
            snakeLocs.append(Node(c[0],c[1]))
        
    
    #print(data)
    print(our_snake)
    print(str(food))
    print(snakes['id'==our_snake]['taunt'])
    print "snake locations: [%s]" % ", ".join(map(str, snakeLocs))
    
    head = Node(snakes['id'==our_snake]['coords'][0][0], snakes['id'==our_snake]['coords'][0][1])
    direction = choose(head)
    directions = ['up', 'down', 'left', 'right']
    
    #TODO: Make 'taunt' do something fun, like take a random word combo from a dictionary ala gfycat
    return {
        'move': directions[direction],
        'taunt': 'battlesnake-python?'
    }

# Jamie: No idea what this comment means or how the function works, but it's best not to break it.
# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
