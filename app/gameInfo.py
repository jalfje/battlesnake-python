class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.G = 100000
        self.H = 0

    def extrapolate(self, direction, distance):
        if direction == 0:
            return Node(self.x, self.y-distance)
        elif direction == 1:
            return Node(self.x, self.y+distance)
        elif direction == 2:
            return Node(self.x-distance, self.y)
        elif direction == 3:
            return Node(self.x+distance, self.y)
        else:
            return NotImplemented
    
    # Returns the distance between itself and another Node - "Manhattan" distance
    # Uses x distance + y distance, not actual (diagonal) distance, because snakes only move N/S/E/W   
    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)
        
    # Finding direction to go to get to self from other - up,down,left,right correspond to 0,1,2,3
    # Works like final - initial with vectors - e.g. (1,0) - (0,0) = 3 -> move right
    def __sub__(self, other):
        # if other is above self, the displacement is to the right. others are similar.
        if self.y - other.y == -1:
            return 0
        if self.y - other.y == 1:
            return 1
        if self.x - other.x == -1:
            return 2
        if self.x - other.x == 1:
            return 3
        else:
            return NotImplemented
    def __str__(self):
        return "({},{})".format(self.x,self.y)
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y
    # Hash function required due to overloaded == operator, and Node's use within sets.
    # This hash function guarantees no collisions with non-equal Nodes. x * 300 > y for all x,y.
    # UNLESS the board height is greater than 300, which it really won't be.
    def __hash__(self):
        return self.x * 300 + self.y

class GameInfo(object):
    def __init__(self, data, initial_taunt):
        self.ID = data['game_id']           # This should stay constant after /start call [UUID]
        self.board_width = data['width']    # This should stay constant after /start call [int]
        self.board_height = data['height']  # This should stay constant after /start call [int]
        self.taunt = initial_taunt
        self.food = []
        self.snakes = []
        self.snake_locs = []
        self.snake_heads = []
        self.prev_food = []
        self.prev_snakes = []
        self.prev_snake_locs = []
        self.prev_snake_heads = []
    
    def update(self, data):
        self.prev_snakes = self.snakes
        self.turn = data['turn']             # Current game turn, should increment by 1 each time. [int]
        self.our_id = data['you']         # This should stay constant after first /move call [UUID]
        # print "Our snake UUID = {}".format(str(self.our_id))
        self.food_list = data['food']         
        self.prev_food = self.food
        self.prev_snake_locs = self.snake_locs
        self.prev_snake_heads = self.snake_heads
        self.food = []
        self.snakes = data['snakes']         # First list in each snake's 'coords' is the head
        self.snake_locs = []
        self.snake_heads = []
        
        for s in self.snakes:
            if s['id'] == self.our_id:
                self.our_snake = s
        
        for f in self.food_list:
            self.food.append(Node(f[0],f[1]))
        
        for s in self.snakes:
            # Don't add our snake's head to the list of snakeHeads
            # Also don't add the heads of any shorter snakes, because we can kill them anyway.
            if not s == self.our_snake and len(s['coords']) > len(self.our_snake['coords']):
                self.snake_heads.append(Node(s['coords'][0][0],s['coords'][0][1]))
            # Add all (including our own, and all heads) snake bodies to 
            for c in s['coords']:
                self.snake_locs.append(Node(c[0],c[1]))
        
        #self.prev_food = food
        #self.prev_snake_locs = snake_locs
        #self.prev_snake_heads = snake_heads

    # This function gives weights to different types of nodes.
    # Note that the function calling this will never call it on a "wall" or a "snake", but
    # in any case we keep their weights here just in case.
    # Not sure if head/snake neighbors should be weighted differently - 
    def moveCost(self, node):
        if node.value == "wall":
            return 1000
        elif node.value == "snake":
            return 10
        elif node.value == "head":
            return 10
        elif node.value == "food":
            return -2
        elif node.value == "nexttohead":
            return 4
        elif node.value == "nexttosnake":
            return 2
        elif node.value == "empty":
            return 2
        else:
            print "Something went wrong - node.value of {} does not have a moveCost".format(str(node))
            try:
                print "Node {} has node.value = {}".format(str(node), node.value)
            except AttributeError:
                print "Node {} does not have node.value!".format(str(node))
            return 2
    
    def getValue(self, node):
        try:
            return node.value
        except AttributeError:
            #print "Caught an attribute error on node {}".format(str(node))
            if (node.x < 0 or node.y < 0 or node.x >= self.board_width or node.y >= self.board_height):
                node.value = "wall"
            elif any(node == h for h in self.snake_heads):
                node.value = "head"
            elif any(node == s for s in self.snake_locs):
                node.value = "snake"
            elif any(node == f for f in self.food):
                node.value = "food"
            else:
                # If this node is next to a snake head
                for h in self.snake_heads:
                    neighbors = [(h.x-1,h.y),(h.x+1,h.y),(h.x,h.y-1),(h.x,h.y+1)]
                    if any(node.x == p[0] and node.y == p[1] for p in neighbors):
                        node.value = "nexttohead"
                        break
                # If this node is next to a snake body segment
                for s in self.snake_locs:
                    neighbors = [(s.x-1,s.y),(s.x+1,s.y),(s.x,s.y-1),(s.x,s.y+1)]
                    if any(node.x == p[0] and node.y == p[1] for p in neighbors):
                        node.value = "nexttosnake"
                        break
        try:
            return node.value
        except AttributeError:
            # In all other cases, return empty
            #print "game.getValue({}) had no value and catching the exception didn't fix it.".format(str(node))
            node.value = "empty"
            return node.value

    def children(self, node):
        x,y = node.x,node.y
        children = []
        nodes = [Node(x-1,y), Node(x+1,y), Node(x,y-1), Node(x,y+1)]
        for n in nodes:
            if not self.getValue(n) == "wall" and not self.getValue(n) == "snake":
                # print "{}, {}".format(n,game.getValue(n))
                children.append(n)
        return children

    # Returns true iff there is a path from node to other without going backwards    
    def lineOfSight(self, node, other):
        tmp = Node(node.x,node.y)
        dx = other.x - node.next
        dy = other.y - node.y
        x = 1
        y = 1
        if dx < 0:
            x = -1
        if dy < 0:
            y = -1
        children = self.children(cpy)
        while not tmp == other and not any(Node(tmp.x+x, tmp.y) == n or Node(tmp.x, tmp.y+y) == n for n in children):
            if not any(Node(tmp.x+x, tmp.y)==n for n in children):
                tmp = Node(tmp.x+x, tmp.y)
            else:
                tmp = Node(tmp.x, tmp.y+y)
        if tmp == other:
            return True;
        else:
            return False;
    
    def center(self):
        return Node(self.board_width/2, self.board_height/2)
