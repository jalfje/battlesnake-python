import bottle
import os
from gameInfo import GameInfo
from gameInfo import Node

games = {}
failureValue = -1


#------------------#
#--- MAIN LOGIC ---#
#------------------#

def AStar(game, head, goalNode):
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
    #TODO: Handle no path found (i.e. the goal is blocked off. Should try to find another node.)
    print("Path not found. Uh oh.")
    return failureValue

def initGoalList(game, head):
    #TODO: figure this out.
    # Start with food.
    goalList = []
    for f in game.food:
        # Ignore food we aren't closest to.
        if any(f.distance(h) < f.distance(head) for h in game.snake_heads):
            continue
        else:
            goalList.append(f)
    # Prioritize food near the center. (This way we stay away from walls)
    center = game.center()
    goalList.sort(key=lambda f:f.distance(center))
    # Then aim for our tail.
    for s in game.snakes:
        if s['id']==game.our_snake:
            tail = Node(s['coords'][-1][0],s['coords'][-1][1])
            goalList.append(tail)
    # Then aim for the center.
    goalList.append(center)
    # Then aim for the a not-next-to-a-snake-head spot (Djikstra? One at a time?).
    # NOT DONE. Will only run the algorithm searching for the best spot if all others don't work.
    # (i.e. if goalNum >= len(goalList))
    for f in goalList:
        print f,
    return goalList

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
    #TODO: Fix this lil bit up
    return max(openSet, key=lambda n:n.G)

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
        print("Goal node: ",str(goalNode))
        nextMove = moveToGoalNode(game, head, goalNode)
        print("Next move: ",str(nextMove))
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
    data = bottle.request.json
    game_id = data['game_id']
    game = GameInfo(data)
    games[game_id] = game
    
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
    game_id = data['game_id']
    game = games[game_id]
    game.update(data)
    
    head = Node(game.snakes['id'==game.our_snake]['coords'][0][0], game.snakes['id'==game.our_snake]['coords'][0][1])
    direction = choose(game, head)
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
