import bottle
import os
import random
# import antigravity
from gameInfo import GameInfo
from gameInfo import Node

games = {}
failureValue = -1


#------------------#
#--- MAIN LOGIC ---#
#------------------#

def AStar(game, head, goalNode):
    print "Call to AStar with head = {} and goalNode = {}".format(str(head),str(goalNode))
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
        
        for node in game.children(current):
            if node in closedSet:
                continue
            
            if node in openSet:
                newG = current.G + game.moveCost(node)
                if node.G > newG:
                    node.G = newG
                    node.parent = current
            else:
                node.G = current.G + game.moveCost(node)
                node.H = node.distance(goalNode)
                node.parent = current
                openSet.add(node)
    print "Path not found from {} to {}. Uh oh.".format(str(head),str(goalNode))
    return failureValue

def initGoalList(game, head):
    # Start with food.
    goalList = []
    foodList = []
    for f in game.food:
        # Ignore food we aren't closest to.
        if any(f.distance(h) < f.distance(head) for h in game.snake_heads):
            continue
        else:
            foodList.append(f)
    
    # Prioritize food nearest to us.
    foodList.sort(key=lambda f:f.distance(head))
    center = game.center()
    
    # Decide where our tail is and how long we are
    snek = game.our_snake
    length = len(snek['coords'])
    health = snek['health_points']
    tail = Node(snek['coords'][-1][0],snek['coords'][-1][1])

    # Priority system: If length < 10 or health < 50, go for food. Otherwise, try to survive.
    if length < 10 or health < 50:
        for f in foodList:
            goalList.append(f)
        goalList.append(tail)
        goalList.append(center)
    else:
        goalList.append(tail)
        goalList.append(center)
        for f in foodList:
            goalList.append(f)
    print "Goallist: ",
    for f in goalList:
        print f,
    print ""
    return goalList

# Finds the farthest spot from the location, and goes in that direciton.
def getFarthestSpot(game, head):
    openSet = set()
    closedSet = set()
    current = head
    
    # Loops through all possible paths and finds the longest one.
    while openSet:
        current = min(openSet, key=lambda n:n.G)
        
        openSet.remove(current)
        closedSet.add(current)
        
        for node in game.children(current):
            if node in closedSet:
                continue
            if node in openSet:
                continue
            else:
                node.G = current.G + 1
                node.parent = current
                openSet.add(node)
    if closedSet:
        return max(closedSet, key=lambda n:n.G)
    else:
        return min(game.children(head), key=lambda game,node:game.getValue(node))

def getGoalNode(game, head, goalList, goalNum):
    if goalNum < len(goalList):
        goal = goalList[goalNum]
    else:
        # TODO: find best possible location if all others are unavailable (can't get to food, tail, center)
        goal = getFarthestSpot(game, head)
    return goal

def moveToGoalNode(game, head, goalNode):
    astar = AStar(game, head, goalNode)
    # AStar may return failureValue to indicate it can't find a path. If so, return failureValue
    # so that we can try again, with a new goal node.
    if (astar != failureValue):
        return astar[1]
    else:
        return failureValue

# Returns an int between 0 and 3, inclusive, corresponding to indices of ['up','down','left','right']
def choose(game, head):
    nextMove = failureValue
    goalList = initGoalList(game, head)
    goalNum = 0
    while nextMove == failureValue:
        goalNode = getGoalNode(game, head, goalList, goalNum)
        goalNum += 1
        print "Goal node: {}".format(str(goalNode))
        nextMove = moveToGoalNode(game, head, goalNode)
        print "Next move: {}".format(str(nextMove))
    nextSpot = head.extrapolate(nextMove - head, 1)
    if (AStar(game, nextSpot, goalNode)) == failureValue: # Warning: May impact memory usage
        pass
        # Code will go here as soon as I finish eating
    return nextMove - head
    

#------------------------#
#--- DEALING WITH I/O ---#
#------------------------#

# Used to find image to return for our head.
#@bottle.route('/static/<path:path>')
#def static(path):
#    return bottle.static_file(path, root='static/')

# Handle start requests.
@bottle.post('/start')
def start():
    global games
    data = bottle.request.json
    game_id = str(data['game_id'])
    game = GameInfo(data)
    games[game_id] = game
    
    # TODO: Do things with data
    # TODO: Do something fun to choose color.
    # TODO: Get a good head image
    # TODO: Choose a good name
    
    return {
        'color': '#ffd700',
        'taunt': 'I am snake!',
        'head_url': 'https://b.thumbs.redditmedia.com/NhLnTsOGywOxwh2FGgsV2l1bg0_bXKAL0AAtD3DPe7o.png',
        'name': 'SNEK.',
        'head_type': 'tongue',
    }

# Handle move requests.
@bottle.post('/move')
def move():
    global games
    data = bottle.request.json
    game_id = str(data['game_id'])
    game = games[game_id]
    game.update(data)
    snek = game.our_snake
    print "Data.you = {}. snek.id = {}.".format(data['you'],snek['id'])
    head = Node(snek['coords'][0][0], snek['coords'][0][1])
    print "Head: {}".format(str(head))
    direction = choose(game, head)
    directions = ['up', 'down', 'left', 'right']
    
    # Deal with taunts
    with open('taunts.txt') as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    
    return {
        'move': directions[direction],
        'taunt': content[random.randint(0, len(content)-1)]
    }

# Jamie: No idea what this comment means or how the function works, but it's best not to break it.
# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
