import bottle
import os
import random

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

def getNextClosestFood(foodList):
    closestFood = foodList[0]
    return closestFood

# Returns an int between 0 and 3, inclusive
def choose():
    return random.randint(0,3)
    
def moveToGoalPoint(goalPoint):
    return


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
    board_width = data['width']
    board_height = data['height']
    turn = data['turn'] # current game turn
    food = data['food']
    snakes = data['snakes']
    
    #print(data)
    print(our_snake)
    #print(food)
    print(snakes['id'==our_snake]['taunt'])
    
    direction = choose()
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
