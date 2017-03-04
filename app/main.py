import bottle
import os
import random

board_width = 0
board_height = 0
turn = 0
our_snake = "UUID"
snakes = []
food = []
snakeLocs = []
# prevSnakeLocs = []
snakeHeads = []
prevSnakeHeads = []
failureValue = -1


#------------------#
#--- MAIN LOGIC ---#
#------------------#
class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.G = 100000
        self.H = 0
        self.value = self.setValue()
    
    # This function gives weights to different types of nodes.
    # Note that the function calling this will never call it on a "wall" or a "snake", but
    # in any case we keep their weights here just in case.
    # Not sure if head/snake neighbors should be weighted differently - 
    def moveCost(self, other):
        if self.value == "wall":
            return 1000
        elif self.value == "snake":
            return 10
	elif self.value == "head":
	    return 10
        elif self.value == "food":
            return -2
        elif self.value == "nexttohead":
            return 4
        elif self.value == "nexttosnake":
            return 2
        elif self.value == "empty":
            return 2
        else:
            print "Something went wrong - node.value of {} does not have a moveCost".format(str(self))
            return 2
    
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
    
    def getRelative(self, dx, dy):
        new = self
        new.x += dx
        new.y += dy
        return new
    # Returns true iff there is a path from self to other without going backwards    
    def lineOfSight(self, other):
        cpy = Node(self.x,self.y)
        dx = other.x - self.next
        dy = other.y - self.y
        x = 1
        y = 1
        if dx < 0:
            x = -1
        if dy < 0L
            y = -1
        while not cpy == other and not any(Node(cpy.x+x, cpy.y) == n or Node(cpy.x, cpy.y+y) == n for n in children(cpy))
            if not any(Node(cpy.x+x, cpy.y)==n for n in children(cpy)):
                cpy = Node(cpy.x+x, cpy.y)
            else:
                cpy = Node(cpy.x, cpy.y+y)
        if cpy == other:
            return True;
        else:
            return False;

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

def initGoalList(head):
    #TODO: figure this out.
    # Start with food.
    goalList = []
    for f in food:
        # Ignore food we aren't closest to.
        if any(f.distance(h) < f.distance(head) for h in snakeHeads):
            continue
        else:
            goalList.append(f)
    # Prioritize food near the center. (This way we stay away from walls)
    center = Node(board_width/2, board_height/2)
    goalList.sort(key=lambda f:f.distance(center))
    # Then aim for our tail.
    for s in snakes:
        if s['id']==our_snake:
            tail = Node(s['coords'][-1][0],s['coords'][-1][1])
            goalList.append(tail)
    # Then aim for the center.
    goalList.append(center)
    # Then aim for the a not-next-to-a-snake-head spot (Djikstra? One at a time?).
    # NOT DONE. Will only run the algorithm searching for the best spot if all others don't work.
    # (i.e. if goalNum >= len(goalList))
    return goalList

def getFarthestSpot(head):
    openSet = set()
    closedSet = set()
    current = head
    
    # Loops through all possible paths and finds the longest one.
    while openSet:
        current = min(openSet, key=lambda o:o.G)
        
        openSet.remove(current)
        closedSet.add(current)
        
        for node in children(current):
            if node in closedSet:
                continue
            
            if node in openSet:
                continue

            else:
                node.G = current.G + node.distance(current)
                node.parent = current
                openSet.add(node)
                
    if current == goalNode:
        path = []
        while current.parent:
            path.append(current)
            current = current.parent
        path.append(current)
        return path[::-1]

def chooseGoalNode(goalList, goalNum):
    if goalNum < len(goalList):
        goal = goalList[goalNum]
    else:
        # TODO: find best possible location if all others are unavailable (can't get to food, tail, center)
        goal = getFarthestSpot(head)
    return goal

def moveToGoalNode(head, goalNode):
    astar = AStar(head, goalNode)
    # AStar may return failureValue to indicate it can't find a path. If so, return failureValue
    # so that we can try again, with a new goal node.
    if (astar != failureValue):
        return astar[1]
    else:
        return failureValue

def getSnakeDirs():
    dirs = []
    direction = 0
    for i in range(1, len(dirs)):
        dirs.append(snakeHeads[i] - prevSnakeHeads[i])
    return dirs

# Returns an int between 0 and 3, inclusive, corresponding to indices of ['up','down','left','right']
def choose(head):
    nextMove = failureValue
    goalList = initGoalList(head)
    goalNum = 0
    while nextMove == failureValue:
        goalNode = chooseGoalNode(goalList, goalNum)
        goalNum += 1
        print("Goal node: ",str(goalNode))
        nextMove = moveToGoalNode(head, goalNode)
        print("Next move: ",str(nextMove))
    return nextMove - head
    

#------------------------#
#--- DEALING WITH I/O ---#
#------------------------#

# Used to find image to return for our head.
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
    prevSnakeHeads = []
    
    # TODO: Do things with data
    # TODO: Do something fun to choose color.
    # TODO: Get a good head image
    # TODO: Choose a good name
    
    return {
        'color': 'gold',
        'taunt': '!!!',
        'head_type': 'tongue',
        'tail_type': 'skinny_tail',
        'name': 'jalfje-battlepython'
    }

# Handle move requests.
@bottle.post('/move')
def move():
    data = bottle.request.json
    game_id = data['game_id']       # This should stay constant after /start call [UUID]
    global board_width,board_height,our_snake,turn,food,snakes,snakeLocs,snakeHeads
    our_snake = data['you']         # This should stay constant after first /move call [UUID]
    board_width = data['width']     # This should stay constant after /start call [int]
    board_height = data['height']   # This should stay constant after /start call [int]
    turn = data['turn']             # Current game turn, should increment by 1 each time. [int]
    foodlist = data['food']         
    snakes = data['snakes']         # First list in each snake's 'coords' is the head
    
    # TODO: If something hasn't been updated, don't create a new node. (To save computation time)
    # TODO: Make one big representation of the whole board so lookups are faster.
    
    for f in foodlist:
        food.append(Node(f[0],f[1]))
    
    for s in snakes:
        # Don't add our snake's head to the list of snakeHeads, add all other heads
        if not s['id'] == our_snake:
            snakeHeads.append(Node(s['coords'][0][0],s['coords'][0][1]))
        # Add all (including our own, and all heads) snake bodies to 
        for c in s['coords']:
            snakeLocs.append(Node(c[0],c[1]))
        
    # Print statements purely for testing
    #print(data)
    print(our_snake)
    print(str(food))
    print(snakes['id'==our_snake]['taunt'])
    print "snake locations: [%s]" % ", ".join(map(str, snakeLocs))
    
    head = Node(snakes['id'==our_snake]['coords'][0][0], snakes['id'==our_snake]['coords'][0][1])
    direction = choose(head)
    directions = ['up', 'down', 'left', 'right']
    
    prevSnakeHeads = snakeHeads
    #TODO: Make 'taunt' do something fun, like take a random word combo from a dictionary ala gfycat
    return {
        'move': directions[direction],
        'taunt': taunts[random.next]
    }

# Jamie: No idea what this comment means or how the function works, but it's best not to break it.
# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
