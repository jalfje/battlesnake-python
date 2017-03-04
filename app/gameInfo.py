class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.G = 100000
        self.H = 0
    
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
    def __init__(self, data):
        self.ID = data['game_id']           # This should stay constant after /start call [UUID]
        self.board_width = data['width']    # This should stay constant after /start call [int]
        self.board_height = data['height']  # This should stay constant after /start call [int]
    
    def update(self, data):
        self.turn = data['turn']             # Current game turn, should increment by 1 each time. [int]
        self.our_snake = data['you']         # This should stay constant after first /move call [UUID]
        self.food_list = data['food']         
        self.snakes = data['snakes']         # First list in each snake's 'coords' is the head
        self.food = []
        self.snake_locs = []
        self.snake_heads = []
        
        for f in self.food_list:
            self.food.append(Node(f[0],f[1]))
        
        for s in self.snakes:
            # Don't add our snake's head to the list of snakeHeads, add all other heads
            if not s['id'] == self.our_snake:
                self.snake_heads.append(Node(s['coords'][0][0],s['coords'][0][1]))
            # Add all (including our own, and all heads) snake bodies to 
            for c in s['coords']:
                self.snake_locs.append(Node(c[0],c[1]))

    # This function gives weights to different types of nodes.
    # Note that the function calling this will never call it on a "wall" or a "snake", but
    # in any case we keep their weights here just in case.
    # Not sure if head/snake neighbors should be weighted differently - 
    def moveCost(self, node):
        if node.value == "wall":
            return 1000
        elif node.value == "snake":
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
            return 2
    
    def getValue(self, node):
        try:
            return node.value
        except AttributeError:
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
            node.value = "empty"
            return node.value

    def children(self, node):
        x,y = node.x,node.y
        children = []
        nodes = [Node(x-1,y), Node(x+1,y), Node(x,y-1), Node(x,y+1)]
        for n in nodes:
            if self.getValue(n) != "wall" and self.getValue(n) != "snake":
                # print "{}, {}".format(n,game.getValue(n))
                children.append(n)
        return children
    
    # Returns true iff there is a path from self to other without going backwards    
    def lineOfSight(self, node, other):
        cpy = Node(self.x,self.y)
        dx = other.x - self.next
        dy = other.y - self.y
        x = 1
        y = 1
        if dx < 0:
            x = -1
        if dy < 0:
            y = -1
        children = self.children(cpy)
        while not cpy == other and not any(Node(cpy.x+x, cpy.y) == n or Node(cpy.x, cpy.y+y) == n for n in children):
            if not any(Node(cpy.x+x, cpy.y)==n for n in children):
                cpy = Node(cpy.x+x, cpy.y)
            else:
                cpy = Node(cpy.x, cpy.y+y)
        if cpy == other:
            return True;
        else:
            return False;
    
    def center(self):
        return Node(self.board_width/2, self.board_height/2)
    
    
